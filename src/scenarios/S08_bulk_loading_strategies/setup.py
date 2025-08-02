from core.database import DatabaseConnection
from datasets.generator import DataGenerator
from core.benchmark import SimpleBenchmark
from core.logger import console
from core.base import BaseSetup

class Setup(BaseSetup):
    def setup(self):
        # This scenario does not require any setup
        pass
