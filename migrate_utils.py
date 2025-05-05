#!/usr/bin/env python3
"""
Migration Script for RSoft CAD Utils Reorganization

This script migrates the current flat structure of utils to the new organized structure.
It creates the necessary directories and moves the code to the appropriate locations.
"""

import os
import shutil
import re
from pathlib import Path


def create_directory_structure(base_path):
    """Create the new directory structure"""
    directories = ["lantern", "io", "config", "visualization"]

    for directory in directories:
        os.makedirs(os.path.join(base_path, directory), exist_ok=True)
        # Create __init__.py file
        with open(os.path.join(base_path, directory, "__init__.py"), "w") as f:
            f.write(f"# {directory} package\n")


def extract_functions(file_path):
    """Extract function definitions from a Python file"""
    with open(file_path, "r") as f:
        content = f.read()

    # Regular expression to find function definitions
    function_pattern = r"def\s+([a-zA-Z_0-9]+)\s*\("
    functions = re.findall(function_pattern, content)

    return functions


def create_main_init(base_path, function_mapping):
    """Create the main __init__.py file with all the imports"""
    init_content = """# src/rsoft_cad/utils/__init__.py
\"\"\"
RSoft CAD Utilities
==================

This package provides utilities for working with RSoft CAD files, 
creating and manipulating photonic lantern layouts, and visualizing data.
\"\"\"

# Import lantern layout functions
from .lantern.circular import lantern_layout, find_scale_factor
from .lantern.hexagonal import hexagonal_fiber_layout, calculate_capillary_diameter

# Import visualization functions
from .lantern.visualization import visualise_lantern, visualise_lp_lantern, plot_hexagonal_fibers
from .visualization.field_plots import plot_field_data
from .visualization.monitor_plots import plot_mon_data

# Import I/O functions
from .io.readers import read_field_data, read_mon_file, read_nef_file
from .io.finders import find_files_by_extension, find_fld_files, find_mon_files
from .io.filesystem import get_next_run_folder, copy_files_to_destination

# Import config functions
from .config.modifier import load_config, save_config, modify_parameter

# Version information
__version__ = '0.1.0'
"""

    with open(os.path.join(base_path, "__init__.py"), "w") as f:
        f.write(init_content)


def migrate_code(src_base, dest_base):
    """Migrate code from old structure to new structure"""

    # Define the mapping of functions to new locations
    function_mapping = {
        "cir_lantern_layout.py": {
            "lantern_layout": "lantern/circular.py",
            "find_scale_factor": "lantern/circular.py",
            "visualise_lantern": "lantern/visualization.py",
        },
        "hex_lantern_layout.py": {
            "hexagonal_fiber_layout": "lantern/hexagonal.py",
            "calculate_capillary_diameter": "lantern/hexagonal.py",
            "plot_hexagonal_fibers": "lantern/visualization.py",
        },
        "plot_utils.py": {
            "visualise_lantern": "lantern/visualization.py:visualise_lp_lantern"
        },
        "read_rsoft_data.py": {
            "find_fld_files": "io/finders.py",
            "find_mon_files": "io/finders.py",
            "find_files_by_extension": "io/finders.py",
            "read_field_data": "io/readers.py",
            "read_mon_file": "io/readers.py",
            "read_nef_file": "io/readers.py",
            "copy_files_to_destination": "io/filesystem.py",
        },
        "plot_rsoft_data.py": {
            "plot_mon_data": "visualization/monitor_plots.py",
            "plot_field_data": "visualization/field_plots.py",
        },
        "folder_utils.py": {"get_next_run_folder": "io/filesystem.py"},
        "modify_config.py": {
            "*": "config/modifier.py"  # Special case: move all functions
        },
    }

    # Create the new directory structure
    create_directory_structure(dest_base)

    # Process each file
    for source_file, functions in function_mapping.items():
        source_path = os.path.join(src_base, source_file)

        if not os.path.exists(source_path):
            print(f"Warning: Source file {source_path} not found, skipping...")
            continue

            # Special case: copy entire file
        if "*" in functions:
            dest_path = os.path.join(dest_base, functions["*"])
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(source_path, dest_path)
            print(f"Copied entire file: {source_path} -> {dest_path}")
            continue

        # Read the source file content
        with open(source_path, "r") as f:
            source_content = f.read()

        # Extract imports
        import_pattern = r"(import.*?\n|from.*?import.*?\n)"
        imports = re.findall(import_pattern, source_content)
        imports_text = "".join(imports)

        # Process each function
        for func_name, dest_file in functions.items():
            # Check if there's a rename operation
            if ":" in dest_file:
                dest_file, new_func_name = dest_file.split(":")
            else:
                new_func_name = func_name

            dest_path = os.path.join(dest_base, dest_file)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # Extract the function definition and body
            func_pattern = r"(def\s+" + func_name + r"\s*\([^)]*\):.*?(?=\n\S|\Z))"
            func_match = re.search(func_pattern, source_content, re.DOTALL)

            if not func_match:
                print(f"Warning: Could not find function {func_name} in {source_path}")
                continue

            func_code = func_match.group(0)

            # If we're renaming the function, update the function definition
            if new_func_name != func_name:
                func_code = func_code.replace(
                    f"def {func_name}", f"def {new_func_name}", 1
                )

            # Check if the destination file exists
            file_exists = os.path.exists(dest_path)

            # Create or append to the destination file
            with open(dest_path, "a+" if file_exists else "w") as f:
                if not file_exists:
                    # Add file header and imports for new files
                    f.write(f"# {dest_file}\n")
                    f.write('"""\n')
                    module_name = os.path.basename(dest_file).replace(".py", "")
                    f.write(
                        f"{module_name.capitalize()} module for RSoft CAD utilities\n"
                    )
                    f.write('"""\n\n')
                    f.write(imports_text)
                    f.write("\n\n")

                # Write the function code
                f.write(func_code)
                f.write("\n\n")

            print(
                f"Migrated: {func_name} -> {dest_path}"
                + (
                    f" (renamed to {new_func_name})"
                    if new_func_name != func_name
                    else ""
                )
            )

    # Create the main __init__.py file
    create_main_init(dest_base, function_mapping)

    print("\nMigration complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate RSoft CAD utils to new structure"
    )
    parser.add_argument(
        "--src",
        default="src/rsoft_cad/utils",
        help="Source directory (default: src/rsoft_cad/utils)",
    )
    parser.add_argument(
        "--dest",
        default="src/rsoft_cad/utils_new",
        help="Destination directory (default: src/rsoft_cad/utils_new)",
    )

    args = parser.parse_args()

    # Ensure source exists
    if not os.path.isdir(args.src):
        print(f"Error: Source directory {args.src} does not exist")
        exit(1)

    # Confirm with user
    print(f"This will migrate utils from {args.src} to {args.dest}")
    confirm = input("Continue? [y/N] ")

    if confirm.lower() != "y":
        print("Migration canceled.")
        exit(0)

    # Create destination if it doesn't exist
    os.makedirs(args.dest, exist_ok=True)

    # Perform migration
    migrate_code(args.src, args.dest)
