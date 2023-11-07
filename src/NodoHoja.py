from src.Nodo import Nodo
from src.NodoInterno import NodoInterno

class NodoHoja(Nodo):

    def __init__(self, pagina):
        self.tipoDeNodo = pagina[:1]
        self.esRaiz = pagina[1:2]
        self.punteroAXadre = pagina[2:6]
        self.cantidadDeElementos = pagina[6:10]
        self.elementos = self.listarRegistros(pagina[10:])

    def getTipoDeNodo(self):
        return int.from_bytes(self.tipoDeNodo)

    def getEsRaiz(self):
        return bool.from_bytes(self.esRaiz)

    def getPunteroAXadre(self):
        return int.from_bytes(self.punteroAXadre, byteorder="big")
    
    def getCantidadDeElementos(self):
        return int.from_bytes(self.cantidadDeElementos, byteorder="big")
    
    def estaCompleto(self):
        return self.getCantidadDeElementos() == 13

    def dividirNodo(self, tabla, numPaginaNodo, idRegistro, registroSerializado):
        tabla.dividirNodoHoja(numPaginaNodo, self, idRegistro, registroSerializado)

    def listarRegistros(self, registros):
        cantidadDeRegistros = self.getCantidadDeElementos()
        listaDeRegistros = {}
        while cantidadDeRegistros != 0:
            idRegistro = int.from_bytes(registros[:4], byteorder="big")
            registro = registros[4:295]
            listaDeRegistros[idRegistro] = registro
            registros = registros[295:]
            cantidadDeRegistros -= 1
        return listaDeRegistros
    
    def pasarNodoAPagina(self):
        pagina = self.tipoDeNodo
        pagina += self.esRaiz
        pagina += self.punteroAXadre
        pagina += self.cantidadDeElementos
        registros = b''
        for idRegistro, registro in self.elementos.items():
            registros += idRegistro.to_bytes(4, byteorder="big")
            registros += registro
        pagina += registros
        cantidadDeRegistros = self.getCantidadDeElementos()
        cantidadDeNulosParaCompletarPagina = 4096 - (cantidadDeRegistros * 295 + 10)
        pagina += (b"\00" * cantidadDeNulosParaCompletarPagina)
        return pagina
    
    def insertarRegistroEn(self, posicion, registro):
        self.elementos.insert(posicion, registro)

    def posicionParaNuevoRegistro(self, idRegistroAInsertar):
        cantDeRegistros = self.getCantidadDeElementos()
        registrosEnPagina = self.elementos
        posicionDelRegistroAAgregar = None
        if cantDeRegistros == 0:
            posicionDelRegistroAAgregar = 0
        elif registrosEnPagina[-1][:4] < idRegistroAInsertar:
            posicionDelRegistroAAgregar = cantDeRegistros
        else:
            posicionDelRegistroAAgregar = 0
            registroEnPagina = registrosEnPagina[posicionDelRegistroAAgregar]
            while registroEnPagina[:4] < idRegistroAInsertar:
                posicionDelRegistroAAgregar += 1
                registroEnPagina = registrosEnPagina[posicionDelRegistroAAgregar]
        return posicionDelRegistroAAgregar
    
    def convertirEnNodoInterno(self):
        pagina = b"\00"
        pagina += self.esRaiz
        pagina += self.punteroAXadre
        pagina += (b"\00" * 4090)
        nodoInterno = NodoInterno(pagina)
        return nodoInterno