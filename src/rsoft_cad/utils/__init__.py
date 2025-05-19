# src/rsoft_cad/utils/__init__.py
"""
RSoft CAD Utilities
==================

This package provides utilities for working with RSoft CAD files,
creating and manipulating photonic lantern layouts, and visualizing data.
"""
from .lp_modes import generate_lp_mode

from .mode_utils import (
    get_modes_below_cutoff,
    group_modes_by_radial_number,
    find_segment_by_comp_name,
    interpolate_taper_value,
)

# Import lantern layout functions
from .fiber_layout.circular import lantern_layout, find_scale_factor
from .fiber_layout.hexagonal import hexagonal_fiber_layout, calculate_capillary_diameter

# Import visualisation functions
from .fiber_layout.visualise_layout import (
    visualise_lantern,
    visualise_lp_lantern,
    plot_hexagonal_fibers,
)
from .rsoft_file_plot.field_plots import plot_field_data
from .rsoft_file_plot.monitor_plots import plot_mon_data

# Import I/O functions
from .rsoft_file_io.readers import (
    read_field_data,
    read_mon_file,
    read_nef_file,
)

from .rsoft_file_io.finders import (
    find_files_by_extension,
    find_fld_files,
    find_mon_files,
)

from .rsoft_file_io.writers import write_femsim_field_data
from .rsoft_file_io.write_lp_modes_to_rsoft import generate_and_write_lp_modes

from .rsoft_file_io.filesystem import (
    get_next_run_folder,
    copy_files_to_destination,
    copy_files_by_extension,
)


# Import config functions
from .config.modifier import (
    load_config,
    save_config,
    modify_parameter,
)


# Version information
__version__ = "0.1.0"
