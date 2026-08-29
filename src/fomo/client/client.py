"""High-level Python client for a FoMo inference server.

FoMo is a time-series foundation-model inference server. ``Client``
builds a ``ForecastRequest``, runs the *wire* converters in
``fomo.types.converters``, and sends metadata plus named frame blobs
through a ``BaseTransport``. Mapping a coerced request onto sktime
``(y, X, fh)`` is a different layer:
``fomo.runtime.executors.sktime.converters``.

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
from fomo.types import (
    ForecastRequest,
    ForecastResponse,
    HealthResult,
    ModelsResult,
    StatsResult,
)
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
        Passed to the default ``HttpTransport`` when ``transport`` is
        omitted. Ignored if ``transport`` is given.
    timeout : float, default 60.0
        Passed to the default ``HttpTransport`` when ``transport`` is
        omitted. Ignored if ``transport`` is given.
    transport : BaseTransport or None, default None
        Optional prebuilt transport. When omitted, constructs
        ``HttpTransport(url, timeout=timeout)``.

    Notes
    -----
    ``HttpTransport`` is the default transport.

    See Also
    --------
    fomo.client.transports.base.BaseTransport
        Abstract transport type.
    fomo.client.transports.http.HttpTransport
        Default HTTP transport.
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
        past: Any,
        time: str,
        target: list[str],
        fh: int,
        model: str = "naive",
        future: Any = None,
        static: Any = None,
        quantiles: list[float] | None = None,
    ) -> ForecastResponse:
        """Send a forecast through the transport and restore native frames.

        Builds a ``ForecastRequest``, then runs ``coerce_request`` →
        ``encode_request`` (JSON metadata + Arrow IPC blobs) →
        ``BaseTransport.forecast`` → ``decode_response`` →
        ``_from_narwhals(template=past)`` so returned frames match
        the caller's native type.

        Parameters
        ----------
        past : any
            Past observations. Native type is the template for returned
            frames. See ``ForecastRequest`` for accepted shapes.
        time : str
            Time-index column name.
        target : list of str
            Target column names.
        fh : int
            Forecast steps ahead.
        model : str, default ``"naive"``
            Loaded model id, not an executor name.
        future : any, optional
            Future rows for known covariates.
        static : any, optional
            Per-series static features.
        quantiles : list of float, optional
            Quantile alphas when the executor supports them.

        Returns
        -------
        ForecastResponse
            ``predictions`` and optional ``quantiles`` restored to the
            native type of ``past``.

        Raises
        ------
        ValidationError
            If ``ForecastRequest`` construction or ``coerce_request``
            fails (shape, columns, field constraints). Inner
            validators raise ``ValueError``, which Pydantic wraps.
        RuntimeError
            If the transport reports a failed forecast. There is no
            custom FoMo exception class; ``HealthError`` is a Pydantic
            model, not raised here.
        Exception
            Other transport failures (connection, encoding, decode of
            the returned blobs). See ``HttpTransport`` for the HTTP
            error surface.

        See Also
        --------
        fomo.types.models.ForecastRequest
            Full field semantics for past/time/target/fh/
            model/future/static/quantiles.
        fomo.types.converters.coerce_request
            Wire conversion to ``CoercedForecastRequest``.
        fomo.types.converters.encode_request
            Split into JSON metadata and Arrow IPC files.
        fomo.client.transports.base.BaseTransport.forecast
            Transport call that carries metadata and frame blobs.
        fomo.client.transports.http.HttpTransport.forecast
            HTTP default: ``POST /forecast/bytes``.
        fomo.types.converters.decode_response
            Rebuild the coerced response from metadata and blobs.
        """
        request = ForecastRequest(
            past=past,
            time=time,
            target=target,
            fh=fh,
            model=model,
            future=future,
            static=static,
            quantiles=quantiles,
        )
        coerced = coerce_request(request)

        # 1. encode request to json + bytes
        req_metadata, req_bytes_encoded = encode_request(coerced)
        # 2. send request to transport
        res_metadata, res_bytes_encoded = self._transport.forecast(
            req_metadata, req_bytes_encoded
        )
        # 3. decode response to json + bytes
        response = decode_response(res_metadata, res_bytes_encoded)

        predictions = _from_narwhals(response.predictions, past)
        quantile_table = (
            _from_narwhals(response.quantiles, past)
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
        """Return runtime health. Delegates to the transport.

        Returns
        -------
        HealthResult
            Status payload from the transport.

        Raises
        ------
        Exception
            Transport failures. See ``HttpTransport`` for the HTTP
            error surface.
        """
        return self._transport.health()

    def models(self) -> ModelsResult:
        """Return loaded models. Delegates to the transport.

        Lists **loaded** models only, not the full registry catalog.

        Returns
        -------
        ModelsResult
            Listing from the transport.

        Raises
        ------
        Exception
            Transport failures. See ``HttpTransport`` for the HTTP
            error surface.
        """
        return self._transport.models()

    def stats(self) -> StatsResult:
        """Return process stats. Delegates to the transport.

        Returns
        -------
        StatsResult
            Metrics payload from the transport.

        Raises
        ------
        Exception
            Transport failures. See ``HttpTransport`` for the HTTP
            error surface.
        """
        return self._transport.stats()

    def close(self) -> None:
        """Close the transport. Delegates to ``BaseTransport.close``."""
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
