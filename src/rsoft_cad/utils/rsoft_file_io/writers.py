def write_femsim_field_data(
    filename,
    complex_data,
    xmin,
    xmax,
    ymin,
    ymax,
    z_pos=0,
    output_type="OUTPUT_REAL_IMAG_3D",
    effective_index=1.0,
    wavelength=1.55,
    format_suffix="/ls1",
):
    """
    Write complex field data to a 2D uniform grid file in RSoft format.

    Parameters:
    -----------
    filename : str
        Path to the output file
    complex_data : numpy.ndarray
        2D numpy array of complex values with shape (nx, ny)
    xmin, xmax : float
        X-axis range
    ymin, ymax : float
        Y-axis range
    z_pos : float, optional
        Z position of the field data. Default is 0.
    output_type : str, optional
        Type of output data. Default is "OUTPUT_REAL_IMAG_3D".
    effective_index : float, optional
        Effective index value. Default is 1.0.
    wavelength : float, optional
        Wavelength value in μm. Default is 1.55.
    format_suffix : str, optional
        Suffix for the format line. Default is "/ls1".

    Returns:
    --------
    None
    """
    # Get the dimensions of the complex data
    nx, ny = complex_data.shape

    # Open the file for writing
    with open(filename, "w") as f:
        # Write the header format lines
        f.write(f"/rn,a,b/nx0{format_suffix}\n")
        f.write("/r,qa,qb\n")

        # Write the X grid information
        f.write(
            f"{nx} {xmin} {xmax} {z_pos} {output_type} {effective_index} 0 Wavelength={wavelength}\n"
        )

        # Write the Y grid information
        f.write(f"{ny} {ymin} {ymax}\n")

        # Write the data rows
        for i in range(nx):
            row_data = []
            for j in range(ny):
                # Extract real and imaginary parts and format with scientific notation
                real = complex_data[i, j].real
                imag = complex_data[i, j].imag
                row_data.append(f"{real:14.5E}")
                row_data.append(f"{imag:14.5E}")

            # Join the row data with spaces and write to file
            f.write("  " + "  ".join(row_data) + "\n")

    print(f"Successfully wrote field data to {filename}")
