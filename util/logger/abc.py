from abc import ABCMeta, abstractmethod


class BaseLogger(metaclass=ABCMeta):
    @abstractmethod
    def info(self, msg, child_Name, signature):
        ...

    @abstractmethod
    def warning(self, msg, child_Name, signature):
        ...

    @abstractmethod
    def error(self, msg, child_Name, signature):
        ...

