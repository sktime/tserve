# Dashboard

The running server serves a browser console at `GET /`. It talks only to the JSON endpoints (`/health`, `/models`, `/stats`, `POST /forecast`). It does not use `/forecast/bytes`.

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) after [starting a server](server.md).

## What you can do

- Pick a **loaded** model (the dropdown is `GET /models`, not the full catalog)
- Set the forecast horizon
- Optionally request a prediction interval (`quantiles`)
- Use a sample series, paste CSV, or drop a CSV file (parsed in the browser)
- Choose the time column and target columns
- Run `POST /forecast` and plot predictions

Health and stats cards on the right poll `GET /health` and `GET /stats`. Toggle **Live** to refresh every 5 seconds.

If the model list is empty, the process started without `--load-models` (or the image `CMD` was replaced with an empty list). Load an id and refresh.

## Live OpenAPI

Same origin, generated from the FastAPI app:

| UI | URL |
| --- | --- |
| Swagger | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| ReDoc | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) |
| Schema | [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json) |

Use Swagger to try `POST /forecast` from the browser. The dashboard is the friendlier console; Swagger is the contract.

Static assets live under `/static` (`index.html`, CSS, JS, favicon). There is no authentication and no hosted FoMo API — these URLs are the process you started.
