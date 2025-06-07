import pandas as pd
import textwrap
from typing import Dict, List, Any, Tuple, Optional


def get_fiber_type_list_by_indices(
    smf_df: pd.DataFrame, indices: List[int]
) -> List[str]:
    """
    Return a list of fiber types based on DataFrame row indices.

    Args:
        smf_df: DataFrame containing fiber specifications
        indices: List of row indices in the DataFrame

    Returns:
        List of fiber type strings corresponding to the indices
    """
    fiber_types = []

    for idx in indices:
        if 0 <= idx < len(smf_df):
            fiber_types.append(smf_df.iloc[idx]["Fiber_Type"])
        else:
            raise ValueError(
                f"Index {idx} is out of bounds for DataFrame with {len(smf_df)} rows"
            )

    return fiber_types


def print_dict(
    dict_obj: Dict[str, Any],
    width: int = 80,
    indent: int = 4,
) -> None:
    """
    Print a dictionary with indented values.

    Args:
        dict_obj: Dictionary to print
        width: Width of the separator line
        indent: Number of spaces to use for indentation
    """
    for key, value in dict_obj.items():
        print(f"{key}: ")
        print(textwrap.indent(str(value), " " * indent))
    print("=" * width)


def fiber_assignment(
    core_map: Dict[str, Any],
    fiber_type_list: List[str],
    smf_df: pd.DataFrame,
    columns_to_include: Optional[List[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Assign fiber properties to each core in the core map for all or selected columns.

    Args:
        core_map: Dictionary mapping LP modes to their properties
        fiber_type_list: List of fiber types to assign to cores
        smf_df: DataFrame containing fiber specifications
        columns_to_include: If provided, only process these columns. If None, process all columns.

    Returns:
        Dictionary where:
        - Keys are column names from the DataFrame
        - Values are dictionaries mapping LP modes to their respective property values
    """
    # Create a dictionary to hold all property dictionaries
    property_dicts: Dict[str, Dict[str, Any]] = {}

    # Determine which columns to process
    cols_to_process = columns_to_include if columns_to_include else smf_df.columns

    # Initialize a dictionary for each column
    for column in cols_to_process:
        if column in smf_df.columns:  # Ensure column exists
            property_dicts[column] = {}

    for i, (key, _) in enumerate(core_map.items()):
        if i < len(fiber_type_list):
            # Get the fiber type for this core
            fiber_type = fiber_type_list[i]
            # Find the row with this fiber type
            fiber_data = smf_df[smf_df["Fiber_Type"] == fiber_type]

            if not fiber_data.empty:
                # For each column, add the value to the corresponding property dictionary
                for column in cols_to_process:
                    if column in fiber_data.columns:
                        property_dicts[column][key] = fiber_data[column].values[0]

    return property_dicts
