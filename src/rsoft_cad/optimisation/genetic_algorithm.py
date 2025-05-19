import pandas as pd
import matplotlib.pyplot as plt
import logging
import os
import random
from typing import List, Tuple

from rsoft_cad.constants import SINGLE_MODE_FIBERS
from rsoft_cad import configure_logging
from rsoft_cad.utils import get_next_run_folder
from rsoft_cad.optimisation.utils import build_and_simulate_lantern
from rsoft_cad.utils import generate_and_write_lp_modes


def create_initial_population(
    population_size: int, num_fibers: int, num_fiber_types: int
) -> List[List[int]]:
    """
    Create an initial population of random fiber index combinations.

    Args:
        population_size: Number of individuals in the population.
        num_fibers: Number of fibers in the lantern.
        num_fiber_types: Total number of fiber types.

    Returns:
        A list of lists, where each inner list represents an individual
        (a combination of fiber indices).
    """
    population = []
    for _ in range(population_size):
        individual = [random.randint(0, num_fiber_types - 1) for _ in range(num_fibers)]
        population.append(individual)
    return population


def calculate_fitness(
    individual: List[int],
    highest_mode: str = "LP01",
    data_dir: str = "output",
    expt_dir: str = "ga_run_",
    taper_length: float = 50000,
    taper_factor: float = 1,
    taper_profile: str = None,  # Added taper_profile parameter
    taper_file_name: str = "custom_taper.dat",
    mode_output: str = "OUTPUT_REAL_IMAG",
    domain_min: float = 50000,
    final_capillary_id: float = 25,
) -> float:
    """
    Calculate the fitness (overlap) of an individual.

    Args:
        individual: A list of fiber indices.
        highest_mode: Mode order to simulate.
        data_dir: Data directory.
        expt_dir: Experiment directory.
        taper_length: Length of taper in microns.
        taper_factor: Tapering factor.
        taper_profile: Custom taper profile (None for default).
        mode_output: Mode output type.
        domain_min: Minimum domain size.

    Returns:
        The fitness value (overlap) of the individual.
    """
    run_name = f"eval_run_{''.join(map(str, individual))}"  # Create a unique run name
    overlap = build_and_simulate_lantern(
        fiber_indices=individual,
        taper_file_name=taper_file_name,
        highest_mode=highest_mode,
        run_name=run_name,
        data_dir=data_dir,
        expt_dir=expt_dir,
        taper_length=taper_length,
        taper_factor=taper_factor,
        mode_output=mode_output,
        domain_min=domain_min,
        final_capillary_id=final_capillary_id,
    )
    return overlap


def select_parents(
    population: List[List[int]], fitnesses: List[float], num_parents: int
) -> List[List[int]]:
    """
    Select parents for crossover using fitness-proportionate selection (roulette wheel).

    Args:
        population: The current population.
        fitnesses: List of fitness values for each individual.
        num_parents: Number of parents to select.

    Returns:
        A list of selected parent individuals.
    """
    total_fitness = sum(fitnesses)
    probabilities = [f / total_fitness for f in fitnesses]
    parents = []
    for _ in range(num_parents):
        # Use random.choices for weighted random selection
        selected_parents = random.choices(population, probabilities)
        parents.append(selected_parents[0])  # Append the selected parent
    return parents


