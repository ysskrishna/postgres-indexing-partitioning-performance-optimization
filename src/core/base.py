from abc import ABC, abstractmethod

class BaseSetup(ABC):
    @abstractmethod
    def setup(self, *args, **kwargs):
        pass

class BaseExecute(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def cleanup(self, *args, **kwargs):
        pass