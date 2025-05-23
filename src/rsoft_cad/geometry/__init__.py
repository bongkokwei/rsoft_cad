"""
This package calculates the geometry of a taper
"""

from .tapers import calculate_taper_properties
from .custom_taper import (
    sigmoid_taper_ratio,
    plot_combined_taper,
    model_photonic_lantern_taper,
    extract_lantern_endpoints,
    create_custom_taper_profile,
)
