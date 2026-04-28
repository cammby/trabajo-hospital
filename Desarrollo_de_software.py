from datetime import datetime, timedeltafrom

class Medico():
    def __init__(self, nombre, especialidad):
        self.nombre = nombre
        self.especialidad = especialidad
        
    def __str__(self):
        return f"Dr. {self.nombre} | Especialidad: {self.especialidad}"

class Socio():
    def __init__(self, nombre, apellido, numero_de_socio, dni, nacionalidad, telefono, domicilio):
        self.nombre = nombre
        self.apellido = apellido
        self.numero_de_socio = numero_de_socio
        self.dni = dni
        self.nacionalidad = nacionalidad
        self.telefono = telefono
        self.domicilio = domicilio

    def __str__(self):
        return f"Nombre: {self.nombre} {self.apellido} | N° Socio: {self.numero_de_socio} | DNI: {self.dni}"

    # Método para agregar al historial
    def agregar_al_historial(self, nota):
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        self.historial_medico.append(f"[{fecha_hoy}]: {nota}")

class Turno():
    def __init__(self, id_turno,medico_nom, socio_nom, fecha, hora):
        self.id_turno = id_turno
        self.medico = medico_nom
        self.socio = socio_nom
        self.fecha_completa = datetime.strptime(f"{fecha} {hora}", "%d/%m/%Y %H:%M")
        self.especialidad = medico_nom.especialidad

    def estado_del_turno(self):
        ahora = datetime.now()
        if self.fecha_completa < ahora:
            return "VENCIDO / FINALIZADO"
        elif self.fecha_completa > ahora:
            return "PROGRAMADO"
        else:
            return "EN CURSO"
        
    def __str__(self):
        fecha_legible = self.fecha_completa.strftime("%d/%m/%Y %H:%M Hs")
        estado = self.estado_del_turno() 
        return (f"\n--------COMPROBANTE DE TURNO---------\n"
                f"Estado: [{estado}]\n"
                f"Paciente: {self.socio.nombre} {self.socio.apellido}\n" 
                f"Médico: {self.medico.nombre}\n"
                f"Especialidad: {self.especialidad}\n"
                f"Fecha y Hora: {fecha_legible}\n"
                f"-----------------------------------")
    
class Clinica():
    
    def __init__(self):
        self.turnos = []
        self.socios = []
        self.medicos = []

    def buscar_socios(self, numero):
        for s in self.socios:
            if s.numero_socio == numero:
                return s
        return None
    
    def buscar_medico(self, nombre):
        for m in self.medicos:
            if m.nombre.lower() == nombre.lower():
                return
        return None
    
    def buscar_turnos_de_socio(self, numero_socio):
        return [t for t in self.turnos if t.socio.numero_socio == numero_socio]
    
def menu_recepcionista(clinica):
    while True:
        print("\n--- Sistema de recepcion---")
        print("1. Registrar nuevo paciente (Socio)")
        print("2. Ver lista de pacientes")
        print("3. Agendar Turno Nuevo")
        print("4. Reagendar Turno existentes")
        print("5. Ver todos los turnos")
        print("6. Cancelar Turno")
        print("7. Volver")

        op = input("Seleccione una opcion: ")

        if op == "1":
            nom = input("Nombre: ")
            ape = input("Apellido: ")
            num = input("Numero de socio: ")
            dni = input("DNI: ")
            nacionalida = input("Nacionalidad: ")
            telefono = input("Telefono: ")
            domicilio = input("Domicilio: ")
            nuevo = Socio(nom, ape, num, dni, nacionalida, domicilio, telefono)
            clinica.socios.append(nuevo)
            print(f"Paciente {ape} registrado con exito.")
        
        elif op == "2":
            if not clinica.socios:
                print("\nNo hay pacientes registrados.")
            else:
                print("\n---Lista de pacientes---")
                for socio in clinica.socios:
                    print(socio)

        elif op == "3":
            num_s = input("Numero de socio: ") 
            socio = clinica.buscar_socios(num_s)
            if socio:
                print("Medico disponibles:", [m.nombre for m in clinica.medicos])
                nom_m = input("Nombre del Medico: ")
                medico = clinica.buscar_medico(nom_m)
                if medico:
                    fec = input("Fecha (DD/MM/AAAA): ")
                    hor = input("Hora (HH:MM) ")
                    try:
                        dt = datetime.strptime(f"{fec} {hor}", "%d/%m/%Y %H:%M")
                        nuevo_turno = Turno(medico, socio, dt)
                        clinica.turnos.append(nuevo_turno)
                        print("Turno agendado correctamente.")
                    except:
                        print("Error: Formato de fecha u hora invalido.")
                else: print("Medico no encontrado.")
            else: print("El socio no existe.Registrelo primero.")

        elif op == "4":
            num_s = input("Ingrese el numero de socio: ")
            turnos_paciente = clinica.buscar_turnos_de_socio(num_s)

            if not turnos_paciente:
                print("Este paciente no tiene turnos programados. ")
            else:
                print("\nTurnos actuales del paciente: ")
                for i, t in enumerate(turnos_paciente):
                    print(f"{i+1}. {t}")

                indice = int(input("Seleccione el numero de turno a cambiar: ")) - 1
                if 0 <= indice < len(turnos_paciente):
                    nueva_fec = input("Nueva fecha (DD/MM/AAAA): ")
                    nueva_hor = input("Nueva hora HH/MM: ")
                    try:
                        nueva_dt = datetime.strptime(f"{nueva_fec} {nueva_hor}", "%d/%m/%Y %H:%M")
                        turnos_paciente[indice].fecha_hora = nueva_dt
                        print("Turno reagendado con exito.")
                    except:
                        print("Formato incorrecto.")
                else:
                    print("Seleccion invalida.")
        elif op == "7":break

mi_clinica = Clinica()
menu_recepcionista(mi_clinica)