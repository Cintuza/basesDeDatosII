from src.Compilador import Compilador
from src.MaquinaVirtual import MaquinaVirtual
from src.Tabla import Tabla

def correrRepl():
    tablaDeMemoria = Tabla()
    maquinaVirtual = MaquinaVirtual(tablaDeMemoria)
    compilador = Compilador(maquinaVirtual)

    query = input("sql>")
    while query is not None:
        compilador.interpretar(query)
        query = input("sql>")

def main():
    correrRepl()

if __name__ == "__main__":
    main()
