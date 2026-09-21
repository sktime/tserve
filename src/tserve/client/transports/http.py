"""httpx transport for TServe status routes and ``POST /predict/bytes``.

TServe is a time-series foundation-model inference server. This module
implements the only concrete ``BaseTransport`` today.
"""

import json
from typing import Any

import httpx2 as httpx

from tserve.client.transports.base import BaseTransport
from tserve.types import HealthResult, ModelsResult, StatsResult
from tserve.types.converters import unpack_envelope

_ARROW_STREAM = "application/vnd.apache.arrow.stream"


class HttpTransport(BaseTransport):
    """httpx transport for TServe JSON status routes and ``/predict/bytes``.

    Parameters
    ----------
    base_url : str
        Server origin. Trailing slashes are stripped before they are
        passed to ``httpx.Client``. Ignored when ``httpx_client`` is
        given.
    timeout : float, default 60.0
        httpx timeout in seconds for a newly constructed client.
        Ignored when ``httpx_client`` is given.
    httpx_client : httpx.Client or None, default None
        Optional prebuilt client. When omitted, constructs
        ``httpx.Client(base_url=base_url.rstrip("/"), timeout=timeout)``.

    Notes
    -----
    ``predict`` always ``POST``s to ``/predict/bytes``. There is no
    JSON ``POST /predict`` path in this transport.

    HTTP status >= 400 raises ``RuntimeError``. There is no custom
    TServe exception class. ``HealthError`` is a Pydantic model nested
    under ``HealthResult.error``, not something this transport raises.

    See Also
    --------
    tserve.client.transports.base.BaseTransport
        Abstract class this transport inherits.
    tserve.types.converters.unpack_envelope
        Parses the ``application/vnd.tserve.predict+arrow`` body.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 60.0,
        httpx_client: httpx.Client | None = None,
    ) -> None:
        """Construct a transport. See ``HttpTransport`` for parameters."""
        self._client = httpx_client or httpx.Client(
            base_url=base_url.rstrip("/"), timeout=timeout
        )

    def predict(
        self, metadata: dict, bytes_encoded: dict[str, bytes]
    ) -> tuple[dict, dict[str, bytes]]:
        """POST encoded frames to ``/predict/bytes`` and unpack the envelope.

        Sends form field ``metadata`` as JSON and each Arrow IPC blob
        as a multipart file with content type
        ``application/vnd.apache.arrow.stream``. The server responds
        with ``application/vnd.tserve.predict+arrow``, which this
        method unpacks via ``unpack_envelope``.

        Parameters
        ----------
        metadata : dict
            JSON-serializable predict fields from ``encode_request``.
        bytes_encoded : dict of str to bytes
            Named Arrow IPC streams (``past``, optional ``future`` /
            ``static``).

        Returns
        -------
        metadata : dict
            Response metadata from the envelope ``response`` part.
        bytes_encoded : dict of str to bytes
            Named Arrow IPC streams (``predictions``, optional
            ``quantiles``).

        Raises
        ------
        RuntimeError
            If the HTTP status is >= 400. See ``_request``.
        ValueError
            If ``unpack_envelope`` rejects the body (truncated, bad
            magic, or unsupported version).
        json.JSONDecodeError
            If the envelope ``response`` part is not valid JSON.
        UnicodeDecodeError
            If an envelope part name is not valid UTF-8.
        httpx.RequestError
            If the HTTP client cannot connect or times out.

        See Also
        --------
        tserve.types.converters.unpack_envelope
            Inverse of the server's ``pack_envelope``.
        """
        response = self._request(
            "POST",
            "/predict/bytes",
            data={"metadata": json.dumps(metadata)},
            files={
                name: (name, blob, _ARROW_STREAM)
                for name, blob in bytes_encoded.items()
            },
        )
        return unpack_envelope(response.content)

    def health(self) -> HealthResult:
        """GET ``/health`` and validate the JSON as ``HealthResult``.

        Returns
        -------
        HealthResult
            Parsed status payload.

        Raises
        ------
        RuntimeError
            If the HTTP status is >= 400. See ``_request``.
        ValidationError
            If the JSON does not match ``HealthResult``.
        """
        return HealthResult.model_validate(self._request("GET", "/health").json())

    def models(self) -> ModelsResult:
        """GET ``/models`` and validate the JSON as ``ModelsResult``.

        Lists **loaded** models only.

        Returns
        -------
        ModelsResult
            Parsed listing of models currently loaded on the server.

        Raises
        ------
        RuntimeError
            If the HTTP status is >= 400. See ``_request``.
        ValidationError
            If the JSON does not match ``ModelsResult``.
        """
        return ModelsResult.model_validate(self._request("GET", "/models").json())

    def stats(self) -> StatsResult:
        """GET ``/stats`` and validate the JSON as ``StatsResult``.

        Returns
        -------
        StatsResult
            Parsed process and per-model metrics.

        Raises
        ------
        RuntimeError
            If the HTTP status is >= 400. See ``_request``.
        ValidationError
            If the JSON does not match ``StatsResult``.
        """
        return StatsResult.model_validate(self._request("GET", "/stats").json())

    def close(self) -> None:
        """Close the underlying ``httpx.Client``.

        Delegates to ``httpx.Client.close``.
        """
        self._client.close()

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        """Issue an HTTP request and raise ``RuntimeError`` on failure.

        Parameters
        ----------
        method : str
            HTTP method (``GET``, ``POST``, …).
        path : str
            Path relative to the client's ``base_url``.
        **kwargs : any
            Forwarded to ``httpx.Client.request``.

        Returns
        -------
        httpx.Response
            The response when ``status_code < 400``.

        Raises
        ------
        RuntimeError
            On HTTP status >= 400. If the body is JSON, uses
            ``detail["error"]`` when ``detail`` is a dict (the server
            wraps predict failures as ``HTTPException`` 400
            ``{error, code: "request_failed", request_id}``). Otherwise
            the raised message is ``str(detail)`` or the raw text body.
        httpx.RequestError
            If the HTTP client cannot connect or times out.

        Notes
        -----
        JSON is detected when ``Content-Type`` starts with
        ``application/json``. Non-JSON bodies use ``response.text``.
        """
        response = self._client.request(method, path, **kwargs)
        if response.status_code < 400:
            return response

        if response.headers.get("content-type", "").startswith("application/json"):
            body: Any = response.json()
        else:
            body = response.text
        detail = body.get("detail", body) if isinstance(body, dict) else body
        if isinstance(detail, dict):
            raise RuntimeError(str(detail.get("error", detail)))
        raise RuntimeError(str(detail))
