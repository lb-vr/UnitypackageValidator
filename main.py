import os
import logging

from src.main import main as main_func
from src.logger_setup import setupLogger


if __name__ == "__main__":
    setupLogger("UnitypackageTools", stderr_level=logging.DEBUG)
    logging.getLogger().info("Current-directory: %s", os.getcwd())
    main_func("test.unitypackage")
