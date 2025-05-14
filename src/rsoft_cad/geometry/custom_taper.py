import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import os

from rsoft_cad.layout import multilayer_lantern_layout


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
    cladding_diameter=125,  # Renamed from initial_diameter
    final_cladding_diameter=None,  # Renamed from final_core_diameter and made optional
    final_capillary_id=150,  # Required parameter for specifying final structure
    capillary_id=275,
    capillary_od=900,
    layers_config=[(3, 1.0)],
    core_map=None,  # New parameter for LP mode mapping
    core_diameters=None,  # New parameter for core diameters
):
    """
    Models a photonic lantern taper with support for LP mode mapping and core diameters.

    This function extends model_photonic_lantern_taper by adding support for mapping
    LP modes to fiber positions through the core_map parameter and tracking core diameters
    along the taper. It renames parameters for clarity and calculates final_cladding_diameter
    from final_capillary_id if not provided.

    Parameters:
    -----------
    z_points : int, optional
        Number of points along the z-axis. Default is 100.
    taper_length : float, optional
        Length of the taper in mm. Default is 21.5.
    cladding_diameter : float, optional
        Initial diameter of the fiber cladding in μm. Default is 125.
    final_cladding_diameter : float, optional
        Final diameter of the fiber claddings in μm. If None, calculated from final_capillary_id.
    final_capillary_id : float, optional
        Final inner diameter of the capillary in μm. Default is 150.
    capillary_id : float, optional
        Initial inner diameter of the capillary in μm. Default is 275.
    capillary_od : float, optional
        Outer diameter of the capillary in μm. Default is 900.
    layers_config : list of tuples, optional
        Configuration for fiber layers if core_map is not provided. Default is [(3, 1.0)].
    core_map : dict, optional
        Mapping of LP mode names to initial fiber positions. If provided, overrides layers_config.
        Example: {"LP01": (0, 0), "LP11a": (100, 0), "LP11b": (0, 100)}
    core_diameters : dict, optional
        Dictionary mapping LP mode names to their initial core diameters in μm.
        Example: {"LP01": 10.7, "LP11a": 9.6, "LP11b": 9.6}
        If not provided, all cores default to 80% of the cladding diameter.

    Returns:
    --------
    dict
        A dictionary containing the taper model data with the following keys:
        - "z": z-positions along the taper
        - "fiber_diameters": Array of fiber (cladding) diameters at each z-position
        - "core_diameters": Array of core diameters at each z-position
        - "fiber_positions": Array of fiber positions at each z-position
        - "capillary_inner_diameter": Inner diameter of the capillary at each z-position
        - "capillary_outer_diameter": Outer diameter of the capillary at each z-position
        - "lp_modes": List of LP mode names
        - "mode_positions": Dictionary mapping LP mode names to their positions along z
        - "mode_core_diameters": Dictionary mapping LP mode names to their core diameters along z
    """
    z = np.linspace(0, taper_length, z_points, endpoint=True)
    taper_ratio = sigmoid_taper_ratio(z, taper_length)

    # Determine number of fibers and initial positions
    if core_map is not None:
        num_fibers = len(core_map)
        # Extract positions from core_map and create initial_positions array
        lp_modes = list(core_map.keys())
        initial_positions = np.array([core_map[mode] for mode in lp_modes])
    else:
        # Fall back to using layers_config if no core_map is provided
        num_fibers = sum(n for n, _ in layers_config)
        initial_fiber_centres_layers, _ = multilayer_lantern_layout(
            cladding_diameter, layers_config
        )
        initial_positions = np.concatenate(
            [np.array(layer) for layer in initial_fiber_centres_layers]
        )
        lp_modes = [f"Fiber_{i+1}" for i in range(num_fibers)]

    # Calculate final_cladding_diameter if not provided
    if final_cladding_diameter is None:
        # Calculate an appropriate final_cladding_diameter based on final_capillary_id
        # This ensures the fibers fit well in the final capillary
        if num_fibers > 1:
            # Consider packing density for multiple fibers
            final_cladding_diameter = final_capillary_id / (1 + 2 / np.sqrt(num_fibers))
        else:
            # For a single fiber, use a conservative ratio
            final_cladding_diameter = final_capillary_id / 3

    # Calculate capillary dimensions along the taper
    capillary_inner = (
        capillary_id * (1 - taper_ratio) + final_capillary_id * taper_ratio
    )
    capillary_outer = (
        capillary_od * (1 - taper_ratio)
        + (capillary_inner / capillary_id) * capillary_od * taper_ratio
    )

    # Create arrays for fiber diameters, core diameters, and positions
    fiber_diameters = np.zeros((z_points, num_fibers))
    fiber_positions = np.zeros((z_points, num_fibers, 2))
    core_diameters_array = np.zeros((z_points, num_fibers))

    # Set default core diameters if not provided or for missing modes
    if core_diameters is None:
        core_diameters = {}

    # Default core diameter is 80% of cladding diameter
    default_core_ratio = 0.8

    # Calculate fiber diameters, core diameters, and positions along the taper
    for i in range(z_points):
        current_taper = taper_ratio[i]
        current_capillary_inner = capillary_inner[i]

        # Calculate current cladding diameter for all fibers
        current_cladding_diameter = (
            cladding_diameter * (1 - current_taper)
            + final_cladding_diameter * current_taper
        )
        fiber_diameters[i, :] = current_cladding_diameter

        # Calculate core diameters - scale with the same taper ratio
        for j, mode in enumerate(lp_modes):
            # Get initial core diameter for this mode, default to 80% of cladding if not specified
            initial_core_diam = core_diameters.get(
                mode, cladding_diameter * default_core_ratio
            )

            # Calculate final core diameter maintaining the same core-to-cladding ratio
            core_to_cladding_ratio = initial_core_diam / cladding_diameter
            final_core_diam = final_cladding_diameter * core_to_cladding_ratio

            # Interpolate between initial and final core diameters using taper ratio
            current_core_diam = (
                initial_core_diam * (1 - current_taper)
                + final_core_diam * current_taper
            )
            core_diameters_array[i, j] = current_core_diam

        # Calculate fiber positions
        initial_available_radius = capillary_id / 2 - cladding_diameter / 2
        current_available_radius = (
            current_capillary_inner / 2 - current_cladding_diameter / 2
        )

        if initial_available_radius > 0:
            scale_factor = current_available_radius / initial_available_radius
            fiber_positions[i, :, :] = initial_positions * scale_factor
        else:
            fiber_positions[i, :, :] = np.zeros_like(initial_positions)

    # Create a mode map for positions over z
    mode_positions = {lp_modes[i]: fiber_positions[:, i, :] for i in range(num_fibers)}

    # Create a mode map for core diameters over z
    mode_core_diameters = {
        lp_modes[i]: core_diameters_array[:, i] for i in range(num_fibers)
    }

    # Return the model data
    return {
        "z": z,
        "fiber_diameters": fiber_diameters,
        "core_diameters": core_diameters_array,
        "fiber_positions": fiber_positions,
        "capillary_inner_diameter": capillary_inner,
        "capillary_outer_diameter": capillary_outer,
        "lp_modes": lp_modes,
        "mode_positions": mode_positions,
        "mode_core_diameters": mode_core_diameters,
    }


