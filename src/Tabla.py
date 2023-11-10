from src.Paginador import Paginador
from src.NodoHoja import NodoHoja
import operator

class Tabla:

    def __init__(self, paginador):
        self.paginador = paginador
    
    def paginaNueva(self):
        if len(self.paginador.cache) == 0:
            return self.cantPaginasBaseDeDatos() + 1
        else:
            mayorPaginaEnCache = max(self.paginador.cache.keys())
            return max(self.cantPaginasBaseDeDatos(), mayorPaginaEnCache) + 1
    
    def cantPaginasBaseDeDatos(self):
        tamanioBaseDatos = self.paginador.tamanioBaseDatos
        paginasEnArchivo = int(tamanioBaseDatos / 4096)
        if len(self.paginador.cache) == 0:
            return paginasEnArchivo
        else:
            mayorPaginaEnCache = max(self.paginador.cache.keys())
            return max(paginasEnArchivo, mayorPaginaEnCache)
        
    # recorre de forma recursiva el arbol hasta encontrar el nodo hoja que debe alojar al registro
    def guardarRegistroEnCache(self, registro, numPagina):
        registroSerializado = self.serializar(registro)
        idRegistro = int.from_bytes(registroSerializado[:4], byteorder="big")
        # paso pagina a cache y obtengo el nodo
        self.paginador.obtenerPagina(numPagina)
        nodo = self.paginador.cache[numPagina]
        esNodoHoja = (1 == self.getTipoNodo(nodo))
        # - si el nodo es hoja y el id ya se encuentra en el arbol, se devuelve un mensaje de Invalido
        # - si el nodo es hoja y el id no existe en el arbol, se agrega el registro
        # - si el nodo es interno, se recorre su conjunto de nodos hijos y se vuelve a llamar 
        # a este metodo sobre el nodo hijo correspondiente
        if esNodoHoja:
            if idRegistro in nodo.elementos:
                return "Inválido"
            else:
                self.agregarElementoANodo(numPagina, nodo, idRegistro, registroSerializado)
                return "INSERT exitoso"
        else:
            numPaginaAEscribir = None
            for pagina, id in nodo.elementos.items():
                if id > idRegistro:
                    numPaginaAEscribir = pagina
                    break
            if numPaginaAEscribir == None:
                punteroDerecho = int.from_bytes(nodo.punteroAHijeDerecho, byteorder = "big")
                numPaginaAEscribir = punteroDerecho
            return self.guardarRegistroEnCache(registro, numPaginaAEscribir)

    # Dado un nodo y su numero de pagina correspondiente, agrega el elemento con su id a la 
    # lista de elementos del nodo. Deja la lista de elementos ordenada por el id de los 
    # elementos y actualiza la cantidad de elementos del nodo.
    # Si agregar el elemento a la lista excedera la capacidad de la misma, se divide el 
    # nodo agregandose los nodos nuevos de forma recursiva
    def agregarElementoANodo(self, numPagina, nodo, idElemento, elemento):
        if (not nodo.estaCompleto()) or (idElemento in nodo.elementos):
            if not (idElemento in nodo.elementos): 
                cantDeElementos = self.getCantidadDeElementos(nodo)
                cantDeElementos += 1
                self.setCantidadDeElementosDeNodo(nodo, cantDeElementos)
            nodo.elementos[idElemento] = elemento
            nodo.elementos = dict(sorted(nodo.elementos.items(), key=operator.itemgetter(1)))
            self.paginador.cache[numPagina] = nodo
        else:
            nodo.dividirNodo(self, numPagina, idElemento, elemento)

    # split del nodo hoja
    def dividirNodoHoja(self, numPaginaNodo, nodo, idRegistro, registroSerializado):
        esRaiz = self.getEsRaiz(nodo)
        registros = nodo.elementos
        registros[idRegistro] = registroSerializado
        registros = dict(sorted(registros.items(), key=operator.itemgetter(1)))
        registros = registros.items()
        if esRaiz:
            # primer nodo: una pagina nueva
            numPrimerNodo = self.paginador.obtenerPagina(self.paginaNueva())
            primerNodo = self.paginador.cache[numPrimerNodo]
            # nodo xadre: el nodo raiz
            punteroAXadre = numPaginaNodo
            nodoXadre = nodo.convertirEnNodoInterno()
        else:
            # primer nodo: el nodo original pasado por parametro
            numPrimerNodo = numPaginaNodo
            primerNodo = self.paginador.cache[numPaginaNodo]
            # nodo xadre: el nodo xadre del nodo original
            punteroAXadre = self.getPunteroAXadre(nodo)
            nodoXadre = self.paginador.cache[punteroAXadre]    
        # segundo nodo: una pagina nueva para ambos casos
        numSegundoNodo = self.paginador.obtenerPagina(self.paginaNueva())
        segundoNodo = self.paginador.cache[numSegundoNodo]
        # se actualizan los registros y cantidad de reg en ambos nodos
        primerNodo.elementos = dict(list(registros)[:len(registros)//2])
        segundoNodo.elementos = dict(list(registros)[len(registros)//2:])
        self.setCantidadDeElementosDeNodo(primerNodo, 7)
        self.setCantidadDeElementosDeNodo(segundoNodo, 7)
        # se completa puntero a nodo xadre en el nodo nuevo
        self.setPunteroAXadre(segundoNodo, punteroAXadre)
        # agrego puntero de nodo nuevo en nodo xadre
        # si el nodo original era hije derecho, este puntero se reemplaza con el segundo nodo
        # caso contrario solo se agrega a la lista de nodos
        punteroHijeDerecho = int.from_bytes(nodoXadre.punteroAHijeDerecho, byteorder="big")
        if punteroHijeDerecho == numPaginaNodo or esRaiz:
            self.setPunteroAHijeDerecho(nodoXadre, numSegundoNodo)
        else:
            idUltimoRegistroDelSegundoNodo = list(segundoNodo.elementos)[-1]
            self.agregarElementoANodo(punteroAXadre, nodoXadre, numSegundoNodo, idUltimoRegistroDelSegundoNodo)
        # actualizo puntero nodo anterior en nodo xadre; si ya se encuentra en la lista se reemplaza, 
        # y si no se agrega de cero
        self.setPunteroAXadre(primerNodo, punteroAXadre)
        idUltimoRegistroDelNodoRaiz = list(primerNodo.elementos)[-1]
        self.agregarElementoANodo(punteroAXadre, nodoXadre, numPrimerNodo, idUltimoRegistroDelNodoRaiz)
        # ordeno los punteros del nodo xadre
        nodoXadre.elementos = dict(sorted(nodoXadre.elementos.items(), key=operator.itemgetter(1)))
        # actualizo los tres nodos en la cache del paginador
        self.paginador.cache[numSegundoNodo] = segundoNodo
        self.paginador.cache[numPrimerNodo] = primerNodo
        self.paginador.cache[punteroAXadre] = nodoXadre

    # split nodo interno
    def dividirNodoInterno(self, numPaginaNodo, nodo, punteroANodoHije, idRegistroMayorDelNodoHijo):
        esRaiz = self.getEsRaiz(nodo)
        punterosANodosHijos = nodo.elementos
        punterosANodosHijos[punteroANodoHije] = idRegistroMayorDelNodoHijo
        punterosANodosHijos = dict(sorted(punterosANodosHijos.items(), key=operator.itemgetter(1)))
        punterosANodosHijos = punterosANodosHijos.items()
        punteroAHijeDerecho = int.from_bytes(nodo.punteroAHijeDerecho, byteorder="big")
        if esRaiz:
            # primer nodo: un nodo nuevo
            numPrimerNodo = self.paginador.obtenerPagina(self.paginaNueva())
            primerNodo = self.paginador.cache[numPrimerNodo]
            primerNodo = primerNodo.convertirEnNodoInterno()
            # nodo xadre: el nodo raiz (se resetea a cero su lista y cantidad de punteros)
            punteroAXadre = numPaginaNodo
            nodoXadre = nodo
            self.setCantidadDeElementosDeNodo(nodoXadre, 0)
            nodoXadre.elementos = {}
        else:
            # primer nodo: nodo pasado por parametro
            numPrimerNodo = numPaginaNodo
            primerNodo = self.paginador.cache[numPaginaNodo]
            # nodo xadre: nodo xadre del nodo pasado por parametro
            punteroAXadre = self.getPunteroAXadre(nodo)
            nodoXadre = self.paginador.cache[punteroAXadre]    
        # segundo nodo: nodo nuevo
        numSegundoNodo = self.paginador.obtenerPagina(self.paginaNueva())
        segundoNodo = self.paginador.cache[numSegundoNodo]
        segundoNodo = segundoNodo.convertirEnNodoInterno()
        # se actualizan los punteros y su cantidad en ambos nodos hijos
        cantElementosMitad = len(punterosANodosHijos)//2
        primerNodo.elementos = dict(list(punterosANodosHijos)[:cantElementosMitad])
        segundoNodo.elementos = dict(list(punterosANodosHijos)[cantElementosMitad+1:])
        self.setCantidadDeElementosDeNodo(primerNodo, cantElementosMitad)
        self.setCantidadDeElementosDeNodo(segundoNodo, cantElementosMitad)
        # se completan los punteros a hijes derechos
        ultimoElementoPrimerNodo = list(punterosANodosHijos)[cantElementosMitad:cantElementosMitad+1]
        self.setPunteroAHijeDerecho(primerNodo, ultimoElementoPrimerNodo[0][0])
        self.setPunteroAHijeDerecho(segundoNodo, punteroAHijeDerecho)
        # se actualizan nodos xadres de cada nodo hijo del primero nodo
        for numPagina in primerNodo.elementos.keys():
            self.paginador.obtenerPagina(numPagina)
            nodoHije = self.paginador.cache[numPagina]
            self.setPunteroAXadre(nodoHije, numPrimerNodo)
            self.paginador.cache[numPagina] = nodoHije
        ultimoNodoPrimerNodo = self.paginador.cache[ultimoElementoPrimerNodo[0][0]]
        self.setPunteroAXadre(ultimoNodoPrimerNodo, numPrimerNodo)
        self.paginador.cache[ultimoElementoPrimerNodo[0][0]] = ultimoNodoPrimerNodo
        # se actualizan nodos xadres de cada nodo hijo del segundo nodo
        for numPagina in segundoNodo.elementos.keys():
            self.paginador.obtenerPagina(numPagina)
            nodoHije = self.paginador.cache[numPagina]
            self.setPunteroAXadre(nodoHije, numSegundoNodo)
            self.paginador.cache[numPagina] = nodoHije
        self.paginador.obtenerPagina(punteroAHijeDerecho)
        hijeDerechoSegundoNodo = self.paginador.cache[punteroAHijeDerecho]
        self.setPunteroAXadre(hijeDerechoSegundoNodo, numSegundoNodo)
        self.paginador.cache[punteroAHijeDerecho] = hijeDerechoSegundoNodo
        # se completa puntero a nodo xadre
        self.setPunteroAXadre(segundoNodo, punteroAXadre)
        # agrego puntero de nodo nuevo en nodo xadre
        punteroHijeDerecho = int.from_bytes(nodoXadre.punteroAHijeDerecho, byteorder="big")
        if punteroHijeDerecho == numPaginaNodo or esRaiz:
            self.setPunteroAHijeDerecho(nodoXadre, numSegundoNodo)
        else:
            self.agregarElementoANodo(punteroAXadre, nodoXadre, numSegundoNodo, nodoXadre.elementos[numPrimerNodo])
        # chequeo si cambio nodo xadre
        punteroAXadreActualizado = self.getPunteroAXadre(segundoNodo)
        if punteroAXadre != punteroAXadreActualizado:
            nodoXadre.elementos = dict(sorted(nodoXadre.elementos.items(), key=operator.itemgetter(1)))
            self.paginador.cache[punteroAXadre] = nodoXadre
            punteroAXadre = punteroAXadreActualizado
            self.paginador.obtenerPagina(punteroAXadreActualizado)
            nodoXadre = self.paginador.cache[punteroAXadreActualizado]
        # actualizo puntero nodo anterior en nodo xadre
        self.setPunteroAXadre(primerNodo, punteroAXadre)
        self.agregarElementoANodo(punteroAXadre, nodoXadre, numPrimerNodo, ultimoElementoPrimerNodo[0][1])
        # ordeno los punteros del nodo xadre
        nodoXadre.elementos = dict(sorted(nodoXadre.elementos.items(), key=operator.itemgetter(1)))
        # actualizo los tres nodos en la cache del paginador
        self.paginador.cache[numSegundoNodo] = segundoNodo
        self.paginador.cache[numPrimerNodo] = primerNodo
        self.paginador.cache[punteroAXadre] = nodoXadre

    def cantidadDeRegistrosGuardados(self, numPagina):
        self.paginador.obtenerPagina(numPagina)
        nodo = self.paginador.cache[numPagina]
        cantidadDeRegistrosTotal = 0
        esNodoHoja = (1 == self.getTipoNodo(nodo))
        if esNodoHoja:
            cantidadDeRegistrosTotal += self.getCantidadDeElementos(nodo)
        else:
            punteros = nodo.elementos
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
            #registro = registro[4:]
            registroDeserializado = self.deserializar(registro)
            registrosDeserializados += registroDeserializado
            if registro[:4] != registros[-1][:4]:
                registrosDeserializados += "\n"
        return registrosDeserializados

    def obtenerTodosLosRegistros(self, numPagina):
        self.paginador.obtenerPagina(numPagina)
        nodo = self.paginador.cache[numPagina]
        registros = []
        esNodoHoja = (1 == self.getTipoNodo(nodo))
        if esNodoHoja:
            registros.extend(nodo.elementos.values())
        else:
            punteros = nodo.elementos
            punteroHijeDerecho = int.from_bytes(nodo.punteroAHijeDerecho, byteorder="big")
            for numPagina in punteros.keys():
                registros.extend(self.obtenerTodosLosRegistros(numPagina))
            registros.extend(self.obtenerTodosLosRegistros(punteroHijeDerecho))
        return registros
        
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
    
    def getTipoNodo(self, nodo):
        return nodo.getTipoDeNodo()
    
    def getEsRaiz(self, nodo):
        return nodo.getEsRaiz()
    
    def getPunteroAXadre(self, nodo):
        return nodo.getPunteroAXadre()
    
    def setPunteroAXadre(self, nodoHoja, numPagina):
        punteroAXadreSerializado = numPagina.to_bytes(4, byteorder="big")
        nodoHoja.punteroAXadre = punteroAXadreSerializado
    
    def setPunteroAHijeDerecho(self, nodoInterno, numPagina):
        punteroAHijeDerechoSerializado = numPagina.to_bytes(4, byteorder="big")
        nodoInterno.punteroAHijeDerecho = punteroAHijeDerechoSerializado
    
    def getCantidadDeElementos(self, nodo):
        return nodo.getCantidadDeElementos()

    def setCantidadDeElementosDeNodo(self, nodo, cantDeElementosActualizada):
        cantidadDeRegistrosSerializado = cantDeElementosActualizada.to_bytes(4, byteorder="big")
        nodo.cantidadDeElementos = cantidadDeRegistrosSerializado

    def setRegistroEn(self, nodoHoja, posicion, registro):
        nodoHoja.insertarRegistroEn(posicion, registro)