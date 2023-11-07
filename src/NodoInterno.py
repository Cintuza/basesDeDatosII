from src.Nodo import Nodo

class NodoInterno(Nodo):

    def __init__(self, pagina):
        self.tipoDeNodo = pagina[:1]
        self.esRaiz = pagina[1:2]
        self.punteroAXadre = pagina[2:6]
        self.cantidadDeElementos = pagina[6:10]
        self.punteroAHijeDerecho = pagina[10:14]
        self.elementos = self.listarPunteros(pagina[14:])

    def getTipoDeNodo(self):
        return int.from_bytes(self.tipoDeNodo)

    def getEsRaiz(self):
        return bool.from_bytes(self.esRaiz)

    def getPunteroAXadre(self):
        return int.from_bytes(self.punteroAXadre, byteorder="big")
    
    def getCantidadDeElementos(self):
        return int.from_bytes(self.cantidadDeElementos, byteorder="big")
    
    def estaCompleto(self):
        return self.getCantidadDeElementos() == 2

    def dividirNodo(self, tabla, numPaginaNodo, idRegistro, registroSerializado):
        tabla.dividirNodoInterno(numPaginaNodo, self, idRegistro, registroSerializado)

    def listarPunteros(self, punteros):
        cantidadDePunteros = self.getCantidadDeElementos()
        listaDePunteros = {}
        while cantidadDePunteros != 0:
            numDePagina = int.from_bytes(punteros[:4], byteorder="big")
            idRegistro = int.from_bytes(punteros[4:8], byteorder="big")
            listaDePunteros[numDePagina] = idRegistro
            punteros = punteros[8:]
            cantidadDePunteros -= 1
        return listaDePunteros
    
    def pasarNodoAPagina(self):
        pagina = self.tipoDeNodo
        pagina += self.esRaiz
        pagina += self.punteroAXadre
        pagina += self.cantidadDeElementos
        pagina += self.punteroAHijeDerecho
        punteros = b''
        for numDePagina, idRegistro in self.elementos.items():
            punteros += numDePagina.to_bytes(4, byteorder="big")
            punteros += idRegistro.to_bytes(4, byteorder="big")
        pagina += punteros
        cantidadDePunteros = self.getCantidadDeElementos()
        cantidadDeNulosParaCompletarPagina = 4096 - (cantidadDePunteros * 8 + 14)
        pagina += (b"\00" * cantidadDeNulosParaCompletarPagina)
        return pagina