from rsoft_cad.utils import find_mon_files, read_mon_file
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import argparse


def plot_combined_monitor_files(data_dir):
    """
    Plot and analyze taper length data from monitor files.

    Parameters:
    -----------
    data_dir : str
        Directory containing the monitor files

    Returns:
    --------
    fig : matplotlib.figure.Figure
        The created figure object
    ax : matplotlib.axes.Axes
        The created axes object
    combined_df : pandas.DataFrame
        Combined dataframe of all monitor data
    final_values : pandas.DataFrame
        Dataframe containing final values for each taper length
    summary : pandas.DataFrame
        Summary table of taper length analysis
    optimal_taper : float
        Optimal taper length value
    optimal_value : float
        Optimal monitor_7 value
    """
    # Find monitor files
    mon_list = find_mon_files(data_dir)

    # Create empty list to store dataframes
    all_dfs = []

    # Process each monitor file
    for i, mon in enumerate(mon_list):
        header, mon_df = read_mon_file(mon)
        mon_df["taper_length"] = mon_df["z"].iloc[-1]
        # Store the dataframe in the list
        all_dfs.append(mon_df)

    # Combine all dataframes into one
    combined_df = pd.concat(all_dfs, ignore_index=True)

    # 1. Get the final monitor_7 value for each taper_length
    final_values = combined_df.loc[combined_df.groupby("taper_length")["z"].idxmax()]

    # 2. Create a nicer visualization with more analysis
    fig, ax = plt.subplots(figsize=(14, 5))

    # Main scatter plot with connecting line
    sns.scatterplot(
        x="taper_length",
        y="monitor_7",
        data=final_values,
        s=100,
        alpha=0.7,
        ax=ax,
    )

    # Add polynomial trend line
    z = np.polyfit(final_values["taper_length"], final_values["monitor_7"], 10)
    p = np.poly1d(z)
    x_trend = np.linspace(
        final_values["taper_length"].min(), final_values["taper_length"].max(), 100
    )
    ax.plot(x_trend, p(x_trend), "--", color="red", alpha=0.7, label="Trend")

    # Enhance the plot
    ax.set_xlabel("Taper Length (μm)", fontsize=12)
    ax.set_ylabel("Normalised power", fontsize=12)
    ax.set_title("Transmission power vs Taper Length", fontsize=14)
    ax.grid(True, alpha=0.3)
    # ax.set_yscale("log")
    ax.legend()
    plt.tight_layout()

    # Summary table
    summary = pd.DataFrame(
        {
            "Taper Length": final_values["taper_length"],
            "Final Z Position": final_values["z"],
            "Final Monitor_7 Value": final_values["monitor_7"],
        }
    ).sort_values("Taper Length")

    # Find optimal taper length (assuming higher monitor_7 is better)
    optimal_idx = final_values["monitor_7"].idxmax()
    optimal_taper = final_values.loc[optimal_idx, "taper_length"]
    optimal_value = final_values.loc[optimal_idx, "monitor_7"]

    return fig, ax, combined_df, final_values, summary, optimal_taper, optimal_value


def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description="Analyze taper length data from RSoft monitor files."
    )
    parser.add_argument(
        "--expt-folder",
        type=str,
        default="beamprop_run_003",
        help="Experiment folder name (default: beamprop_run_003)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save the figure to a file",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="taper_length_analysis.png",
        help="Output file name (default: taper_length_analysis.png)",
    )

    args = parser.parse_args()

    # Use the arguments
    expt_folder = args.expt_folder
    to_print = args.save
    output_file = args.output_file

    results_dir = os.path.join("output", expt_folder, "rsoft_data_files")

    (
        fig,
        ax,
        combined_df,
        final_values,
        summary,
        optimal_taper,
        optimal_value,
    ) = plot_combined_monitor_files(results_dir)

    print("Summary of taper length analysis:")
    print(summary)
    print(f"\nOptimal taper length: {optimal_taper} μm")
    print(f"Optimal monitor_7 value: {optimal_value:.6f}")

    # Optional: save the figure
    if to_print:
        fig.savefig(output_file, dpi=300, bbox_inches="tight")
        print(f"Figure saved as {output_file}")

    plt.show()


# Example usage:
if __name__ == "__main__":
    main()
