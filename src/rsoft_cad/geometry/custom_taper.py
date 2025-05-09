import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

from rsoft_cad.layout import multilayer_lantern_layout
from rsoft_cad.utils import lantern_layout


def sigmoid(x, center, width, amplitude=1):
    return amplitude / (1 + np.exp(-(x - center) / width))


def sigmoid_taper_ratio(
    z,
    taper_length,
    center1_ratio=0.33,  # Position parameters (relative to taper_length)
    center2_ratio=0.5,
    center3_ratio=0.67,
    width1_ratio=1 / 6,  # Width parameters (relative to taper_length)
    width2_ratio=1 / 10,
    width3_ratio=1 / 6,
    weight1=0.1,  # Weight parameters for combining sigmoids
    weight2=0.8,
    weight3=0.1,
    min_value=0,  # Output range parameters
    max_value=1,
):
    """
    Creates a realistic taper ratio using a weighted combination of three sigmoid functions.

    Parameters:
    -----------
    z : array-like
        Position values along the taper
    taper_length : float
        Total length of the taper
    center1_ratio, center2_ratio, center3_ratio : float
        Relative positions of sigmoid centers (as fraction of taper_length)
    width1_ratio, width2_ratio, width3_ratio : float
        Relative widths of sigmoids (as fraction of taper_length)
    weight1, weight2, weight3 : float
        Weights for combining the sigmoid functions (should sum to 1)
    min_value, max_value : float
        Range for clipping the output values

    Returns:
    --------
    array-like
        Taper ratio values
    """
    # Calculate actual centers and widths
    center1 = taper_length * center1_ratio
    center2 = taper_length * center2_ratio
    center3 = taper_length * center3_ratio

    width1 = taper_length * width1_ratio
    width2 = taper_length * width2_ratio
    width3 = taper_length * width3_ratio

    # Calculate the three sigmoid components
    s1 = sigmoid(z, center1, width1)
    s2 = sigmoid(z, center2, width2)
    s3 = sigmoid(z, center3, width3)

    # Combine using weights
    taper = weight1 * s1 + weight2 * s2 + weight3 * s3

    # Clip to desired range
    return np.clip(taper, min_value, max_value)


def model_photonic_lantern_taper(
    z_points=100,
    taper_length=21.5,
    initial_diameter=125,
    final_core_diameter=32,
    capillary_id=275,
    capillary_od=900,
    layers_config=[(3, 1.0)],
):
    z = np.linspace(0, taper_length, z_points)
    taper_ratio = sigmoid_taper_ratio(z, taper_length)
    num_fibers = sum(n for n, _ in layers_config)
    final_capillary_id = (
        final_core_diameter * (1 + 2 / np.sqrt(num_fibers))
        if num_fibers > 1
        else final_core_diameter * 3
    )
    capillary_inner = (
        capillary_id * (1 - taper_ratio) + final_capillary_id * taper_ratio
    )
    capillary_outer = (
        capillary_od * (1 - taper_ratio)
        + (capillary_inner / capillary_id) * capillary_od * taper_ratio
    )
    initial_fiber_centres_layers, _ = multilayer_lantern_layout(
        initial_diameter, layers_config
    )
    initial_positions = np.concatenate(
        [np.array(layer) for layer in initial_fiber_centres_layers]
    )
    fiber_diameters = np.zeros((z_points, num_fibers))
    fiber_positions = np.zeros((z_points, num_fibers, 2))

    for i in range(z_points):
        current_taper = taper_ratio[i]
        current_capillary_inner = capillary_inner[i]
        fiber_diameter = (
            initial_diameter * (1 - current_taper) + final_core_diameter * current_taper
        )
        fiber_diameters[i, :] = fiber_diameter
        initial_available_radius = capillary_id / 2 - initial_diameter / 2
        current_available_radius = current_capillary_inner / 2 - fiber_diameter / 2
        if initial_available_radius > 0:
            scale_factor = current_available_radius / initial_available_radius
            fiber_positions[i, :, :] = initial_positions * scale_factor
        else:
            fiber_positions[i, :, :] = np.zeros_like(initial_positions)

    return {
        "z": z,
        "fiber_diameters": fiber_diameters,
        "fiber_positions": fiber_positions,
        "capillary_inner_diameter": capillary_inner,
        "capillary_outer_diameter": capillary_outer,
    }


