<div class="tserve-hero" markdown>

# TServe

Time series serving for foundation models. Load models once, keep them warm, and forecast from any HTTP client or from Python.
{ .tserve-hero__tagline }

[Quick start](quick-start.md){ .md-button .md-button--primary }
[Install TServe](installation.md){ .md-button }

</div>

TServe is a server you run, not a hosted API. It loads named time-series models and exposes predictions through JSON, a type-preserving Python client, and a browser dashboard.

<div class="grid cards" markdown>

-   :material-docker:{ .lg .middle } **Run anywhere**

    ---

    Start with a Docker image, or install with UV or Pip. CPU and GPU options are available.

-   :material-cube-outline:{ .lg .middle } **Choose your models**

    ---

    Serve Chronos, TTM, TimesFM, Moirai, Toto, TiRex, FlowState, Kronos, Mantis, and more.

-   :material-api:{ .lg .middle } **Use your preferred client**

    ---

    Send JSON from any language, or preserve pandas, polars, pyarrow, and dict inputs with Python.

-   :material-chart-line:{ .lg .middle } **Keep models warm**

    ---

    Pay model download and load costs at startup instead of on every prediction.

</div>

## Next steps

<div class="grid cards" markdown>

-   :material-rocket-launch-outline:{ .lg .middle } **Quick start**

    ---

    Launch a server and send your first forecast.

    [:octicons-arrow-right-24: Quick start](quick-start.md)

-   :material-download-outline:{ .lg .middle } **Installation**

    ---

    Choose Docker, UV, Pip, or a source install.

    [:octicons-arrow-right-24: Install TServe](installation.md)

-   :material-map-outline:{ .lg .middle } **Overview**

    ---

    Understand servers, transports, canonical frames, and executors.

    [:octicons-arrow-right-24: How TServe works](overview.md)

-   :material-cube-outline:{ .lg .middle } **Model catalog**

    ---

    Find a model and its matching Docker tag or dependency extra.

    [:octicons-arrow-right-24: Browse models](models/index.md)

-   :material-server:{ .lg .middle } **Server**

    ---

    Configure model loading, CLI flags, saved models, and the dashboard.

    [:octicons-arrow-right-24: Run a server](server/index.md)

-   :material-api:{ .lg .middle } **Clients**

    ---

    Send forecasts over HTTP or with the Python client.

    [:octicons-arrow-right-24: Send predictions](client/index.md)

</div>
