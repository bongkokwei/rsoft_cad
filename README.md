# Photonic Lantern Simulation Toolkit

## Overview

The Photonic Lantern Simulation Toolkit is a comprehensive Python package for designing, simulating, and analysing photonic lanterns - specialised optical components that enable efficient coupling between multimode and single-mode optical systems.

## Features

### Key Capabilities
- Multi-core fibre and photonic lantern design
- Flexible configuration management
- Advanced mode selective lantern generation
- Simulation file generation for RSoft CAD
- Geometric layout visualisation
- Parametric design exploration

### Supported Functionalities
- Hexagonal and circular fibre layouts
- Mode coupling analysis
- Customisable fibre parameters
- Automated lantern geometry calculations
- Simulation file generation

## Installation

```bash
# Clone the repository
git clone https://github.com/bongkokwei/rsoft_cad.git
cd rsoft_cad

# Install in development mode
pip install -e .
```

## Core Modules

### Configuration Management
- `modify_config.py`: Utility for modifying configuration files
- Supports dynamic parameter changes
- Enables easy exploration of design parameters

### Fibre and Lantern Design
- `rsoft_mspl.py`: Mode Selective Photonic Lantern (MSPL) generator
- Supports multiple LP mode configurations
- Automatic mode mapping and positioning

### Simulation Utilities
- `rsoft_simulations.py`: Handles simulation file generation and execution
- Supports different simulation backends
- File renaming and processing utilities

## Design Principles

### Mode Selection
- Supports multiple LP modes (LP01, LP11, LP21, etc.)
- Automatic mode cutoff frequency management
- Flexible core diameter and index configuration

### Geometric Layout
- Hexagonal and circular fibre arrangements
- Automatic capillary diameter calculation
- Precise mode positioning algorithms

## Example Usage

### Creating and Simulating a Multi-Core Fibre
```python
from rsoft_cad.rsoft_mspl import ModeSelectiveLantern
from rsoft_cad.rsoft_simulations import run_simulation
import os

# Create a mode selective lantern
mspl = ModeSelectiveLantern()
core_map = mspl.create_lantern(
    highest_mode="LP11",
    launch_mode="LP01",
    taper_factor=5,
    taper_length=80000,
    savefile=True  # Ensure the file is saved for simulation
)

# Run simulation
filepath = mspl.design_filepath
filename = mspl.design_filename

# Simulate the lantern design
simulation_result = run_simulation(
    filepath,
    filename,
    sim_package="bsimw32",
    prefix_name=f"LP01_taper_80000",
    save_folder="mode_selective_lantern_simulations",
    hide_sim=True
)

# Optional: Check simulation output
print(f"Simulation completed with return code: {simulation_result.returncode}")
print("Simulation stdout:", simulation_result.stdout)
print("Simulation stderr:", simulation_result.stderr)
```

### Running Batch Simulations
For systematic exploration, you can create loops to vary parameters:
```python
taper_lengths = [50000, 60000, 70000, 80000, 90000]
launch_modes = ["LP01", "LP11"]

for launch_mode in launch_modes:
    for taper_length in taper_lengths:
        # Create lantern with current parameters
        mspl = ModeSelectiveLantern()
        core_map = mspl.create_lantern(
            highest_mode="LP11",
            launch_mode=launch_mode,
            taper_factor=5,
            taper_length=taper_length,
            savefile=True
        )
        
        # Run simulation
        run_simulation(
            mspl.design_filepath,
            mspl.design_filename,
            sim_package="bsimw32",
            prefix_name=f"{launch_mode}_taper_{taper_length}",
            save_folder="parameter_sweep_simulations",
            hide_sim=True
        )
```

## Visualisation

The toolkit provides visualisation utilities:
- Hexagonal fibre layout plotting
- Mode positioning visualisation
- Capillary and core diameter representations

## Requirements

- Python 3.6+
- NumPy 2.0+
- Matplotlib 3.0+

## Simulation Workflow

1. Design Configuration
2. Parameter Optimisation
3. Lantern Geometry Generation
4. Simulation File Creation
5. Simulation Execution
6. Results Analysis

## Planned Improvements
- Machine learning integration
- More comprehensive design space exploration
- Advanced visualisation tools

## Contact

Kok-Wei Bong - bongkokwei@gmail.com