def extract_lantern_endpoints(model_output):
    """
    Extract endpoint information for the photonic lantern taper model, including
    cladding, core, and capillary dimensions.

    Parameters:
    -----------
    model_output : dict
        The dictionary returned by model_photonic_lantern_taper function

    Returns:
    --------
    tuple
        A tuple of three dictionaries (cladding_endpoints, core_endpoints, cap_endpoints):
        - cladding_endpoints and core_endpoints contain LP mode information
        - cap_endpoints contains capillary information with just width and height

        Format:
        {
            "LP01": {
                "end.x": x_position,
                "end.y": y_position,
                "end.z": z_position,
                "end.height": diameter,
                "end.width": diameter
            },
            ...
        }

        cap_endpoints format:
        {
            "end.z": z_position,
            "end.height": inner_diameter,
            "end.width": inner_diameter
        }
    """
    # Extract required data from the model output
    z = model_output["z"]
    fiber_diameters = model_output["fiber_diameters"]  # Cladding diameters
    lp_modes = model_output["lp_modes"]
    mode_positions = model_output["mode_positions"]
    mode_core_diameters = model_output["mode_core_diameters"]
    capillary_inner_diameter = model_output["capillary_inner_diameter"]

    # Get index of the end of the taper
    end_idx = len(z) - 1
    end_z = z[end_idx]

    # Initialize the result dictionaries
    cladding_endpoints = {}
    core_endpoints = {}

    # For each LP mode, extract the endpoint information
    for i, mode in enumerate(lp_modes):
        # Get the final position
        if mode in mode_positions:
            # If we have mode_positions dictionary, use it directly
            end_pos = mode_positions[mode][end_idx]
            end_x, end_y = end_pos
        else:
            # Fall back to the fiber_positions array
            end_x = model_output["fiber_positions"][end_idx, i, 0]
            end_y = model_output["fiber_positions"][end_idx, i, 1]

        # Get the final cladding diameter
        end_cladding_diameter = fiber_diameters[end_idx, i]

        # Get the final core diameter from the new mode_core_diameters dictionary
        if mode in mode_core_diameters:
            end_core_diameter = mode_core_diameters[mode][end_idx]
        else:
            # Use the core_diameters array as fallback if the dictionary access fails
            end_core_diameter = model_output["core_diameters"][end_idx, i]

        # Create the cladding entry for this mode
        cladding_endpoints[mode] = {
            "end.x": float(end_x),
            "end.y": float(end_y),
            "end.z": float(end_z),
            "end.height": float(end_cladding_diameter),
            "end.width": float(end_cladding_diameter),
        }

        # Create the core entry for this mode
        core_endpoints[mode] = {
            "end.x": float(end_x),
            "end.y": float(end_y),
            "end.z": float(end_z),
            "end.height": float(end_core_diameter),
            "end.width": float(end_core_diameter),
        }

    # Create the capillary endpoints dictionary
    # Since the capillary is centered by definition, we only need height and width
    cap_endpoints = {
        "end.z": float(end_z),
        "end.height": float(capillary_inner_diameter[end_idx]),
        "end.width": float(capillary_inner_diameter[end_idx]),
    }

    return cladding_endpoints, core_endpoints, cap_endpoints


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
        final_core_diameter=20,
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


