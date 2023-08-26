
from MaquinaVirtual import MaquinaVirtual

class Compilador:

    maquinaVirtual = MaquinaVirtual()

    ## Si la query empieza con un punto (.) le pide a la maquina virtual que
    ## ejecute la query como un metacomando. Caso contrario le pide a la 
    ## maquina virtual que ejecute la query como sentencia SQL
    
    def interpretar(self, query):
        if query.startswith("."):
            self.maquinaVirtual.ejecutarMetacomando(query)
        else:
            self.maquinaVirtual.ejecutarSentenciaSQL(query)

   