

from abc import ABCMeta, abstractmethod
from . import Communication_Interface as C_I


class Plant(metaclass=ABCMeta):
    def __init__(self, method):
        self.method = method
        method.register(self)

    def connection(self):
        file_name = self.get_file_name_plant()
        self.connect = C_I.Communication_Interface(file_name)
        return self.connect.connection()

    @abstractmethod
    def get_file_name_plant(self):
        pass

    @abstractmethod
    def process_simulation(self):
        pass

    @abstractmethod
    def update(self, data):
        pass