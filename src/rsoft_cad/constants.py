"""
Constants and configuration data for the RSoft CAD package.
"""

# LP mode cutoff frequencies (normalized)
lp_mode_cutoffs_freq = {
    "LP01": 0.000,  # No cutoff (always guided)
    "LP11": 2.405,  # First zero of J0
    "LP21": 3.832,  # First zero of J1
    "LP02": 3.832,  # Second zero of J0
    "LP31": 5.136,  # First zero of J2
    "LP12": 5.520,  # Second zero of J1
    "LP41": 6.380,  # First zero of J3
    "LP22": 7.016,  # Second zero of J2
    "LP03": 7.016,  # Third zero of J0
    "LP51": 7.588,  # First zero of J4
    "LP13": 8.654,  # Third zero of J1
    "LP32": 8.417,  # Second zero of J3
    "LP61": 8.772,  # First zero of J5
    "LP42": 9.761,  # Second zero of J4
    "LP71": 9.936,  # First zero of J6
    "LP23": 10.174,  # Third zero of J2
    "LP04": 10.174,  # Fourth zero of J0
    "LP52": 11.065,  # Second zero of J5
    "LP81": 11.086,  # First zero of J7
    "LP33": 11.620,  # Third zero of J3
    "LP14": 11.792,  # Fourth zero of J1
    "LP91": 12.225,  # First zero of J8
    "LP62": 12.339,  # Second zero of J6
    "LP43": 13.015,  # Third zero of J4
    "LP24": 13.324,  # Fourth zero of J2
    "LP05": 13.324,  # Fifth zero of J0
}

# Default fiber properties
DEFAULT_FIBER_PROPS = {
    "core_dia": 10.4,  # Core diameter in microns
    "cladding_dia": 125.0,  # Cladding diameter in microns
    "core_index": 1.45213,  # Core refractive index
    "cladding_index": 1.44692,  # Cladding refractive index
    "bg_index": 1.4345,  # Background refractive index
    "pos_x": 0,  # X position in microns
    "pos_y": 0,  # Y position in microns
    "pos_z": 0,  # Z position in microns
    "taper_factor": 1,  # Taper factor
    "taper_length": 80000,  # Taper length in microns
}
