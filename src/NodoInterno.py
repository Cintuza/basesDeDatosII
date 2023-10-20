class NodoInterno:

    def __init__(self, pagina):
        self.tipoDeNodo = pagina[:1]
        self.esRaiz = pagina[1:2]
        self.punteroAXadre = pagina[2:6]
        self.cantidadClaves = pagina[6:10]
        self.punteroAHijeDerecho = pagina[10:14]
        self.punteros = self.listarPunteros(pagina[14:])

    def listarPunteros(self, punteros):
        cantidadDePunteros = int.from_bytes(self.cantidadClaves, byteorder="big")
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
        pagina += self.cantidadClaves
        pagina += self.punteroAHijeDerecho
        punteros = b''
        for numDePagina, idRegistro in self.punteros.items():
            punteros += numDePagina.to_bytes(4, byteorder="big")
            punteros += idRegistro.to_bytes(4, byteorder="big")
        pagina += punteros
        cantidadDePunteros = int.from_bytes(self.cantidadClaves, byteorder="big")
        cantidadDeNulosParaCompletarPagina = 4096 - (cantidadDePunteros * 8 + 14)
        pagina += (b"\00" * cantidadDeNulosParaCompletarPagina)
        return pagina