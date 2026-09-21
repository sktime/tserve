# Python API

Signatures for the public objects. Guides: [Python](../client/python.md) for calling a server, [From source](../server/source.md) for running one.

## Client

Import from `tserve.client`. Needs the `client` extra.

::: tserve.client.client.Client
    options:
      heading_level: 3
      members:
        - predict
        - health
        - models
        - stats
        - close

## Server

Import from `tserve.server`. Needs the `server` extra and a family extra for the models you load.

::: tserve.server.serve.Server
    options:
      heading_level: 3
      members:
        - run
        - url

## Predict request and response

`PredictRequest` is both the JSON body of `POST /predict` and the keyword signature of `Client.predict`. Table formats and column rules are in the [data specification](../client/data.md).

::: tserve.types.models.PredictRequest
    options:
      heading_level: 3
      members: false

::: tserve.types.models.PredictResponse
    options:
      heading_level: 3
      members: false

## Status payloads

Returned by `client.health()`, `client.models()`, and `client.stats()`, and by the [matching HTTP routes](http.md#status-routes).

::: tserve.types.models.HealthResult
    options:
      heading_level: 3
      members: false

::: tserve.types.models.HealthError
    options:
      heading_level: 3
      members: false

::: tserve.types.models.ModelsResult
    options:
      heading_level: 3
      members: false

::: tserve.types.models.ModelInfo
    options:
      heading_level: 3
      members: false

::: tserve.types.models.StatsResult
    options:
      heading_level: 3
      members: false

::: tserve.types.models.MemoryStats
    options:
      heading_level: 3
      members: false

::: tserve.types.models.ModelStats
    options:
      heading_level: 3
      members: false

::: tserve.types.models.RequestCounts
    options:
      heading_level: 3
      members: false

::: tserve.types.models.LatencySummary
    options:
      heading_level: 3
      members: false