def plot_taper_cross_sections(model, ax_row, num_sections=6):
    z = model["z"]
    fiber_diameters = model["fiber_diameters"]
    fiber_positions = model["fiber_positions"]
    capillary_inner = model["capillary_inner_diameter"]
    num_fibers = fiber_positions.shape[1]

    indices = np.linspace(0, len(z) - 1, num_sections, dtype=int)

    for i, idx in enumerate(indices):
        ax = ax_row[i]
        circle = plt.Circle((0, 0), capillary_inner[idx] / 2, fill=False, color="gray")
        ax.add_artist(circle)

        for j in range(num_fibers):
            fiber_x, fiber_y = fiber_positions[idx, j]
            fiber_circle = plt.Circle(
                (fiber_x, fiber_y),
                fiber_diameters[idx, j] / 2,
                color="orange",
                alpha=0.7,
            )
            ax.add_artist(fiber_circle)

        max_radius = capillary_inner[0] / 2 * 1.1
        ax.set_xlim(-max_radius, max_radius)
        ax.set_ylim(-max_radius, max_radius)
        ax.set_aspect("equal")
        ax.set_title(f"z = {z[idx]:.1f} mm", fontsize=8)
        ax.set_xticks([])
        ax.set_yticks([])


def plot_taper_profile(model, ax):
    z = model["z"]
    capillary_inner = model["capillary_inner_diameter"]
    capillary_outer = model["capillary_outer_diameter"]
    fiber_diameters = model["fiber_diameters"]
    num_fibers = fiber_diameters.shape[1]

    ax.plot(
        z,
        capillary_outer,
        color="lightgray",
        linestyle="-",
        label="Capillary Outer Diameter",
    )
    ax.plot(
        z,
        capillary_inner,
        color="gray",
        linestyle="-",
        label="Capillary Inner Diameter",
    )

    for i in range(num_fibers):
        ax.plot(
            z,
            fiber_diameters[:, i],
            color=f"C{i}",
            linestyle="--",
            linewidth=0.7,
            label=f"Fiber {i+1} Diameter" if i == 0 else "",
        )

    ax.set_xlabel("z position (mm)")
    ax.set_ylabel("Diameter (μm)")
    ax.set_title("Longitudinal Profile")
    ax.legend(fontsize=8)
    ax.grid(True)


def plot_combined_taper(model, num_cross_sections=6, figsize=(15, 6)):
    """
    Generates a figure with cross-sections and the longitudinal profile of the taper.

    Args:
        model (dict): The dictionary returned by the model_photonic_lantern_taper function.
        num_cross_sections (int, optional): The number of cross-sections to plot. Defaults to 6.
        figsize (tuple, optional): The size of the figure (width, height) in inches. Defaults to (15, 6).
    """
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(2, num_cross_sections, height_ratios=[1, 1])

    # Plot cross-sections on the top row
    ax_cross = [fig.add_subplot(gs[0, i]) for i in range(num_cross_sections)]
    plot_taper_cross_sections(
        model,
        ax_cross,
        num_sections=num_cross_sections,
    )

    # Plot the longitudinal profile on the bottom row, spanning all columns
    ax_profile = fig.add_subplot(gs[1, :])
    plot_taper_profile(model, ax_profile)

    plt.tight_layout()
    return fig


if __name__ == "__main__":
    """7 cores configuration"""
    layers_config_7_fibers = [(1, 0), (5, 2)]
    core_map_7_fibers = model_photonic_lantern_taper(
        z_points=200,
        taper_length=50,
        initial_diameter=125,
        final_core_diameter=40,
        capillary_id=375,
        capillary_od=900,
        layers_config=layers_config_7_fibers,
    )

    # Plot the combined figure for the 7-fiber case
    fig_combined_7 = plot_combined_taper(core_map_7_fibers)

    """ 3 cores configuration """
    layers_config_3_fibers = [(3, 1.0)]
    core_map_3_fibers = model_photonic_lantern_taper(
        z_points=200,
        taper_length=50,
        initial_diameter=125,
        final_core_diameter=20,
        capillary_id=275,
        capillary_od=900,
        layers_config=layers_config_3_fibers,
    )

    # Plot the combined figure for the 3-fiber case
    fig_combined_3 = plot_combined_taper(core_map_3_fibers)

    """ Plot taper ratio along normalised length """
    fig_taper, ax_taper = plt.subplots(1, 1, figsize=(15, 6))
    z = np.linspace(0, 1, 100)
    taper_ratio = 1 - sigmoid_taper_ratio(z, taper_length=1)
    ax_taper.plot(z, taper_ratio)
    ax_taper.grid(True)
    ax_taper.set_xlabel("Normalised z-dir")
    ax_taper.set_ylabel("Taper ratio (arb units)")
    ax_taper.set_title("Taper Ratio Profile")

    plt.show()
