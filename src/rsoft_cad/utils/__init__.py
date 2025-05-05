# src/rsoft_cad/utils/__init__.py
"""
RSoft CAD Utilities
==================

This package provides utilities for working with RSoft CAD files,
creating and manipulating photonic lantern layouts, and visualizing data.
"""

# Import lantern layout functions
from .lantern.circular import lantern_layout, find_scale_factor
from .lantern.hexagonal import hexagonal_fiber_layout, calculate_capillary_diameter

# Import visualization functions
from .lantern.visualization import (
    visualise_lantern,
    visualise_lp_lantern,
    plot_hexagonal_fibers,
)
from .visualisation.field_plots import plot_field_data
from .visualisation.monitor_plots import plot_mon_data

# Import I/O functions
from .io.readers import read_field_data, read_mon_file, read_nef_file
from .io.finders import find_files_by_extension, find_fld_files, find_mon_files
from .io.filesystem import get_next_run_folder, copy_files_to_destination

# Import config functions
from .config.modifier import load_config, save_config, modify_parameter

# Version information
__version__ = "0.1.0"
