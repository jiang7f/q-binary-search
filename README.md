## Overview

This repository consists of three main components:

* **`env_setup/`**: Conda environment configuration files
* **`qbs/`**: Source code for the qbs algorithm
* **`reproduce/`**: Scripts and notebooks for reproducing the experiments in the paper

## Installation

### 1. Set up the Conda environment

Navigate to the environment setup directory:

```bash
cd env_setup
```

Install the CPU-compatible environment:

```bash
conda env create -f cpu-env.yml
```

Activate the environment:

```bash
conda activate qbs
```

If the installation fails or is interrupted, remove the environment and reinstall:

```bash
conda remove -n qbs --all
```

### 2. GPU Support (Optional)

Our method is accelerated using the DDSIM backend and already runs efficiently on CPU.  

GPU acceleration via `qiskit-aer-gpu` is optional and can speed up baseline simulations (e.g., HEA and QAOA), which involve many `RX` gates. However, the CPU environment alone is sufficient for reproducing all experimental results.

To enable GPU support on Linux, you must have CUDA 11.2 or later and a compatible GPU driver installed.

#### Option A: Preconfigured environment for CUDA 12.8

If CUDA 12.8 is available on your system, you can set up the environment directly with:

```bash
conda env create -f gpu-cuda12.8-env.yml
```

#### Option B: Manual installation for other CUDA versions

To add GPU support to an existing `qbs` environment, simply install the GPU simulator with:

```bash
pip install qiskit-aer-gpu
```

## Verify Installation

Run the environment check script located in the `env_setup/` directory:

```bash
python env_check.py
```

If your environment is correctly configured, you will see:

```
✅ CPU environment configured successfully!
```

If GPU support is also correctly set up, you will additionally see:

```
✅ GPU environment configured successfully!
```

The programs in `reproduce/` will automatically detect whether GPU acceleration is available. No manual switching is required.

If the test fails, consider:

1. Ensuring the correct Conda environment is activated.
2. Making sure the Python environment is isolated from global site-packages. You may disable the user site by:

   ```bash
   export PYTHONNOUSERSITE=1
   ```

## Troubleshooting

This section summarizes known issues that may arise during execution and provides suggested workarounds.

### 1. `A process in the process pool was terminated abruptly while the future was running or pending.`

These errors may occur when **too many reproduction programs are executed simultaneously**, causing excessive load on the CPU or GPU.

**Solution:**
Run the reproduction programs **one at a time**, preferably in sequence. If the issue persists even with sequential execution, consider reducing parallelism by adjusting the `num_processes` variable in the script, or switching to a machine with more resources.

### 2. Output files are missing or not saved in the expected subdirectory

This usually happens when the script is executed from the wrong working directory, since output paths are **relative to the execution location**.

**Solution:**
Make sure to **run each script from within its corresponding subdirectory** (e.g., `figure_x/` or `table_2/`) so that output files are saved in the correct place.
