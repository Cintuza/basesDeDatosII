from src.Paginador import Paginador
from src.NodoHoja import NodoHoja
import operator

class Tabla:

    def __init__(self, paginador):
        self.paginador = paginador

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
        
    def guardarRegistroEnCache(self, registro, numPagina):
        registroSerializado = self.serializar(registro)
        numPaginaRaiz = self.paginador.obtenerPagina(numPagina)
        nodoRaiz = self.paginador.cache[numPaginaRaiz]
        esNodoHoja = bool.from_bytes(nodoRaiz.tipoDeNodo)
        if esNodoHoja:
            self.agregarRegistroAPagina(nodoRaiz, registroSerializado)
            if self.getCantidadDeRegistrosPagina(nodoRaiz) < 14:
                self.paginador.cache[numPaginaRaiz] = nodoRaiz
            else:
                self.dividirNodo(numPaginaRaiz, nodoRaiz)
        else:
            numPaginaAEscribir = None
            idRegistroDeserializado = int.from_bytes(registroSerializado[:4], byteorder = "big")
            for pagina, id in nodoRaiz.punteros.items():
                if id > idRegistroDeserializado:
                    numPaginaAEscribir = pagina
                    break
            if numPaginaAEscribir == None:
                punteroDerecho = int.from_bytes(nodoRaiz.punteroAHijeDerecho, byteorder = "big")
                numPaginaAEscribir = punteroDerecho
            self.guardarRegistroEnCache(registro, numPaginaAEscribir)

    def dividirNodo(self, numPaginaNodo, nodo):
        esRaiz = self.getEsRaiz(nodo)
        registros = nodo.registros
        if esRaiz:
            # primer nodo
            numPrimerNodo = self.paginador.obtenerPagina(self.paginaNueva())
            primerNodo = self.paginador.cache[numPrimerNodo]
            # nodo xadre
            punteroAXadre = numPaginaNodo
            nodoXadre = nodo.convertirEnNodoInterno()
        else:
            # primer nodo
            numPrimerNodo = numPaginaNodo
            primerNodo = self.paginador.cache[numPaginaNodo]
            # nodo xadre
            punteroAXadre = int.from_bytes(nodo.punteroAXadre, byteorder="big")
            nodoXadre = self.paginador.cache[punteroAXadre]    
        # segundo nodo
        numSegundoNodo = self.paginador.obtenerPagina(self.paginaNueva())
        segundoNodo = self.paginador.cache[numSegundoNodo]
        # se actualizan los registros y cantidad de reg en ambos nodos
        primerNodo.registros = registros[:7]
        segundoNodo.registros = registros[7:]
        self.setCantidadDeRegistrosPagina(primerNodo, 7)
        self.setCantidadDeRegistrosPagina(segundoNodo, 7)
        # se completa puntero a nodo xadre en el nodo nuevo
        self.setPunteroAXadre(primerNodo, punteroAXadre)
        self.setPunteroAXadre(segundoNodo, punteroAXadre)
        cantidadDePunteros = int.from_bytes(nodoXadre.cantidadClaves, byteorder="big")
        self.setCantidadDeClaves(nodoXadre, cantidadDePunteros + 1)
        punteroHijeDerecho = int.from_bytes(nodoXadre.punteroAHijeDerecho, byteorder="big")
        # actualizo puntero nodo anterior en nodo xadre
        ultimoRegistroDelNodoRaiz = primerNodo.registros[-1]
        idUltimoRegistroDelNodoRaiz = int.from_bytes(ultimoRegistroDelNodoRaiz[:4], byteorder="big")
        nodoXadre.punteros[numPrimerNodo] = idUltimoRegistroDelNodoRaiz
        # agrego puntero de nodo nuevo en nodo xadre
        if punteroHijeDerecho == numPaginaNodo or esRaiz:
            self.setPunteroAHijeDerecho(nodoXadre, numSegundoNodo)
        else:
            ultimoRegistroDelSegundoNodo = segundoNodo.registros[-1]
            idUltimoRegistroDelSegundoNodo = int.from_bytes(ultimoRegistroDelSegundoNodo[:4], byteorder="big")
            nodoXadre.punteros[numSegundoNodo] = idUltimoRegistroDelSegundoNodo
        # ordeno los punteros
        nodoXadre.punteros = dict(sorted(nodoXadre.punteros.items(), key=operator.itemgetter(1)))
        self.paginador.cache[numSegundoNodo] = segundoNodo
        self.paginador.cache[numPrimerNodo] = primerNodo
        self.paginador.cache[punteroAXadre] = nodoXadre
        
    def agregarPunteroANodoInterno(self, nodoInterno, numPagina, nodo):
        ultimoRegistroDelNodo = nodo.registros[-1]
        idUltimoRegistroDelNodo = int.from_bytes(ultimoRegistroDelNodo[:4], byteorder="big")
        punteroHijeDerecho = int.from_bytes(nodoInterno.punteroAHijeDerecho, byteorder="big")
        nodoInterno.punteros[numPagina] = idUltimoRegistroDelNodo
        # ordeno los punteros
        nodoInterno.punteros = dict(sorted(nodoInterno.punteros.items(), key=operator.itemgetter(1)))

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

    def cantidadDeRegistrosGuardados(self, numPagina):
        self.paginador.obtenerPagina(numPagina)
        nodo = self.paginador.cache[numPagina]
        cantidadDeRegistrosTotal = 0
        esNodoHoja = bool.from_bytes(nodo.tipoDeNodo)
        if esNodoHoja:
            cantidadDeRegistrosTotal += self.getCantidadDeRegistrosPagina(nodo)
        else:
            punteros = nodo.punteros
            punteroHijeDerecho = int.from_bytes(nodo.punteroAHijeDerecho, byteorder="big")
            for numPagina in punteros.keys():
                cantidadDeRegistrosTotal += self.cantidadDeRegistrosGuardados(numPagina)
            cantidadDeRegistrosTotal += (self.cantidadDeRegistrosGuardados(punteroHijeDerecho))
        return cantidadDeRegistrosTotal
    
    def guardarRegistrosEnBaseDeDatos(self):
        self.paginador.actualizarArchivo()

    def obtenerTodosLosRegistrosDeserializados(self):
        registros = self.obtenerTodosLosRegistros(1)
        registrosDeserializados = ""
        for registro in registros:
            registro = registro[4:]
            registroDeserializado = self.deserializar(registro)
            registrosDeserializados += registroDeserializado
            if registro[:4] != registros[-1][:4]:
                registrosDeserializados += "\n"
        return registrosDeserializados

    def obtenerTodosLosRegistros(self, numPagina):
        self.paginador.obtenerPagina(numPagina)
        nodo = self.paginador.cache[numPagina]
        registros = []
        esNodoHoja = bool.from_bytes(nodo.tipoDeNodo)
        if esNodoHoja:
            registros.extend(nodo.registros)
        else:
            punteros = nodo.punteros
            punteroHijeDerecho = int.from_bytes(nodo.punteroAHijeDerecho, byteorder="big")
            for numPagina in punteros.keys():
                registros.extend(self.obtenerTodosLosRegistros(numPagina))
            registros.extend(self.obtenerTodosLosRegistros(punteroHijeDerecho))
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
    
    def getEsRaiz(self, nodo):
        esRaiz = bool.from_bytes(nodo.esRaiz)
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