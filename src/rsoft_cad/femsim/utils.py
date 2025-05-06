from typing import List, Optional


def filter_indices(
    unique_indices: List[int],
    max_indices: Optional[int],
    plot_indices: Optional[List[int]],
) -> List[int]:
    """
    Filter indices based on provided criteria.

    Args:
        unique_indices (List[int]): List of all available unique indices
        max_indices (Optional[int]): Maximum number of indices to display
        plot_indices (Optional[List[int]]): Specific indices to plot

    Returns:
        List[int]: Filtered list of indices to plot
    """
    # Filter indices if a list of indices is requested
    if plot_indices is not None:
        valid_indices_to_plot = [idx for idx in plot_indices if idx in unique_indices]
        if not valid_indices_to_plot:
            print(
                f"Warning: None of the specified indices ({plot_indices}) were found in the data."
            )
            return []
        return valid_indices_to_plot
    elif max_indices is not None and max_indices < len(unique_indices):
        return unique_indices[:max_indices]
    return unique_indices
