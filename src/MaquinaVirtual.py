from src.Tabla import Tabla

class MaquinaVirtual:
    
    def __init__(self, tabla):
        self.tabla = tabla
    
    def ejecutarMetacomando(self, query):
        if query == ".exit":
            print("Terminado")
            exit()
        elif query == ".table-metadata":
            print("Paginas: " + str(len(self.tabla.paginas)) + "\n" + "Registros: " + str(self.tabla.cantidadDeRegistrosGuardados()))
        else:
            print(query + " no es un comando valido")

    def ejecutarSentenciaSQL(self, query):
        if query.lower().startswith("select"):
            print(self.obtenerTodosLosRegistrosDeserializados())
            print(self.tabla.cantidadDeRegistrosGuardados())
            print(len(self.tabla.paginas))
        elif query.lower().startswith("insert"):
            registro = query[7:]
            self.insertarRegistro(registro)
        else:
            print(query + " no es una sentencia valida")

    def insertarRegistro(self, registro):
        registroSerializado = self.serializar(registro)
        self.tabla.guardarRegistroEnPagina(registroSerializado)

    # 
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
    
    def obtenerTodosLosRegistrosDeserializados(self):
        registros = self.tabla.obtenerTodosLosRegistros()
        registrosDeserializados = ""
        for registro in registros:
            registroDeserializado = self.deserializar(registro)
            registrosDeserializados += registroDeserializado
            if registro != registros[-1]:
                registrosDeserializados += "\n"
        return registrosDeserializados

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