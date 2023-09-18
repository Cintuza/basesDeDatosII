import os

class Paginador:

    def __init__(self):
        self.direccionBaseDatos = ""
        self.tamanioBaseDatos = 0
        self.cache = {}

    # Recibe el nombre del archivo que contiene la base de datos.
    # Si el archivo existe, se abre dicho archivo.
    # Si el archivo no existe, se crea de cero en la carpeta datos/
    # El archivo se abre con permisos para agregar datos y para leer el archivo.
    # Se asigna el archivo abierto a la variable baseDeDatos del paginador
    def abrirBase(self, nombreBaseDeDatos):
        self.direccionBaseDatos = "datos/" + nombreBaseDeDatos
        with open(self.direccionBaseDatos, "rb") as baseDeDatos:
            self.baseDeDatos = baseDeDatos
            self.tamanioBaseDatos = os.path.getsize(self.direccionBaseDatos)

    def obtenerPagina(self, numDePagina):
        if not (numDePagina in self.cache):
            self.__pasarPaginaACache(numDePagina)
        return numDePagina

    def getRegistros(self):
        with open(self.direccionBaseDatos, "rb") as registros:
            return registros.read()
        
    def __pasarPaginaACache(self, numPagina):
        posicionInicial = 4096 * (numPagina - 1)
        pagina = bytearray()
        with open(self.direccionBaseDatos, "rb") as baseDeDatos:
            if posicionInicial < self.tamanioBaseDatos:
                pagina = baseDeDatos.read()[posicionInicial:posicionInicial+4096]
        self.cache[numPagina] = pagina