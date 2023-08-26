from Compilador import Compilador

def correrRepl():
    compilador = Compilador()

    query = input("sql>")
    while query is not None:
        compilador.interpretar(query)
        query = input("sql>")

def main():
    correrRepl()

if __name__ == "__main__":
    main()
