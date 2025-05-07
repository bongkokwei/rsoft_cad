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

# Single-mode fiber specifications as a list of dictionaries
SINGLE_MODE_FIBERS = [
    {
        "Fiber_Type": "SMF-28",
        "Manufacturer": "Corning",
        "Core_Index": 1.4677,
        "Core_Diameter_micron": 8.2,
        "Cladding_Index": 1.4624,
        "Cladding_Diameter_micron": 125,
        "Cutoff_Wavelength_nm": 1260,
        "Mode_Field_Diameter_micron": 10.4,
        "Numerical_Aperture": 0.14,
        "Attenuation_dB_km": 0.18,
        "V_Number": 2.3268,
        "Relative_Delta_percent": 0.3605,
    },
    {
        "Fiber_Type": "LEAF",
        "Manufacturer": "Corning",
        "Core_Index": 1.4681,
        "Core_Diameter_micron": 9.6,
        "Cladding_Index": 1.4623,
        "Cladding_Diameter_micron": 125,
        "Cutoff_Wavelength_nm": 1450,
        "Mode_Field_Diameter_micron": 10.7,
        "Numerical_Aperture": 0.14,
        "Attenuation_dB_km": 0.2,
        "V_Number": 2.7241,
        "Relative_Delta_percent": 0.3943,
    },
    {
        "Fiber_Type": "OS2",
        "Manufacturer": "Various",
        "Core_Index": 1.4675,
        "Core_Diameter_micron": 8.5,
        "Cladding_Index": 1.462,
        "Cladding_Diameter_micron": 125,
        "Cutoff_Wavelength_nm": 1260,
        "Mode_Field_Diameter_micron": 9.8,
        "Numerical_Aperture": 0.13,
        "Attenuation_dB_km": 0.22,
        "V_Number": 2.2397,
        "Relative_Delta_percent": 0.3741,
    },
    {
        "Fiber_Type": "TrueWave RS",
        "Manufacturer": "OFS",
        "Core_Index": 1.4685,
        "Core_Diameter_micron": 7.5,
        "Cladding_Index": 1.4628,
        "Cladding_Diameter_micron": 125,
        "Cutoff_Wavelength_nm": 1320,
        "Mode_Field_Diameter_micron": 8.7,
        "Numerical_Aperture": 0.15,
        "Attenuation_dB_km": 0.23,
        "V_Number": 2.2802,
        "Relative_Delta_percent": 0.3874,
    },
    {
        "Fiber_Type": "G.652.D",
        "Manufacturer": "Various",
        "Core_Index": 1.4679,
        "Core_Diameter_micron": 8.3,
        "Cladding_Index": 1.4625,
        "Cladding_Diameter_micron": 125,
        "Cutoff_Wavelength_nm": 1260,
        "Mode_Field_Diameter_micron": 10.5,
        "Numerical_Aperture": 0.14,
        "Attenuation_dB_km": 0.19,
        "V_Number": 2.3552,
        "Relative_Delta_percent": 0.3672,
    },
    {
        "Fiber_Type": "G.655",
        "Manufacturer": "Various",
        "Core_Index": 1.4682,
        "Core_Diameter_micron": 7.8,
        "Cladding_Index": 1.4627,
        "Cladding_Diameter_micron": 125,
        "Cutoff_Wavelength_nm": 1480,
        "Mode_Field_Diameter_micron": 9.2,
        "Numerical_Aperture": 0.15,
        "Attenuation_dB_km": 0.22,
        "V_Number": 2.3714,
        "Relative_Delta_percent": 0.3739,
    },
    {
        "Fiber_Type": "G.657.A2",
        "Manufacturer": "Various",
        "Core_Index": 1.4676,
        "Core_Diameter_micron": 8.0,
        "Cladding_Index": 1.4621,
        "Cladding_Diameter_micron": 125,
        "Cutoff_Wavelength_nm": 1280,
        "Mode_Field_Diameter_micron": 9.5,
        "Numerical_Aperture": 0.13,
        "Attenuation_dB_km": 0.21,
        "V_Number": 2.1079,
        "Relative_Delta_percent": 0.3741,
    },
    {
        "Fiber_Type": "IDF",
        "Manufacturer": "OFS",
        "Core_Index": 1.467,
        "Core_Diameter_micron": 6.0,
        "Cladding_Index": 1.461,
        "Cladding_Diameter_micron": 125,
        "Cutoff_Wavelength_nm": 1200,
        "Mode_Field_Diameter_micron": 7.5,
        "Numerical_Aperture": 0.16,
        "Attenuation_dB_km": 0.24,
        "V_Number": 1.9458,
        "Relative_Delta_percent": 0.4082,
    },
    {
        "Fiber_Type": "SMF-28e+",
        "Manufacturer": "Corning",
        "Core_Index": 1.4678,
        "Core_Diameter_micron": 8.3,
        "Cladding_Index": 1.4624,
        "Cladding_Diameter_micron": 125,
        "Cutoff_Wavelength_nm": 1260,
        "Mode_Field_Diameter_micron": 10.5,
        "Numerical_Aperture": 0.14,
        "Attenuation_dB_km": 0.17,
        "V_Number": 2.3552,
        "Relative_Delta_percent": 0.3672,
    },
    {
        "Fiber_Type": "AllWave",
        "Manufacturer": "OFS",
        "Core_Index": 1.4676,
        "Core_Diameter_micron": 8.4,
        "Cladding_Index": 1.4622,
        "Cladding_Diameter_micron": 125,
        "Cutoff_Wavelength_nm": 1250,
        "Mode_Field_Diameter_micron": 10.3,
        "Numerical_Aperture": 0.14,
        "Attenuation_dB_km": 0.19,
        "V_Number": 2.3836,
        "Relative_Delta_percent": 0.3673,
    },
]