def create_custom_taper_profile(
    data_dir,
    expt_dir,
    taper_func=None,
    file_name="custom_profile_dim.txt",
    num_points=300,
    taper_length=1,
    z_range=(0, 1),
    header="/rn,a,b /nx0 100 0 1 1 OUTPUT_REAL\n ",
    save_to_rsoft_data=True,
    rsoft_data_dir=None,
    **taper_func_kwargs,
):
    """
    Create a custom taper profile using sigmoid function and save to file(s).

    Parameters:
    -----------
    data_dir : str
        Base directory for data
    expt_dir : str
        Experiment directory name
    taper_func : callable, optional
        Function to generate the taper profile. Should accept a numpy array of z values
        as first argument and return a numpy array of taper ratios.
        If None (default), will use sigmoid_taper_ratio.
    file_name : str, optional
        Name of the output file, default is "custom_profile_dim.txt"
    num_points : int, optional
        Number of points in the profile, default is 300
    taper_length : float, optional
        Length parameter for the sigmoid taper ratio, default is 1
    z_range : tuple, optional
        Range of z values (start, end), default is (0, 1)
    header : str, optional
        Header text for the output file
    save_to_rsoft_data : bool, optional
        Whether to also save to rsoft_data_files subdirectory, default is True
    rsoft_data_dir:
        Data directory name.
    **taper_func_kwargs :
        Additional keyword arguments to pass to the taper function

    Returns:
    --------
    tuple
        (z, taper_ratios) arrays
    """
    # Create z array
    z = np.linspace(z_range[0], z_range[1], num_points)

    # Calculate taper ratios
    # Calculate taper ratios using the provided function or default
    if taper_func is None:
        # Use sigmoid_taper_ratio as default
        taper_ratios = sigmoid_taper_ratio(
            z, taper_length=taper_length, **taper_func_kwargs
        )
    else:
        # Use the custom function provided
        taper_ratios = taper_func(z, **taper_func_kwargs)
    # Prepare save location
    save_to = os.path.join(data_dir, expt_dir)

    # Save to main directory
    np.savetxt(
        os.path.join(save_to, file_name),
        np.column_stack((z, taper_ratios)),
        delimiter="\t",
        header=header,
        comments="",
    )

    # Optionally save to rsoft_data_files subdirectory
    if save_to_rsoft_data:
        rsoft_dir = os.path.join(save_to, rsoft_data_dir)
        # Create directory if it doesn't exist
        os.makedirs(rsoft_dir, exist_ok=True)
        np.savetxt(
            os.path.join(rsoft_dir, file_name),
            np.column_stack((z, taper_ratios)),
            delimiter="\t",
            header=header,
            comments="",
        )

    return z, taper_ratios
