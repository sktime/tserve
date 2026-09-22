# Installation

Choose how you want to run the TServe server. **Docker is the fastest and recommended way**: each image already contains the dependencies for its model family, and separate CPU and GPU tags remove any torch setup work.

## Docker

Install [Docker Desktop](https://docs.docker.com/desktop/) on macOS or Windows, or [Docker Engine](https://docs.docker.com/engine/install/) on Linux.

Pull the `hub` image, which supports Chronos Bolt/T5, TTM, and TimesFM 2.x:

=== "CPU"

    ```bash
    docker pull sktime/tserve:hub
    ```

=== "GPU"

    NVIDIA hosts need the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) and `--gpus all` at runtime:

    ```bash
    docker pull sktime/tserve:hub-gpu
    ```

Other model families use different image tags. Choose the model first, then use its tag from the [model catalog](models/index.md#dependencies). Every CPU tag has a `-gpu` variant. For Hugging Face tokens, cache volumes, and all Docker options, see [Docker](server/docker.md).

## UV / Pip

TServe requires Python 3.12 or newer. Install the `server` extra and the extra for the model family you need. The examples below install the `hub` family. A plain install pulls the CUDA build of torch (MPS on macOS); the CPU tabs skip that download on a machine without a GPU.

=== "uv"

    Install [uv](https://docs.astral.sh/uv/getting-started/installation/), create a virtual environment, and install TServe:

    ```bash
    uv venv
    ```

    Then install TServe:

    === "GPU (default)"

        ```bash
        uv pip install "tserve[server,hub]"
        ```

    === "CPU only"

        ```bash
        uv pip install torch --index-url https://download.pytorch.org/whl/cpu
        ```

        ```bash
        uv pip install "tserve[server,hub]"
        ```

=== "pip"

    Create a [virtual environment](https://docs.python.org/3/library/venv.html), activate it, and install TServe:

    === "macOS / Linux"

        ```bash
        python -m venv .venv
        source .venv/bin/activate
        ```

    === "Windows PowerShell"

        ```powershell
        py -m venv .venv
        .venv\Scripts\Activate.ps1
        ```

    Then install TServe:

    === "GPU (default)"

        ```bash
        python -m pip install "tserve[server,hub]"
        ```

    === "CPU only"

        ```bash
        python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
        ```

        ```bash
        python -m pip install "tserve[server,hub]"
        ```

The `server` extra alone supports the `naive` test baseline. Replace `hub` with another [family extra](models/index.md#dependencies), or use `full` for every family. The same CPU-first order is documented as [CPU-only install](server/pip.md#cpu-only-install).

## From source

Use a source install when developing TServe or testing unreleased changes. It is also the only path where the `gpu` extra selects the torch index, because that choice lives in the repository's uv lockfile. The [From source](server/source.md) guide covers cloning the repository, editable installs, dependency extras, and GPU setup.

## Next

Continue to the [Quick start](quick-start.md) to launch the server and send your first prediction.
