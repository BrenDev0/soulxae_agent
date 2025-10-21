import os
from src.shared.dependencies.container import Container

from src.shared.utils.logs.logger import Logger

def configure_container():
    logger = Logger()
    Container.register("logger", logger)

    




    





