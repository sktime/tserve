"""Python client for a running FoMo inference server.

Import ``Client`` from ``fomo.client``. Tables keep the type you send
as ``past`` (pandas, polars, pyarrow, narwhals, or dict). JSON
``POST /predict`` is the curl path; this client sends Arrow to
``POST /predict/bytes``.
"""

from typing import Any, Self

from fomo.client.transports.base import BaseTransport
from fomo.client.transports.http import HttpTransport
from fomo.types import (
    HealthResult,
    ModelsResult,
    PredictRequest,
    PredictResponse,
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

    The client connects to a local FoMo server. Use it as a context
    manager so the HTTP session is closed.

    Parameters
    ----------
    url : str
        Server origin, for example ``"http://127.0.0.1:8000"``.
        Ignored if ``transport`` is given.
    timeout : float, default 60.0
        Request timeout in seconds. Ignored if ``transport`` is given.
    transport : BaseTransport or None, default None
        Optional prebuilt transport. When omitted, uses HTTP.

    Examples
    --------
    >>> from fomo.client import Client
    >>> with Client("http://127.0.0.1:8000") as client:
    ...     result = client.predict(
    ...         past={"timestamp": ["2024-01-01", "2024-01-02"], "sales": [120, 135]},
    ...         time="timestamp",
    ...         target=["sales"],
    ...         fh=3,
    ...         model="naive",
    ...     )

    See Also
    --------
    [Python client](../client/python.md)
        Install, connect, predict, and use native table types.
    [Install and serve](../server/index.md)
        Start the local server this client calls.
    [HTTP API](../client/http.md)
        Send the same predict fields as JSON instead of Arrow.
    """

    def __init__(
        self,
        url: str,
        *,
        timeout: float = 60.0,
        transport: BaseTransport | None = None,
    ) -> None:
        """Construct a Client."""
        self._transport = transport or HttpTransport(url, timeout=timeout)

    def predict(
        self,
        *,
        past: Any,
        fh: int,
        time: str | None = None,
        target: str | list[str] | None = None,
        model: str = "naive",
        future: Any = None,
        static: Any = None,
        quantiles: list[float] | None = None,
    ) -> PredictResponse:
        """Send a prediction and restore tables to the type of ``past``.

        Parameters
        ----------
        past : any
            Past observations (dict, pandas, polars, …). Return type
            of ``predictions`` matches this.
        fh : int
            Prediction steps ahead (``> 0``).
        time : str, optional
            Time-index column. When omitted, the first column of
            ``past`` is used.
        target : str or list of str, optional
            Target column names. When omitted, remaining ``past``
            columns are used.
        model : str, default ``"naive"``
            Loaded model id (see ``GET /models``).
        future : any, optional
            Future timestamps when using ``static``.
        static : any, optional
            One-row static features, broadcast over time.
        quantiles : list of float, optional
            Quantile alphas, e.g. ``[0.1, 0.5, 0.9]``.

        Returns
        -------
        PredictResponse
            ``predictions``, optional ``quantiles``, ``model``, and
            ``request_id``.

        Raises
        ------
        ValidationError
            If the request shape or columns are invalid.
        RuntimeError
            If the server returns HTTP >= 400.

        Notes
        -----
        This method sends Arrow tables to ``POST /predict/bytes``.
        JSON clients use ``POST /predict``.

        See Also
        --------
        [Data specification](../client/data.md)
            Table formats, column roles, inference, and response fields.
        [Models catalog](../models/index.md)
            Available model ids and their dependencies.
        [Errors](../reference/errors.md)
            Local validation, transport, and server failures.
        """
        request = PredictRequest(
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
        res_metadata, res_bytes_encoded = self._transport.predict(
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

        return PredictResponse(
            predictions=predictions,
            model=response.model,
            request_id=response.request_id,
            quantiles=quantile_table,
        )

    def health(self) -> HealthResult:
        """Return ``GET /health`` (liveness).

        Returns
        -------
        HealthResult
            Currently ``status='ok'``.

        See Also
        --------
        [HTTP status routes](../reference/http.md#status-routes)
            Route behavior and response examples.
        """
        return self._transport.health()

    def models(self) -> ModelsResult:
        """Return ``GET /models`` — loaded ids, not the registry catalog.

        Returns
        -------
        ModelsResult
            Each row has ``id``, ``executor``, and ``source``.

        See Also
        --------
        [Models catalog](../models/index.md)
            Model ids the server can load.
        [HTTP status routes](../reference/http.md#status-routes)
            Loaded-model response semantics.
        """
        return self._transport.models()

    def stats(self) -> StatsResult:
        """Return ``GET /stats`` — uptime, memory, per-model latency.

        Returns
        -------
        StatsResult
            Process and per-loaded-id metrics.

        See Also
        --------
        [HTTP status routes](../reference/http.md#status-routes)
            Stats response fields and example.
        """
        return self._transport.stats()

    def close(self) -> None:
        """Close the HTTP session.

        Called automatically when a ``with Client(...)`` block exits.

        See Also
        --------
        [Python client](../client/python.md#connect)
            Context-manager usage.
        """
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
