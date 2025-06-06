import pandas as pd

from rsoft_cad.optimisation import (
    build_and_simulate_lantern,
    build_parameterised_lantern,
)
from rsoft_cad.constants import SINGLE_MODE_FIBERS
from rsoft_cad.optimisation.utils import get_fiber_type_list_by_indices
from rsoft_cad.utils import get_next_run_folder, visualise_modes

data_dir = "output"
expt_dir = get_next_run_folder("output", "best_config_run_")
fiber_indices = [1, 2, 2, 9, 9, 8, 0, 0]

build_and_simulate_lantern(
    fiber_indices=fiber_indices,
    taper_file_name="custom_taper.dat",
    run_name="manual_config",
    expt_dir=expt_dir,
    data_dir=data_dir,
    save_folder="rsoft_data_files",
    highest_mode="LP31",
    launch_mode="LP01",
    taper_length=50000,
    femnev=int(2 * len(fiber_indices)),
    num_grid=200,
    final_capillary_id=12,
    manual_mode=True,
    domain_min=50000,
)

# Sort the original list by core diameter
smf_df = pd.DataFrame(SINGLE_MODE_FIBERS)
fiber_types = get_fiber_type_list_by_indices(smf_df, fiber_indices)
print(f"Selected fiber types: {fiber_types}")

output_file = visualise_modes(
    folder_name=expt_dir,
    num_modes=16,
    nrow=4,
    ncol=4,
    figsize=(10, 10),
    show_plot=True,
    cleanup_files=True,
)


"""
Select fibers from biggest to smallest:
    [
        "1. LEAF", 9.6
        "2. OS2", 8.5
        "9. Allwave", 8.4
        "8. SMF-28e+", 8.3
        "0. SMF-28", 8.2
        "6. G.657.A2", 8.0
        "5. G.655", 7.8
        "3. TrueWave RS", 7.5
        G652D 8.3
        7.IDF 6.0
    ]
"""
