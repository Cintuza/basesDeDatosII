from src.Tabla import Tabla

class MaquinaVirtual:
    
    def __init__(self, tabla):
        self.tabla = tabla
    
    def ejecutarMetacomando(self, query):
        if query == ".exit":
            self.tabla.guardarRegistrosEnBaseDeDatos()
            print("Terminado")
            exit()
        elif query == ".table-metadata":
            print("Paginas: " + str(self.tabla.cantPaginasBaseDeDatos()) + "\n" + "Registros: " + str(self.tabla.cantidadDeRegistrosGuardados()))
        else:
            print(query + " no es un comando valido")

    def ejecutarSentenciaSQL(self, query):
        if query.lower() == "select":
            print(self.obtenerTodosRegistros())
        elif query.lower().startswith("insert"):
            registro = query[7:]
            self.insertarRegistro(registro)
        else:
            print("Inválido")
   
    def registroEsValido(self, registro):
        elementosDelRegistro = registro.split(" ")
        cantidadElementosRegistro = len(elementosDelRegistro)
        if (cantidadElementosRegistro == 3) and (elementosDelRegistro[0].isnumeric()):
            return True
        else:
            return False

    def insertarRegistro(self, registro):
        if self.registroEsValido(registro):
            self.tabla.guardarRegistroEnCache(registro)
            print("INSERT exitoso")
        else:
            print("Operación inválida")

    def obtenerTodosRegistros(self): 
        return self.tabla.obtenerTodosLosRegistrosDeserializados()
