import os


def get_next_run_folder(folder_path, prefix):
    """
    Find all folders with the given prefix in the specified path,
    identify the maximum run number, and return the next run folder name.

    Args:
        folder_path (str): Path to the directory to search in
        prefix (str): Prefix of the folders to search for

    Returns:
        str: Next run folder name in the format 'run_XXX' where XXX is the next number
    """
    max_run = 0

    # Check if the folder path exists
    if not os.path.exists(folder_path):
        raise ValueError(f"The folder path '{folder_path}' does not exist")

    # Get all directories in the folder path
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        # Check if it's a directory and starts with the prefix
        if os.path.isdir(item_path) and item.startswith(prefix):
            # Try to extract the run number
            try:
                # Extract the part after the prefix
                run_part = item[len(prefix) :]
                # Convert to integer
                run_number = int(run_part)
                # Update max_run if this is larger
                max_run = max(max_run, run_number)
            except (ValueError, IndexError):
                # If we can't convert to an integer, skip this directory
                continue

    # Return the next run number formatted as 'run_XXX'
    return f"{prefix}{max_run + 1:03d}"


# Example usage:
if __name__ == "__main__":
    next_run = get_next_run_folder("output", "taper_sweep_run_")
    print(next_run)  # Outputs something like "run_007" if the highest was "run_006"
