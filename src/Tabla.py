from src.Paginador import Paginador
from src.NodoHoja import NodoHoja

class Tabla:

    def __init__(self, paginador):
        self.paginador = paginador

    def paginaAEscribir(self):
        if len(self.obtenerTodosLosRegistros()) % 14 == 0:
            return self.ultimaPaginaEscrita() + 1
        else:
            return self.ultimaPaginaEscrita()

    def ultimaPaginaEscrita(self):
        if len(self.paginador.cache) == 0:
            return self.cantPaginasBaseDeDatos()
        else:
            return max(self.paginador.cache.keys())
    
    def paginaNueva(self):
        if len(self.paginador.cache) == 0:
            return self.cantPaginasBaseDeDatos() + 1
        else:
            mayorPaginaEnCache = max(self.paginador.cache.keys())
            return max(self.cantPaginasBaseDeDatos(), mayorPaginaEnCache) + 1
    
    def cantPaginasBaseDeDatos(self):
        tamanioBaseDatos = self.paginador.tamanioBaseDatos
        if (tamanioBaseDatos % 4096 == 0):
            return int(tamanioBaseDatos / 4096)
        else:
            return int(tamanioBaseDatos / 4096) + 1
        
    def guardarRegistroEnCache(self, registro):
        registroSerializado = self.serializar(registro)
        # obtengo la pagina a escribir
        numPagina = self.paginador.obtenerPagina(self.paginaAEscribir())
        nodoHoja = self.paginador.cache[numPagina]
        # agrego el registro a la lista de registros del nodo
        self.agregarRegistroAPagina(nodoHoja, registroSerializado)
        if self.getCantidadDeRegistrosPagina(nodoHoja) < 14:
            self.paginador.cache[numPagina] = nodoHoja
        else:
            # primer nodo hoja nuevo
            numPrimerNodoHojaNuevo = self.paginador.obtenerPagina(self.paginaNueva())
            primerNodoHojaNuevo = self.paginador.cache[numPrimerNodoHojaNuevo]
            # segundo nodo hoja nuevo
            numSegundoNodoHojaNuevo = self.paginador.obtenerPagina(self.paginaNueva())
            segundoNodoHojaNuevo = self.paginador.cache[numSegundoNodoHojaNuevo]
            # se actualizan los registros y cantidad de reg en ambos nodos
            primerNodoHojaNuevo.registros = nodoHoja.registros[:7]
            segundoNodoHojaNuevo.registros = nodoHoja.registros[7:]
            self.setCantidadDeRegistrosPagina(primerNodoHojaNuevo, 7)
            self.setCantidadDeRegistrosPagina(segundoNodoHojaNuevo, 7)
            # se completa puntero a nodo xadre
            self.setPunteroAXadre(primerNodoHojaNuevo, numPagina)
            self.setPunteroAXadre(segundoNodoHojaNuevo, numPagina)
            # se pasa en nodo raiz a nodo interno
            nodoInterno = nodoHoja.convertirEnNodoInterno()
            ultimoRegistroDelPrimerNodo = primerNodoHojaNuevo.registros[6]
            idUltimoRegistroDelPrimerNodo = int.from_bytes(ultimoRegistroDelPrimerNodo[:4], byteorder="big")
            nodoInterno.punteros[numPrimerNodoHojaNuevo] = idUltimoRegistroDelPrimerNodo
            self.setCantidadDeClaves(nodoInterno, 1)
            self.setPunteroAHijeDerecho(nodoInterno, numSegundoNodoHojaNuevo)
            # se actualizan los nodos en el cache
            self.paginador.cache[numPagina] = nodoInterno
            self.paginador.cache[numPrimerNodoHojaNuevo] = primerNodoHojaNuevo
            self.paginador.cache[numSegundoNodoHojaNuevo] = segundoNodoHojaNuevo

    def agregarRegistroAPagina(self, nodoHoja, registroSerializado):
        idRegistro = registroSerializado[0:4]
        registroSerializadoConId = idRegistro + registroSerializado
        # agrego el registro a la lista de registros del nodo
        posicionDelRegistroAAgregar = self.obtenerPosicionDeRegistroAInsertar(nodoHoja, idRegistro)
        # actualizo cantidad de registros en nodo
        cantDeRegistros = self.getCantidadDeRegistrosPagina(nodoHoja)
        cantDeRegistros += 1
        self.setCantidadDeRegistrosPagina(nodoHoja, cantDeRegistros)
        self.setRegistroEn(nodoHoja, posicionDelRegistroAAgregar, registroSerializadoConId)

    def obtenerPosicionDeRegistroAInsertar(self, nodoHoja, idRegistroAInsertar):
        return nodoHoja.posicionParaNuevoRegistro(idRegistroAInsertar)

    def cantidadDeRegistrosGuardados(self):
        return 0
        # if (self.cantPaginasBaseDeDatos() == 0):
        #     return 0
        # else:
        #     self.paginador.obtenerPagina(self.paginaAEscribir())
        #     pagina = self.paginador.cache[self.ultimaPaginaEscrita()]
        #     cantDeRegistros = self.getCantidadDeRegistrosPagina(pagina)
        #     return cantDeRegistros
        
    def guardarRegistrosEnBaseDeDatos(self):
        self.paginador.actualizarArchivo()

    def obtenerTodosLosRegistrosDeserializados(self):
        registros = self.obtenerTodosLosRegistros()
        registrosDeserializados = ""
        for registro in registros:
            registro = registro[4:]
            registroDeserializado = self.deserializar(registro)
            registrosDeserializados += registroDeserializado
            if registro[:4] != registros[-1][:4]:
                registrosDeserializados += "\n"
        return registrosDeserializados

    def obtenerTodosLosRegistros(self):
        paginas = self.obtenerTodasLasPaginas()
        registros = []
        for pagina in paginas:
            tipoDeNodo = int.from_bytes(pagina.tipoDeNodo)
            if tipoDeNodo == 1:
                registros += pagina.registros
        return registros
    
    def obtenerTodasLasPaginas(self):
        paginas = []
        for numPagina in range(1, self.ultimaPaginaEscrita() + 1):
            posicionPagina = self.paginador.obtenerPagina(numPagina)
            pagina = self.paginador.cache[posicionPagina]
            paginas.append(pagina)
        return paginas
        
    def serializar(self, registro):
        elementosDelRegistro = registro.split(" ")
        id = elementosDelRegistro[0]
        nombre = elementosDelRegistro[1]
        email = elementosDelRegistro[2]

        idSerializado = self.serializarId(id)
        nombreSerializado = self.serializarNombre(nombre)
        emailSerializado = self.serializarEmail(email)

        registroSerializado = idSerializado + nombreSerializado + emailSerializado

        return registroSerializado
    
    # Recibe un ID en string, lo convierte a int, y despues a 4 bytes en formato big endian
    def serializarId(self, id):
        numId = int(id)
        return numId.to_bytes(4, byteorder="big")
    
    # Recibe un string correspondiente a un nombre y devuelve 32 bytes como sigue:
    # - los primeros bytes representan el nombre ingresado traducido en byte en formato ascii
    # - los siguientes bytes corresponden a caracteres nulos
    def serializarNombre(self, nombre):
        nombreEnBytes = bytes(nombre, "ascii")
        cantidadEspaciosNulosNecesarios = 32 - len(nombreEnBytes)
        return nombreEnBytes + b"\00"*cantidadEspaciosNulosNecesarios
    
    # Recibe un string correspondiente a un email y devuelve 255 bytes como sigue:
    # - los primeros bytes representan el email ingresado traducido en byte en formato ascii
    # - los siguientes bytes corresponden a caracteres nulos
    def serializarEmail(self, email):
        emailEnBytes = bytes(email, "ascii")
        cantidadEspaciosNulosNecesarios = 255 - len(emailEnBytes)
        return emailEnBytes + b"\00"*cantidadEspaciosNulosNecesarios

    # Recibe 291 bytes que se distribuyen de la siguiente manera:
    # - primeros 4 bytes corresponden a un int
    # - los siguientes 32 bytes corresponden a un string que representan un nombre
    # - los ultimos 255 bytes corresponden a un string que representa un email
    # Devuelve los tres datos en string separados por un espacio
    def deserializar(self, registro):
        idEnBytes = registro[:4]
        nombreEnBytes = registro[4:36]
        emailEnBytes = registro[36:]
        
        id = self.deserializarId(idEnBytes)
        nombre = self.deserializarString(nombreEnBytes)
        email = self.deserializarString(emailEnBytes)

        return id + " " + nombre + " " + email

    # Recibe 4 bytes en formato big endian, transforma el numero en int y lo devuelve en string
    def deserializarId(self, id):
        numId = int.from_bytes(id, byteorder="big")
        return str(numId)

    # Recibe bytes codificados en ascii y devuelve un string decodificado, 
    # eliminando los bytes de mas que pueda llegar a haber
    def deserializarString(self, bytes):
        posicionFinalDatos = bytes.find(b'\x00')
        datosEnBytes = bytes[:posicionFinalDatos]
        return str(datosEnBytes, 'ascii')
    
    def getTipoNodo(self, pagina):
        tipoDeNodo = pagina[0:1]
        return tipoDeNodo
    
    def getEsRaiz(self, pagina):
        esRaiz = pagina[1:2]
        return esRaiz
    
    def getPunteroAXadre(self, pagina):
        punteroAXadre = pagina[2:6]
        return punteroAXadre
    
    def setPunteroAXadre(self, nodoHoja, numPagina):
        punteroAXadreSerializado = numPagina.to_bytes(4, byteorder="big")
        nodoHoja.punteroAXadre = punteroAXadreSerializado
    
    def setPunteroAHijeDerecho(self, nodoInterno, numPagina):
        punteroAHijeDerechoSerializado = numPagina.to_bytes(4, byteorder="big")
        nodoInterno.punteroAHijeDerecho = punteroAHijeDerechoSerializado
    
    def getCantidadDeRegistrosPagina(self, nodoHoja):
        cantidadDeRegistros = int.from_bytes(nodoHoja.cantidadRegistros, byteorder="big")
        return cantidadDeRegistros

    def setCantidadDeRegistrosPagina(self, nodoHoja, cantDeRegistrosActualizada):
        cantidadDeRegistrosSerializado = cantDeRegistrosActualizada.to_bytes(4, byteorder="big")
        nodoHoja.cantidadRegistros = cantidadDeRegistrosSerializado

    def setCantidadDeClaves(self, nodoInterno, cantDeClavesActualizada):
        cantidadDeClavesSerializada = cantDeClavesActualizada.to_bytes(4, byteorder="big")
        nodoInterno.cantidadClaves = cantidadDeClavesSerializada

    def setRegistroEn(self, nodoHoja, posicion, registro):
        nodoHoja.insertarRegistroEn(posicion, registro)

    # def getValorEn(self, pagina, posicion):
    #     posicionEnPagina = 14 + posicion * 295
    #     valor = pagina[posicionEnPagina:posicionEnPagina + 291]
    #     return valor
    
    # def getClaveEn(self, pagina, posicion):
    #     posicionEnPagina = 10 + posicion * 295
    #     clave = pagina[posicionEnPagina:posicionEnPagina + 4]
    #     return clave