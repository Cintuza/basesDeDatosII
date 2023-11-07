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
    
    @abstractmethod
    def estaCompleto(self):
        pass
    
    @abstractmethod
    def dividirNodo(self, tabla, numPaginaNodo, idRegistro, registroSerializado):
        pass