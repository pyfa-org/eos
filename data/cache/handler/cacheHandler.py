from abc import ABCMeta
from abc import abstractmethod


class CacheHandler(metaclass=ABCMeta):
  """Abstract base class for cache handlers."""


  @abstractmethod
  def getType(self, typeID):
    ...

  @abstractmethod
  def getAttribute(self, attrID):
    ...

  @abstractmethod
  def getEffect(self, effectID):
    ...

  @abstractmethod
  def getModifier(self, modifierID):
    ...

  @abstractmethod
  def getFingerprint(self):
    ...

  @abstractmethod
  def updateCache(self, data, fingerprint):
    ...

