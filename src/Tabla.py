from src.Pagina import Pagina
from src.Paginador import Paginador

class Tabla:

    def __init__(self, paginador):
        self.paginas = []
        self.paginador = paginador

    def ultimaPaginaEscrita(self):
        if len(self.paginador.cache) == 0:
            return self.cantPaginasBaseDeDatos()
        else:
            return max(self.paginador.cache.keys())

    def paginaAEscribir(self):
        if len(self.obtenerTodosLosRegistros()) % 14 == 0:
            return self.ultimaPaginaEscrita() + 1
        else:
            return self.ultimaPaginaEscrita()
        
    def guardarRegistroEnCache(self, registro):
        registroSerializado = self.serializar(registro)
        numPagina = self.paginador.obtenerPagina(self.paginaAEscribir())
        self.paginador.cache[numPagina] += registroSerializado
        if len(self.paginador.cache[numPagina]) == 4074:
            self.paginador.cache[numPagina] += b"\00"*22

    def cantidadDeRegistrosGuardados(self):
        tamanioBaseDatos = self.paginador.tamanioBaseDatos
        if (tamanioBaseDatos % 4096 == 0):
            return self.cantPaginasBaseDeDatos() * 14
        else:
            return int(tamanioBaseDatos / 4096) * 14 + int((tamanioBaseDatos % 4096) / 291)
        
    def guardarRegistrosEnBaseDeDatos(self):
        if self.cantPaginasBaseDeDatos() <= self.ultimaPaginaEscrita():
            paginas = []
            with open(self.paginador.direccionBaseDatos, "ab+") as baseDeDatos:
                posicion = 4096 * max((self.cantPaginasBaseDeDatos() - 1), 0)
                baseDeDatos.truncate(posicion)
                for numPagina in range(self.cantPaginasBaseDeDatos(), self.ultimaPaginaEscrita() + 1):
                    posicionPagina = self.paginador.obtenerPagina(numPagina)
                    pagina = self.paginador.cache[posicionPagina]
                    baseDeDatos.write(pagina)
    
    def obtenerTodasLasPaginas(self):
        paginas = []
        for numPagina in range(1, self.ultimaPaginaEscrita() + 1):
            posicionPagina = self.paginador.obtenerPagina(numPagina)
            pagina = self.paginador.cache[posicionPagina]
            paginas.append(pagina)
        return paginas

    def obtenerTodosLosRegistros(self):
        paginas = self.obtenerTodasLasPaginas()
        registros = []
        for pagina in paginas:
            posicionInicial = 0
            while (posicionInicial < 4074) and (posicionInicial < len(pagina)):
                registro = pagina[posicionInicial:posicionInicial+291]
                registros.append(registro)
                posicionInicial += 291
        return registros
        
    def serializar(self, registro):
        elementosDelRegistro = registro.split(" ")
        id = elementosDelRegistro[0]
        nombre = elementosDelRegistro[1]
        email = elementosDelRegistro[2]

        idSerializado = self.serializarId(id)
        nombreSerializado = self.serializarNombre(nombre)
        emailSerializado = self.serializarEmail(email)

        return idSerializado + nombreSerializado + emailSerializado
    
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

    def obtenerTodosLosRegistrosDeserializados(self):
        registros = self.obtenerTodosLosRegistros()
        registrosDeserializados = ""
        for registro in registros:
            registroDeserializado = self.deserializar(registro)
            registrosDeserializados += registroDeserializado
            if registro != registros[-1]:
                registrosDeserializados += "\n"
        return registrosDeserializados
    
    def cantPaginasBaseDeDatos(self):
        tamanioBaseDatos = self.paginador.tamanioBaseDatos
        if (tamanioBaseDatos % 4096 == 0):
            return int(tamanioBaseDatos / 4096)
        else:
            return int(tamanioBaseDatos / 4096) + 1