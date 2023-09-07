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
        if query.lower() == "select":
            print(self.obtenerTodosRegistros())
        elif query.lower().startswith("insert"):
            registro = query[7:]
            self.insertarRegistro(registro)
        else:
            print("Inválido")
   
    def registroEsValido(self, registro):
        cantidadElementosRegistro = len(registro.split(" "))
        if cantidadElementosRegistro == 3:
            return True
        else:
            return False

    def insertarRegistro(self, registro):
        if self.registroEsValido(registro):
            self.tabla.guardarRegistroEnPagina(registro)
            print("INSERT exitoso")
        else:
            print("Operación inválida")

    def obtenerTodosRegistros(self): 
        return self.tabla.obtenerTodosLosRegistrosDeserializados()
