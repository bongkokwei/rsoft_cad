# Photonic Lantern Simulation Toolkit

> **Note:** This project is currently a work in progress.

This repository contains tools for designing, simulating, and analysing photonic lanterns - specialised optical components that enable efficient coupling between multimode and single-mode optical systems.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/rsoft_cad.git
cd rsoft_cad

# Install in development mode
pip install -e .
```

## Overview

Photonic lanterns are tapered optical structures that transform a multimode waveguide into multiple single-mode waveguides arranged in a specific geometry. These components are crucial in various applications including telecommunications, astronomy, and sensing.


## Core Modules

### `rsoft_cad.rsoft_circuit.py`

This utility class provides a Python interface for creating RSoft circuit files. It abstracts away the syntax of RSoft's circuit definition format.

**Key Classes:**
- `RSoftCircuit`: Manages circuit components and parameters

**Key Methods:**
- `add_segment()`: Add a waveguide segment to the circuit
- `add_pathways()`: Define light paths through segments
- `add_pathways_monitor()`: Add optical power monitoring
- `add_launch_field()`: Configure input light sources
- `write()`: Generate the RSoft .ind file


## Configuration System

The configuration system allows for flexible photonic lantern design without modifying the core code.

### Configuration Structure

The configuration file is organized into the following sections:

1. `pl_params`: Basic parameters for the photonic lantern design
2. `center_core_segment`: Properties of the center core
3. `center_cladding_segment`: Properties of the center cladding
4. `core_segment`: Template for surrounding cores
5. `cladding_segment`: Template for surrounding claddings
6. `capillary_segment`: Properties of the outer capillary
7. `launch_field_config`: Launch field parameters
8. `rsoft_circuit_config`: RSoft circuit configuration

### Parameter Path Format

When modifying parameters with `modify_config.py`, use dot notation to specify the parameter path:

- `pl_params.Num_Cores_Ring`: Number of cores in the ring
- `core_segment.begin.height`: Height of the core segment at the beginning
- `launch_field_config.port_num`: Port number for the launch field

## Getting Started

1. Install the package:
   ```bash
   pip install -e .
   ```

2. Run an example photonic lantern simulation:
   ```bash
   python -m examples.photonic_lantern
   ```

3. To customize your photonic lantern design:
   ```bash
   python -m rsoft_cad.utils.modify_config --param "pl_params.Num_Cores_Ring" "6" --output config/custom_config.json
   python -m examples.photonic_lantern --config config/custom_config.json --output output/custom_lantern.ind
   ```

## Design Principles

The photonic lantern is designed with the following principles:

1. The cores are arranged in a circular pattern to maximise symmetry
2. The outer cores are placed at a distance that ensures proper mode evolution

## Notes on Simulation

When running simulations:
- The launch field is configured for the specified port in the outer ring
- The taper slope represents a gradual transition to minimise losses
- All cores and cladding taper linearly along the z-axis
- The surrounding capillary provides structural support and index guiding

## File Format

The generated `.ind` files follow RSoft's circuit definition format, with parameters, segments, pathways, monitors, and launch fields defined in blocks.


## Requirements

- Python 3.6+
- NumPy 2.0+
- Matplotlib 3.0+