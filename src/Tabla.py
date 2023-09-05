from src.Pagina import Pagina

class Tabla:

    paginas = []

    def ultimaPagina(self):
        return self.paginas[-1]

    def paginaAEscribir(self):
        if (len(self.paginas) == 0) or (self.ultimaPagina().estaCompleta()):
            paginaNueva = Pagina()
            self.paginas.append(paginaNueva)
            return paginaNueva
        else:
            return self.ultimaPagina()
        
    def guardarRegistroEnPagina(self, registro):
        pagina = self.paginaAEscribir()
        pagina.guardarRegistro(registro)

    def cantidadDeRegistrosGuardados(self):
        if len(self.paginas) == 0:
            return 0
        else:
            paginasCompletas = len(self.paginas) - 1
            cantidadRegistrosUltimaPagina = self.ultimaPagina().cantidadDeRegistrosGuardados()
            return (paginasCompletas * 14) + cantidadRegistrosUltimaPagina
    
    def obtenerTodosLosRegistros(self):
        registros = []
        for pagina in self.paginas:
            registros.extend(pagina.obtenerTodosLosRegistros())
        return registros