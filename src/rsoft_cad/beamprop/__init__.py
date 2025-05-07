"""
BeamPROP simulation module for RSoft CAD package.

This package provides utilities for simulating and analyzing optical
beam propagation in photonic devices, particularly for tapered lantern structures.
It includes functions for parameter scanning and visualization of simulation results.
"""

from .beamprop_param_scan import beamprop_tapered_lantern
from .beamprop_plot_util import plot_combined_monitor_files
