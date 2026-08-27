"""High-level Python client for a FoMo inference server.

FoMo is a time-series foundation-model inference server. ``Client``
builds a ``ForecastRequest``, runs the *wire* converters in
``fomo.types.converters``, and sends Arrow IPC through
``HttpTransport`` (``POST /forecast/bytes``). Mapping a coerced request
onto sktime ``(y, X, fh)`` is a different layer:
``fomo.runtime.executors.sktime.convertors``.

See Also
--------
fomo.client.transports.base.BaseTransport
    Abstract transport ``Client`` injects. Defaults to ``HttpTransport``.
fomo.types.models.ForecastRequest
    User-facing forecast fields.
fomo.types.converters
    ``coerce_request``, ``encode_request``, ``decode_response``,
    ``_from_narwhals``.
"""

from typing import Any, Self

from fomo.client.transports.base import BaseTransport
from fomo.client.transports.http import HttpTransport
from fomo.types import ForecastRequest, ForecastResponse, HealthResult, ModelsResult, StatsResult
from fomo.types.converters import (
    _from_narwhals,
    coerce_request,
    decode_response,
    encode_request,
)


class Client:
    """Call a FoMo inference server from Python.

    Parameters
    ----------
    url : str
        Server base URL. Used only when ``transport`` is omitted.
    timeout : float, default 60.0
        Request timeout in seconds for a newly constructed
        ``HttpTransport``.
    transport : BaseTransport or None, default None
        Optional prebuilt transport. When omitted, constructs
        ``HttpTransport(url, timeout=timeout)``.

    Notes
    -----
    Only ``HttpTransport`` exists today. Inject another
    ``BaseTransport`` subclass to swap the wire.

    See Also
    --------
    fomo.client.transports.base.BaseTransport
        Abstract transport type.
    fomo.client.transports.http.HttpTransport
        Default transport.
    fomo.types.models.ForecastRequest
        User-facing forecast fields.
    fomo.types.converters
        Wire converters used by ``forecast``.
    """

    def __init__(
        self,
        url: str,
        *,
        timeout: float = 60.0,
        transport: BaseTransport | None = None,
    ) -> None:
        """Construct a client. See ``Client`` for parameters."""
        self._transport = transport or HttpTransport(url, timeout=timeout)

    def forecast(
        self,
        *,
        history: Any,
        time: str,
        target: list[str],
        horizon: int,
        context: int,
        model: str = "naive",
        future: Any = None,
        static: Any = None,
        series_id: list[str] | None = None,
        known_future: list[str] | None = None,
        freq: str | None = None,
        quantiles: list[float] | None = None,
        params: dict[str, Any] | None = None,
    ) -> ForecastResponse:
        """Send a forecast over the bytes path and restore native frames.

        Builds a ``ForecastRequest``, then runs
        ``coerce_request`` → ``encode_request`` (JSON metadata + Arrow
        IPC files) → ``HttpTransport.forecast`` (``POST /forecast/bytes``
        multipart) → ``unpack_envelope`` → ``decode_response`` →
        ``_from_narwhals(template=history)`` so returned frames match
        the caller's native type.

        This method always uses the bytes path. It does not POST JSON
        to ``/forecast``.

        Parameters
        ----------
        history : any
            Past observations. Native type is the template for returned
            frames. See ``ForecastRequest`` for accepted shapes.
        time : str
            Time-index column name.
        target : list of str
            Target column names.
        horizon : int
            Forecast steps ahead.
        context : int
            Required look-back length. Unused by current executors.
        model : str, default ``"naive"``
            Loaded model id, not an executor name.
        future : any, optional
            Future rows for known covariates.
        static : any, optional
            Per-series static features.
        series_id : list of str, optional
            Panel key columns. Not supported yet; the server rejects
            them (HTTP 400 → ``RuntimeError``).
        known_future : list of str, optional
            Exogenous column names present in history and future.
        freq : str, optional
            Unused by current executors.
        quantiles : list of float, optional
            Quantile alphas when the executor supports them.
        params : dict, optional
            Unused by current executors.

        Returns
        -------
        ForecastResponse
            ``predictions`` and optional ``quantiles`` restored to the
            native type of ``history``.

        Raises
        ------
        ValidationError
            If ``ForecastRequest`` construction or ``coerce_request``
            fails (shape, columns, field constraints). Inner
            validators raise ``ValueError``, which Pydantic wraps.
        RuntimeError
            If the transport receives HTTP status >= 400, including
            panel rejection on the server. There is no custom FoMo
            exception class; ``HealthError`` is a Pydantic model, not
            raised here.
        httpx.RequestError
            If the HTTP client cannot connect or times out.
        ValueError
            If ``unpack_envelope`` rejects a truncated or invalid
            envelope (propagated from the transport).
        json.JSONDecodeError
            If the envelope ``response`` part is not valid JSON.

        See Also
        --------
        fomo.types.models.ForecastRequest
            Full field semantics for history/time/target/horizon/
            context/model/future/static/series_id/known_future/freq/
            quantiles/params.
        fomo.types.converters.coerce_request
            Wire conversion to ``CoercedForecastRequest``.
        fomo.types.converters.encode_request
            Split into JSON metadata and Arrow IPC files.
        fomo.client.transports.http.HttpTransport.forecast
            ``POST /forecast/bytes`` multipart.
        fomo.types.converters.decode_response
            Rebuild the coerced response from the unpacked envelope.
        """
        request = ForecastRequest(
            history=history,
            time=time,
            target=target,
            horizon=horizon,
            context=context,
            model=model,
            future=future,
            static=static,
            series_id=series_id,
            known_future=known_future,
            freq=freq,
            quantiles=quantiles,
            params=params,
        )
        coerced = coerce_request(request)

        # 1. encode request to json + bytes
        req_metadata, req_bytes_encoded = encode_request(coerced)
        # 2. send request to transport
        res_metadata, res_bytes_encoded = self._transport.forecast(req_metadata, req_bytes_encoded)
        # 3. decode response to json + bytes
        response = decode_response(res_metadata, res_bytes_encoded)

        predictions = _from_narwhals(response.predictions, history)
        quantile_table = (
            _from_narwhals(response.quantiles, history)
            if response.quantiles is not None
            else None
        )

        return ForecastResponse(
            predictions=predictions,
            model=response.model,
            request_id=response.request_id,
            quantiles=quantile_table,
        )

    def health(self) -> HealthResult:
        """Return server health. Delegates to the transport.

        Returns
        -------
        HealthResult
            Payload from ``GET /health``.

        Raises
        ------
        RuntimeError
            If the transport receives HTTP status >= 400.
        httpx.RequestError
            If the HTTP client cannot connect or times out.
        """
        return self._transport.health()

    def models(self) -> ModelsResult:
        """Return loaded models. Delegates to the transport.

        ``GET /models`` lists **loaded** models only.

        Returns
        -------
        ModelsResult
            Payload from ``GET /models``.

        Raises
        ------
        RuntimeError
            If the transport receives HTTP status >= 400.
        httpx.RequestError
            If the HTTP client cannot connect or times out.
        """
        return self._transport.models()

    def stats(self) -> StatsResult:
        """Return process stats. Delegates to the transport.

        Returns
        -------
        StatsResult
            Payload from ``GET /stats``.

        Raises
        ------
        RuntimeError
            If the transport receives HTTP status >= 400.
        httpx.RequestError
            If the HTTP client cannot connect or times out.
        """
        return self._transport.stats()

    def close(self) -> None:
        """Close the transport. Delegates to ``HttpTransport.close``."""
        self._transport.close()

    def __enter__(self) -> Self:
        """Enter a context and return this client.

        Returns
        -------
        Client
            ``self``.
        """
        return self

    def __exit__(self, *exc: object) -> None:
        """Exit a context by closing the transport.

        Delegates to ``close``. Does not suppress exceptions.

        Parameters
        ----------
        *exc : object
            Context-manager exception triple, unused.
        """
        self.close()
