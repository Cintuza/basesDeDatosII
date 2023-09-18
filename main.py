from src.Compilador import Compilador
from src.MaquinaVirtual import MaquinaVirtual
from src.Tabla import Tabla
from src.Paginador import Paginador

import sys
import os

paginador = Paginador()
tablaDeMemoria = Tabla(paginador)
maquinaVirtual = MaquinaVirtual(tablaDeMemoria)
compilador = Compilador(maquinaVirtual)

def correrRepl():
    query = input("sql>")
    while query is not None:
        compilador.interpretar(query)
        query = input("sql>")

def main():
    nombreBaseDatos = sys.argv[1]
    paginador.abrirBase(nombreBaseDatos)
    correrRepl()

if __name__ == "__main__":
    main()
