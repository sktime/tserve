# Python API

Public entry points. Guides use [`Client`][fomo.client.client.Client], [`Server`][fomo.server.serve.Server], and [`ForecastRequest`][fomo.types.models.ForecastRequest].

## Client

::: fomo.client.client.Client
    options:
      members:
        - forecast
        - health
        - models
        - stats
        - close

## Server

::: fomo.server.serve.Server
    options:
      members:
        - run
        - url

## Request and response

::: fomo.types.models.ForecastRequest
    options:
      members: false

::: fomo.types.models.ForecastResponse
    options:
      members: false

## Status payloads

::: fomo.types.models.HealthResult
    options:
      members: false

::: fomo.types.models.ModelsResult
    options:
      members: false

::: fomo.types.models.ModelInfo
    options:
      members: false

::: fomo.types.models.StatsResult
    options:
      members: false