def crossover(parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
    """
    Perform single-point crossover to generate two offspring.

    Args:
        parent1: The first parent.
        parent2: The second parent.

    Returns:
        A tuple containing the two offspring.
    """
    crossover_point = random.randint(
        1, len(parent1) - 1
    )  # Ensure at least one gene is exchanged
    offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
    offspring2 = parent2[:crossover_point] + parent1[crossover_point:]
    return offspring1, offspring2


def mutate(
    individual: List[int], mutation_rate: float, num_fiber_types: int
) -> List[int]:
    """
    Mutate an individual by randomly changing some of its genes.

    Args:
        individual: The individual to mutate.
        mutation_rate: The probability of mutating each gene (0 to 1).
        num_fiber_types: The number of possible fiber types.

    Returns:
        The mutated individual.
    """
    mutated_individual = []
    for gene in individual:
        if random.random() < mutation_rate:
            # Change the gene to a random fiber type
            mutated_gene = random.randint(0, num_fiber_types - 1)
            mutated_individual.append(mutated_gene)
        else:
            mutated_individual.append(gene)
    return mutated_individual


def genetic_algorithm(
    population_size: int,
    num_fibers: int,
    num_fiber_types: int,
    num_generations: int,
    mutation_rate: float,
    crossover_rate: float,
    num_parents: int,
    highest_mode: str = "LP01",
    data_dir: str = "output",
    expt_dir: str = "ga_run_",
    taper_length: float = 50000,
    taper_factor: float = 1,
    taper_profile: str = None,  # Added taper_profile parameter
    taper_file_name: str = "custom_taper.dat",
    mode_output: str = "OUTPUT_REAL_IMAG",
    domain_min: float = 50000,
    final_capillary_id: float = 25,
    num_grid: int = 200,
) -> Tuple[List[int], float]:
    """
    Perform a genetic algorithm to optimize fiber indices for maximum overlap.

    Args:
        population_size: Number of individuals in the population.
        num_fibers: Number of fibers in the lantern.
        num_fiber_types: Total number of fiber types.
        num_generations: Number of generations to evolve.
        mutation_rate: Probability of mutating a gene.
        crossover_rate: Probability of performing crossover.
        num_parents: Number of parents to select for crossover.
        highest_mode: Mode order to simulate.
        data_dir: Data directory.
        expt_dir: Experiment directory.
        taper_length: Length of taper in microns.
        taper_factor: Tapering factor.
        taper_profile: Custom taper profile (None for default).
        mode_output: Mode output type.
        domain_min: Minimum domain size.

    Returns:
        A tuple containing:
        - The best individual (list of fiber indices).
        - The fitness (overlap) of the best individual.
    """
    logger = logging.getLogger(__name__)
    population = create_initial_population(population_size, num_fibers, num_fiber_types)
    logger.info(f"Initialized population of size {population_size}")

    best_fitness = -1.0
    best_individual = []

    # Build ideal output
    ref_folder_name = "ideal_modes"
    ref_prefix = "ref_LP"

    lp_dir = os.path.join(data_dir, expt_dir, ref_folder_name)
    generate_and_write_lp_modes(
        mode_field_diam=final_capillary_id,
        highest_mode=highest_mode,
        num_grid_x=num_grid,
        num_grid_y=num_grid,
        output_dir=lp_dir,
        ref_prefix=ref_prefix,
    )

    for generation in range(num_generations):
        logger.info(f"--- Generation {generation + 1} ---")

        # 1. Evaluate Fitness
        fitnesses = [
            calculate_fitness(
                individual,
                highest_mode=highest_mode,
                data_dir=data_dir,
                expt_dir=expt_dir,
                taper_length=taper_length,
                taper_factor=taper_factor,
                taper_profile=taper_profile,
                taper_file_name=taper_file_name,
                mode_output=mode_output,
                domain_min=domain_min,
                final_capillary_id=final_capillary_id,
            )
            for individual in population
        ]
        logger.debug(f"  Fitnesses: {fitnesses}")

        # 2. Find Best Individual
        current_best_fitness = max(fitnesses)
        current_best_index = fitnesses.index(current_best_fitness)
        current_best_individual = population[current_best_index]

        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_individual = current_best_individual
            logger.info(
                f"  New best individual: {best_individual} with overlap: {best_fitness:.6f}"
            )
        else:
            logger.info(
                f"  Best individual from previous generation:  {best_individual} with overlap: {best_fitness:.6f}"
            )

        # 3. Selection
        parents = select_parents(population, fitnesses, num_parents)
        logger.debug(f"  Selected {len(parents)} parents")

        # 4. Crossover
        offspring = []
        for i in range(0, len(parents) - 1, 2):  # Pair up parents
            if random.random() < crossover_rate:
                child1, child2 = crossover(parents[i], parents[i + 1])
                offspring.extend([child1, child2])
                logger.debug(f"  Crossover between parents {i} and {i+1}")
            else:
                offspring.extend(
                    [parents[i], parents[i + 1]]
                )  # If no crossover, keep parents
                logger.debug(f"  No crossover between parents {i} and {i+1}")
        # If odd number of parents, add the last parent to offspring
        if len(parents) % 2 != 0:
            offspring.append(parents[-1])

        # 5. Mutation
        mutated_offspring = [
            mutate(child, mutation_rate, num_fiber_types) for child in offspring
        ]
        logger.debug(f"  Mutated {len(mutated_offspring)} offspring")

        # 6. Replacement (replace entire population with new offspring)
        population = mutated_offspring

    logger.info("\n--- Genetic Algorithm Results ---")
    logger.info(f"Best individual: {best_individual}")
    logger.info(f"Best overlap: {best_fitness:.6f}")
    return best_individual, best_fitness


if __name__ == "__main__":
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
