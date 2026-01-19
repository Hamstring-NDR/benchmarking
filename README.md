<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Hamstring-NDR/hamstring">
    <img src="./assets/benchmarking-logo.png" alt="Logo">
  </a>

<h3 align="center">HAMSTRING Benchmarking Suite</h3>

  <p align="center">
    Performance validation, stress testing, and stability analysis for the Hamstring NDR.
    <br />
    <br />
    <a href="https://github.com/Hamstring-NDR/hamstring-benchmarking/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/Hamstring-NDR/hamstring-benchmarking/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<!-- ABOUT THE PROJECT -->

## About The Project

This is the dedicated benchmarking suite for [Hamstring](https://github.com/Hamstring-NDR/hamstring) (formerly heiDGAF).
It is designed to validate the performance and stability of the Hamstring NDR pipeline under various load conditions.

### Architecture

The benchmarking suite consists of two main components:

* **Controller** (`src/controller`): The orchestrator of the benchmarking process.
    * Reads the `config.yaml` to determine which tests to run.
    * Manages execution parameters (data rates, durations, etc.).
    * Can trigger tests locally or on remote hosts.
    * Instructs the Test Runner to execute specific scenarios.

* **Test Runner** (`src/test_runner`): The execution engine.
    * Runs on the target machine (or within a Docker container).
    * Generates traffic/load according to the parameters received from the Controller.
    * Collects metrics and handles the actual interaction with the system under test.

### Reporting Feature

The suite includes a comprehensive **Reporting Feature** that aggregates test results into an overview PDF.

* **PDF Overview Generator**: Located in `src/test_runner/plotting/pdf_overview_generator.py`.
* **Capabilities**:
    * Combines metadata (test dates, configuration).
    * Visualizes latency comparisons and fill levels.
    * Plots throughput (entering vs. processed logs) over time.
    * Generates a single, easy-to-read PDF report for each test run, saved in the `testing_reports` directory.

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* **Docker**: Ensure Docker and Docker Compose are installed.
* **Python**: Python 3.10+ is recommended.
* **Hamstring Containers**:
  > [!IMPORTANT]
  > **The Hamstring containers must be running before starting any benchmarks.**
  > The benchmarking suite connects to the existing `docker_heidgaf` network to inject traffic.
  >
  > ```sh
    > # In the main Hamstring project directory:
    > HOST_IP=127.0.0.1 docker compose -f docker/docker-compose.yml up -d
    > ```

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/Hamstring-NDR/hamstring-benchmarking.git
   cd hamstring-benchmarking
   ```

2. Create and activate a virtual environment:
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the dependencies (editable mode is recommended):
   ```sh
   pip install -e .
   ```
    * Or install specific requirements via `pip install -r requirements.txt` (if available),
      or `sh install_requirements.sh`.

<!-- USAGE EXAMPLES -->
## Usage

### Configuration

Configure your test runs in `config.yaml`. You can define:

* **Remote Execution**: Host details and SSH keys.
* **Tests**:
    * **Ramp Up**: Gradually increases load.
    * **Burst**: Simulates spikes in traffic.
    * **Maximum Throughput**: Tests the absolute limit of the system.
    * **Long Term**: Stability testing over hours or days.
* **Test Runs**: List of tests to execute sequentially (e.g., `["ramp_up", "burst"]`).

### Running Tests

To start the configured benchmarks, run the controller:

```sh
python src/controller/benchmark_controller.py
```

The controller will:

1. Parse the `config.yaml`.
2. Connect to the `benchmark_test_runner` container (or remote host).
3. Execute the defined tests sequentially.
4. Generate PDF reports upon completion.

### Output

Ranked results and PDF reports will be generated in:

* `benchmark_results/`: Raw data and individual graphs.
* `testing_reports/`: Consolidated PDF overview reports.

<!-- LICENSE -->
## License

Distributed under the EUPL License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
