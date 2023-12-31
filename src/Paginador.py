import os
from src.NodoHoja import NodoHoja
from src.NodoInterno import NodoInterno

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
        self.direccionBaseDatos = nombreBaseDeDatos
        with open(self.direccionBaseDatos, "ab+") as baseDeDatos:
            self.baseDeDatos = baseDeDatos
            self.tamanioBaseDatos = os.path.getsize(self.direccionBaseDatos)
        if self.tamanioBaseDatos == 0:
            pagina = b'\x01\x01' + bytearray(4094)
            self.cache[1] = NodoHoja(pagina)

    def obtenerPagina(self, numDePagina):
        if not (numDePagina in self.cache):
            self.__pasarPaginaACache(numDePagina)
        return numDePagina
        
    def __pasarPaginaACache(self, numPagina):
        posicionInicial = 4096 * (numPagina - 1)
        pagina = bytearray()
        if posicionInicial < self.tamanioBaseDatos:
            with open(self.direccionBaseDatos, "rb") as baseDeDatos:
                pagina = baseDeDatos.read()[posicionInicial:posicionInicial+4096]
        else:
            pagina = b'\x01\x00' + bytearray(4094)
        if pagina[:1] == b'\x00':
            self.cache[numPagina] = NodoInterno(pagina)
        else:
            self.cache[numPagina] = NodoHoja(pagina)

    def actualizarArchivo(self):
        if len(self.cache) != 0:
            with open(self.direccionBaseDatos, "rb+") as baseDeDatos:
                for numNodo, nodo in self.cache.items():
                    posicion = 4096 * (numNodo - 1)
                    pagina = nodo.pasarNodoAPagina()
                    baseDeDatos.seek(posicion)
                    baseDeDatos.write(pagina)