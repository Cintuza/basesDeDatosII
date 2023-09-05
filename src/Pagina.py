class Pagina:

    def __init__(self):
        self.datos = bytearray()

    def guardarRegistro(self, registro):
        if not self.estaCompleta():
            self.datos += registro

    def cantidadDeRegistrosGuardados(self):
        return len(self.datos) // 291

    def estaCompleta(self):
        return self.cantidadDeRegistrosGuardados() == 14
    
    def obtenerRegistro(self, posicionInicial):
        if posicionInicial != len(self.datos):
            return self.datos[posicionInicial:posicionInicial+291]
        
    def obtenerTodosLosRegistros(self):
        posicionInicial = 0
        registros = []
        while posicionInicial < len(self.datos):
            registro = self.datos[posicionInicial:posicionInicial+291]
            registros.append(registro)
            posicionInicial += 291
        return registros