def calculate_taper_properties(
    position,
    start_dia=None,
    end_dia=None,
    taper_length=None,
    taper_factor=None,
):
    """
    Calculate properties at any point along a tapered section.

    Parameters:
    position (float): Position along the taper where properties are needed
    start_dia (float, optional): Starting diameter
    end_dia (float, optional): Ending diameter
    taper_length (float, optional): Length of the tapered section. Defaults to 100.0 if not provided.
    taper_factor (float, optional): Ratio of start diameter to end diameter. Can be used instead of providing both diameters.

    Returns:
    tuple: (diameter, taper_rate, taper_factor, end_dia)
        - diameter (float): Diameter at the specified position
        - taper_rate (float): Rate of change of diameter per unit length
        - taper_factor (float): Ratio of start diameter to end diameter
        - end_dia (float): Ending diameter
    """
    # Set default values if not provided
    if taper_length is None:
        taper_length = 100.0

    # Handle different input combinations
    if taper_factor is not None:
        # If taper_factor is provided
        if start_dia is not None:
            # Calculate end_dia from start_dia and taper_factor
            end_dia = start_dia / taper_factor
        elif end_dia is not None:
            # Calculate start_dia from end_dia and taper_factor
            start_dia = end_dia * taper_factor
        else:
            # If neither diameter is provided, use default start_dia
            start_dia = 10.0
            end_dia = start_dia / taper_factor
    else:
        # Handle cases without taper_factor
        if start_dia is None and end_dia is None:
            start_dia = 10.0
            end_dia = 5.0
        elif start_dia is None and end_dia is not None:
            # If only end diameter is provided, assume a standard taper rate
            taper_rate = -0.05  # Default taper rate
            start_dia = end_dia - (taper_rate * taper_length)
        elif end_dia is None and start_dia is not None:
            # If only start diameter is provided, assume a standard taper rate
            taper_rate = -0.05  # Default taper rate
            end_dia = start_dia - (taper_rate * taper_length)

    # Check that position is within the taper length
    if position < 0 or position > taper_length:
        raise ValueError(
            f"Position must be between 0 and taper length ({taper_length})"
        )

    # Calculate taper factor and rate
    taper_factor = start_dia / end_dia if end_dia != 0 else float("inf")
    taper_rate = (end_dia - start_dia) / taper_length

    # Calculate the diameter at the given position
    diameter = start_dia + (taper_rate * position)

    # Return all requested values
    return diameter, taper_rate, taper_factor, end_dia


if __name__ == "__main__":

    print(
        calculate_taper_properties(
            position=40000,
            start_dia=375 - 125,
            end_dia=None,
            taper_factor=8,
            taper_length=50000,
        )
    )
