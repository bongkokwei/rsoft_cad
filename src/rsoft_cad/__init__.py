import logging
import os


def configure_logging(log_file="simulation.log", log_level=logging.INFO):
    """
    Configure logging for the rsoft_cad package.

    Parameters
    ----------
    log_file : str
        Path to the log file
    log_level : int
        Logging level (e.g., logging.INFO, logging.DEBUG)
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=log_level,
        # format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        format="%(asctime)s - %(module)s.%(funcName)s - %(levelname)s - \n\t %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),  # Prints to console as well
        ],
    )

    # Return the root logger in case the caller wants to customize it further
    return logging.getLogger()
