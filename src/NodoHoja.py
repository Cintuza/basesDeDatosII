from src.NodoInterno import NodoInterno

class NodoHoja:

    def __init__(self, pagina):
        self.tipoDeNodo = pagina[:1]
        self.esRaiz = pagina[1:2]
        self.punteroAXadre = pagina[2:6]
        self.cantidadRegistros = pagina[6:10]
        self.registros = self.listarRegistros(pagina[10:])

    def listarRegistros(self, registros):
        cantidadDeRegistros = int.from_bytes(self.cantidadRegistros, byteorder="big")
        listaDeRegistros = []
        while cantidadDeRegistros != 0:
            listaDeRegistros.append(registros[:295])
            registros = registros[295:]
            cantidadDeRegistros -= 1
        return listaDeRegistros
    
    def pasarNodoAPagina(self):
        pagina = self.tipoDeNodo
        pagina += self.esRaiz
        pagina += self.punteroAXadre
        pagina += self.cantidadRegistros
        registros = b''
        for registro in self.registros:
            registros += registro
        pagina += registros
        cantidadDeRegistros = int.from_bytes(self.cantidadRegistros, byteorder="big")
        cantidadDeNulosParaCompletarPagina = 4096 - (cantidadDeRegistros * 295 + 10)
        pagina += (b"\00" * cantidadDeNulosParaCompletarPagina)
        return pagina
    
    def insertarRegistroEn(self, posicion, registro):
        self.registros.insert(posicion, registro)

    def posicionParaNuevoRegistro(self, idRegistroAInsertar):
        cantDeRegistros = int.from_bytes(self.cantidadRegistros, byteorder="big")
        registrosEnPagina = self.registros
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