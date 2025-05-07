import matplotlib.pyplot as plt
import numpy as np


def plot_mon_data(
    header_info,
    data_df,
    monitors_to_plot=None,
    figsize=(10, 6),
    title="Monitor Data",
):
    """
    Plot data from a .mon file.

    Parameters:
    file_path (str): Path to the .mon file
    monitors_to_plot (list, optional): List of monitor indices to plot.
    If None, all non-zero monitors are plotted.
    figsize (tuple, optional): Figure size (width, height) in inches. Default is (12, 8).
    title (str, optional): Plot title. Default is "Monitor Data".

    Returns:
    matplotlib.figure.Figure: The generated figure
    """
    # Create a figure
    fig, ax = plt.subplots(figsize=figsize)

    # Determine which monitors to plot
    if monitors_to_plot is None:
        # Find monitors with non-zero data (skip the z column)
        non_zero_columns = []
        for col in data_df.columns[1:]:
            if data_df[col].abs().sum() > 0:
                non_zero_columns.append(col)
        monitors_to_plot = non_zero_columns
    else:
        # Convert monitor indices to column names
        monitors_to_plot = [f"monitor_{i}" for i in monitors_to_plot]

    # Plot each monitor's data
    for col in monitors_to_plot:
        monitor_idx = int(col.split("_")[1])
        monitor_type = (
            header_info["monitor_types"][monitor_idx - 1]
            if monitor_idx <= len(header_info["monitor_types"])
            else "Unknown"
        )
        label = f"{col} ({monitor_type})"
        ax.plot(data_df["z"], data_df[col], label=label)

    # Add labels and title
    ax.set_xlabel("Z Position")
    ax.set_ylabel("Monitor Value")
    ax.set_title(title)
    ax.grid(True)
    ax.legend()

    plt.tight_layout()
    return fig
