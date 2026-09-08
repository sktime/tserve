# Python API

Signatures for the public objects. Guides: [Python](../client/python.md) for
calling a server, [From source](../server/source.md) for running one.

## Client

Import from `fomo.client`. Needs the `client` extra.

::: fomo.client.client.Client
    options:
      heading_level: 3
      members:
        - forecast
        - health
        - models
        - stats
        - close

## Server

Import from `fomo.server`. Needs the `server` extra and a family extra for the
models you load.

::: fomo.server.serve.Server
    options:
      heading_level: 3
      members:
        - run
        - url

## Forecast request and response

`ForecastRequest` is both the JSON body of `POST /forecast` and the keyword
signature of `Client.forecast`. Table formats and column rules are in the
[data specification](../client/data.md).

::: fomo.types.models.ForecastRequest
    options:
      heading_level: 3
      members: false

::: fomo.types.models.ForecastResponse
    options:
      heading_level: 3
      members: false

## Status payloads

Returned by `client.health()`, `client.models()`, and `client.stats()`, and by
the [matching HTTP routes](http.md#status-routes).

::: fomo.types.models.HealthResult
    options:
      heading_level: 3
      members: false

::: fomo.types.models.HealthError
    options:
      heading_level: 3
      members: false

::: fomo.types.models.ModelsResult
    options:
      heading_level: 3
      members: false

::: fomo.types.models.ModelInfo
    options:
      heading_level: 3
      members: false

::: fomo.types.models.StatsResult
    options:
      heading_level: 3
      members: false

::: fomo.types.models.MemoryStats
    options:
      heading_level: 3
      members: false

::: fomo.types.models.ModelStats
    options:
      heading_level: 3
      members: false

::: fomo.types.models.RequestCounts
    options:
      heading_level: 3
      members: false

::: fomo.types.models.LatencySummary
    options:
      heading_level: 3
      members: false
