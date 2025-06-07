from rsoft_cad.utils.rsoft_file_io.readers import read_field_data
from rsoft_cad.optimisation.cost_function import delete_files_except
import matplotlib.pyplot as plt
import numpy as np
import os


def visualise_modes(
    folder_name,
    data_dir="output",
    save_folder="rsoft_data_files",
    file_prefix="manual_config",
    num_modes=20,
    nrow=4,
    ncol=5,
    figsize=(12, 10),
    dpi=300,
    show_plot=True,
    cleanup_files=True,
    files_to_keep=None,
):
    """
    Visualise electromagnetic modes in a grid layout.

    Parameters:
    -----------
    folder_name : str
        Name of the folder containing the mode data
    num_modes : int, default=20
        Number of modes to visualise
    nrow : int, default=4
        Number of rows in the subplot grid
    ncol : int, default=5
        Number of columns in the subplot grid
    figsize : tuple, default=(12, 10)
        Figure size as (width, height)
    dpi : int, default=300
        Resolution for saved figure
    show_plot : bool, default=True
        Whether to display the plot
    cleanup_files : bool, default=True
        Whether to clean up files after plotting
    files_to_keep : list, default=None
        List of files to keep during cleanup. If None, keeps default files.

    Returns:
    --------
    str
        Path to the saved figure file
    """

    # Set default files to keep if not specified
    if files_to_keep is None:
        files_to_keep = ["custom_taper.dat", "combined_plot.png"]

    # Configure matplotlib styling
    plt.style.use("dark_background")
    plt.rcParams.update(
        {
            "figure.facecolor": "#2E2E2E",
            "axes.facecolor": "#2E2E2E",
            "savefig.facecolor": "#2E2E2E",
            "axes.edgecolor": "white",
            "axes.labelcolor": "white",
            "text.color": "white",
            "xtick.color": "white",
            "ytick.color": "white",
            "grid.color": "#404040",
            "axes.grid": False,
            "grid.alpha": 0.7,
            "xtick.labelbottom": False,
        }
    )

    # Create figure with subplots
    fig, axes = plt.subplots(nrows=nrow, ncols=ncol, figsize=figsize)
    fig.patch.set_facecolor("#2E2E2E")

    # Flatten the axes array for easier iteration
    axes_flat = axes.flatten()

    # Process each mode
    for i in range(num_modes):
        filename = os.path.join(
            data_dir,
            folder_name,
            save_folder,
            f"{file_prefix}_ex.m{i:02d}",
        )

        try:
            # Read the data
            data_dict = read_field_data(filename)

            # Extract the complex data matrix
            complex_data = data_dict["complex_data"]

            # Calculate magnitude
            magnitude_data = np.abs(complex_data)

            # Get spatial coordinates
            xmin, xmax = data_dict["xmin"], data_dict["xmax"]
            ymin, ymax = data_dict["ymin"], data_dict["ymax"]

            # Plot on the corresponding subplot
            ax = axes_flat[i]

            # Create the plot
            im = ax.imshow(
                magnitude_data,
                cmap="viridis",
                aspect="equal",
                extent=[xmin, xmax, ymin, ymax],
                origin="lower",
            )

            # Set title
            ax.set_title(f"Mode {i:02d}", color="white", fontsize=12)

            # Remove ticks for cleaner look
            ax.set_xticks([])
            ax.set_yticks([])

        except Exception as e:
            # Handle missing files or errors
            ax = axes_flat[i]
            ax.text(
                0.5,
                0.5,
                f"Error\nMode {i:02d}\n{str(e)[:20]}...",
                ha="center",
                va="center",
                transform=ax.transAxes,
                color="white",
                fontsize=10,
            )
            ax.set_facecolor("#2E2E2E")

    # Adjust spacing between subplots
    plt.tight_layout(pad=1.5)

    # Define output path
    figure_filename = os.path.join(
        "output",
        folder_name,
        "rsoft_data_files",
        "combined_plot.png",
    )

    # Save the entire grid
    plt.savefig(
        figure_filename,
        dpi=dpi,
        bbox_inches="tight",
        facecolor="none",
        edgecolor="none",
        transparent=True,
    )

    # Show plot if requested
    if show_plot:
        plt.show()

    # Clean up files if requested
    if cleanup_files:
        delete_files_except(
            folder_path=os.path.join("output", folder_name, "rsoft_data_files"),
            match_string=None,
            files_to_keep=files_to_keep,
        )

    return figure_filename


# Example usage:
if __name__ == "__main__":
    # Use with default parameters
    # output_file = visualise_modes("best_config_run_003")

    # Or customise parameters
    output_file = visualise_modes(
        folder_name="best_config_run_010",
        num_modes=16,
        nrow=4,
        ncol=4,
        figsize=(10, 10),
        show_plot=True,
        cleanup_files=True,
    )
