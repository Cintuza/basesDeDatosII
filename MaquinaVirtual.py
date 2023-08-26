class MaquinaVirtual:
    
    def ejecutarMetacomando(self, query):
        if query == ".exit":
            print("Terminado")
            exit()
        else:
            print(query + " no es un comando valido")

    def ejecutarSentenciaSQL(self, query):
        if query.startswith("SELECT"):
            print("SELECT no implementado")
        elif query.startswith("INSERT"):
            print("INSERT no implementado")
        else:
            print(query + " no es una sentencia valida")
