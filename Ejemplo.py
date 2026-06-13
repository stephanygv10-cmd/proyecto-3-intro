# seccion 1, pregunta 1
def izquierda_vs_derecha(num, i):
    if i > num:
        return 0
    else:
        return 0

#seccion 2, pregunta 2
def elementos_unicos(lista):
    return elementos_unicos_aux(lista, 0, [])

def elementos_unicos_aux(lista, i, no_repetidos):
    if i == len(lista):
        return 0

    elif lista[i] not in (lista[i:]):
        no_repetidos.append(lista[i])
        return elementos_unicos(lista, i + 1, no_repetidos)

    else:
        return elementos_unicos(lista, i, no_repetidos)


#seccion 2, POO

class Nave:
    def __init__(self, nombre, tipo, nivel, energia_actual, potencia):
        self.nombre = nombre
        self.tipo = tipo
        self.nivel = nivel
        self.energia_maxima = 100
        self.energia_actual = energia_actual
        self.potencia = potencia

    def mejorar(self):
        self.nivel += 1

    def mostrar(self):
        print(f"Nombre: {self.nombre} \n Tipo: {self.tipo}\n Nivel: {self.nivel}"
              f"\nEnergia: {self.energia_actual}/{self.energia_maxima}"
              f"\n Potencia: {self.potencia}")

class Explorador:
    def __init__(self, nombre):
        self.nombre = nombre
        self.insignias = 0
        self.flota = []

    def agregar_nave(self, nave):
        if len(self.flota) < 5 :
            self.flota.append(nave)

        else:
            print("Ya no puede ingresar mas naves a la flota, esta lleno")

    def mejorar_flota(self):
        for m in self.flota:
            m.mejorar()
        suma = 0
        for m in self.flota:
            suma += m.nivel
        self.insignias = suma //5


    def mostrar_flota(self):
        print(f"Nombre del explorador: {self.nombre}\n Cantidad de insignias: {self.insignias}")

        for mos in self.flota:
            mos.mostrar()

#crear las naves
halcon = Nave("Halcón Estelar", "Caza", 5, 100, 22)
orion = Nave("Orion", "Exploración", 4, 90, 18)
atlas = Nave("Atlas", "Carga", 4, 95, 16)
fenix = Nave("Fénix", "Defensa", 4, 100, 17)
pegaso = Nave("Pegaso", "Transporte", 3, 70, 12)
nova = Nave("Nova", "Caza", 5, 85, 20)

#crear explorador
leo = Explorador("Leo")

#agregar naves
leo.agregar_nave(halcon)
leo.agregar_nave(orion)
leo.agregar_nave(atlas)
leo.agregar_nave(fenix)
leo.agregar_nave(pegaso)
leo.agregar_nave(nova)

#Llamar a mejorar flota
print(f"Mostrar flota:")
leo.mostrar_flota()

#Llamar 4 veces a mejorar flota

for i in range(4):
    leo.mejorar_flota()
#Llamar nuevamente a metodo mostrar_flota
print(f"Mostrar flota despues:")
leo.mostrar_flota()



# comentarios: mied