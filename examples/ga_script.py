import pandas as pd
import matplotlib.pyplot as plt
import logging
import os

from rsoft_cad.constants import SINGLE_MODE_FIBERS
from rsoft_cad import configure_logging
from rsoft_cad.utils import get_next_run_folder
from rsoft_cad.optimisation import genetic_algorithm

data_dir = "output"
expt_dir = get_next_run_folder(data_dir, "ga_run_")
log_filename = f"{expt_dir}.log"

configure_logging(
    log_file=os.path.join(data_dir, expt_dir, log_filename),
    log_level=logging.DEBUG,
)

num_fibers = 6
num_fiber_types = len(SINGLE_MODE_FIBERS)
population_size = 50
num_generations = 100
mutation_rate = 0.01
crossover_rate = 0.8
num_parents = 20

best_individual, best_fitness = genetic_algorithm(
    population_size=population_size,
    num_fibers=num_fibers,
    num_fiber_types=num_fiber_types,
    num_generations=num_generations,
    mutation_rate=mutation_rate,
    crossover_rate=crossover_rate,
    num_parents=num_parents,
    data_dir=data_dir,  # Pass data_dir
    expt_dir=expt_dir,
    highest_mode="LP02",
    mode_output="OUTPUT_REAL_IMAG",
    final_capillary_id=40,  # micron
)

print("\n--- Final Results ---")
print(f"Best fiber indices: {best_individual}")
print(f"Best overlap: {best_fitness:.6f}")
