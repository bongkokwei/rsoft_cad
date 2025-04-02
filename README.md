# Photonic Lantern Simulation Toolkit

> **Note:** This project is currently a work in progress.

This repository contains tools for designing, simulating, and analysing photonic lanterns - specialised optical components that enable efficient coupling between multimode and single-mode optical systems.

## Overview

Photonic lanterns are tapered optical structures that transform a multimode waveguide into multiple single-mode waveguides arranged in a specific geometry. These components are crucial in various applications including telecommunications, astronomy, and sensing.

## Files in this Repository

### 1. `lantern_layout.py`

This script provides functionality to calculate and visualise the geometric arrangement of fibres in a photonic lantern.

**Key Features:**
- Calculate the optimal radius for arranging `n` cladding circles in a lantern layout
- Generate visualisations of the lantern cross-section
- Analyse scaling relationships between cladding diameter and lantern radius

**Usage Example:**
```python
# Calculate layout for 5 fibres with 125μm cladding diameter
R, centres_x, centres_y = lantern_layout(cladding_dia=125, n=5)

# Display key dimensions
print(f"Radius of lantern modes: {R:.2f} micron")
print(f"Radius of centre core: {R - (cladding_dia / 2):.2f} micron")
print(f"Radius of capillary: {R + (cladding_dia / 2):.2f} micron")
```

### 2. `photonic_lantern.py`

This script defines a complete photonic lantern structure with tapered cores and cladding for simulation in RSoft.

**Key Features:**
- Configurable parameters for lantern design (number of cores, taper length, etc.)
- Creates a six-core photonic lantern with centre core plus five surrounding cores
- Automatically generates the tapered structure with proper refractive indices
- Includes launch field setup for simulation

**Configuration Parameters:**
- `Num_Cores_Ring`: Number of cores in the outer ring (default: 5)
- `Taper_Length`: Length of the taper section in microns (default: 55000)
- `Taper_Slope`: Taper ratio (default: 14.9)
- `Diameter_SM_Clad`: Diameter of single-mode fibre cladding (default: 125μm)
- `Diameter_SM_Core`: Diameter of single-mode fibre core (default: 8.2μm)

### 3. `rsoft_circuit.py`

This utility class provides a Python interface for creating RSoft circuit files. It abstracts away the syntax of RSoft's circuit definition format.

**Key Classes:**
- `RSoftCircuit`: Manages circuit components and parameters

**Key Methods:**
- `add_segment()`: Add a waveguide segment to the circuit
- `add_pathways()`: Define light paths through segments
- `add_pathways_monitor()`: Add optical power monitoring
- `add_launch_field()`: Configure input light sources
- `write()`: Generate the RSoft .ind file

## Getting Started

1. Install dependencies:
   ```
   pip install numpy matplotlib
   ```

2. To visualise a lantern layout:
   ```
   python lantern_layout.py
   ```

3. To generate an RSoft circuit file for a six-core photonic lantern:
   ```
   python photonic_lantern.py
   ```
   This will create a file at `output/six_core_PL.ind`

## Design Principles

The photonic lantern is designed with the following principles:

1. The cores are arranged in a circular pattern to maximise symmetry
2. The outer cores are placed at a distance that ensures proper mode evolution

## Notes on Simulation

When running simulations:
- The launch field is configured for the second port in the outer ring
- The taper slope of 14.9 represents a gradual transition to minimise losses
- All cores and cladding taper linearly along the z-axis
- The surrounding capillary provides structural support and index guiding

## File Format

The generated `.ind` files follow RSoft's circuit definition format, with parameters, segments, pathways, monitors, and launch fields defined in blocks.