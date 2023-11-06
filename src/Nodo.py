from abc import ABC, abstractmethod

class Nodo(ABC):

    @abstractmethod
    def getTipoDeNodo(self):
        pass

    @abstractmethod
    def getEsRaiz(self):
        pass

    @abstractmethod
    def getPunteroAXadre(self):
        pass
    
    @abstractmethod
    def getCantidadDeElementos(self):
        pass