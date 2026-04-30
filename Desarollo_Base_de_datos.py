import sqlite3
from datetime import datetime

# --- CLASES DE DATOS ---
class Medico:
    def __init__(self, id_medico, nombre, especialidad):
        self.id = id_medico
        self.nombre = nombre
        self.especialidad = especialidad
        
    def __str__(self):
        return f"Dr. {self.nombre} | Especialidad: {self.especialidad}"

class Socio:
    def __init__(self, nombre, apellido, numero_socio, dni, nacionalidad, telefono, domicilio):
        self.nombre = nombre
        self.apellido = apellido
        self.numero_socio = numero_socio
        self.dni = dni
        self.nacionalidad = nacionalidad
        self.telefono = telefono
        self.domicilio = domicilio

    def __str__(self):
        return f"Nombre: {self.nombre} {self.apellido} | N° Socio: {self.numero_socio} | DNI: {self.dni}"

# --- Lógica de la base de datos ---

class Clinica():
    def __init__(self, db_name="clinica.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._crear_tablas()
        self._seed_medicos()

    def _crear_tablas(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS socios (
            numero_socio TEXT PRIMARY KEY, nombre TEXT, apellido TEXT,
            dni TEXT, nacionalidad TEXT, telefono TEXT, domicilio TEXT)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, especialidad TEXT)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS turnos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, socio_id TEXT, medico_id INTEGER,
            fecha_hora TEXT, FOREIGN KEY(socio_id) REFERENCES socios(numero_socio),
            FOREIGN KEY(medico_id) REFERENCES medicos(id))''')
        self.conn.commit()

    def _seed_medicos(self):
        self.cursor.execute('''SELECT COUNT(*) FROM medicos''')
        if self.cursor.fetchone()[0] == 0:
            # Corregido: nombre de columna 'especialidad'
            medicos = [("García", "Pediatría"), ("Lopez", "Cardiologia"), ("Martinez", "Dermatologia")]
            self.cursor.executemany('''INSERT INTO medicos (nombre, especialidad) VALUES (?,?)''', medicos)
            self.conn.commit()

    def registrar_socio(self, s):
        try:
            self.cursor.execute('''INSERT INTO socios VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                (s.numero_socio, s.nombre, s.apellido, s.dni, s.nacionalidad, s.telefono, s.domicilio))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
            
    # Agregado: Método faltante para buscar socio
    def buscar_socio(self, numero):
        self.cursor.execute("SELECT * FROM socios WHERE numero_socio = ?", (numero,))
        row = self.cursor.fetchone()
        if row:
            return Socio(row[1], row[2], row[0], row[3], row[4], row[5], row[6])
        return None

    def buscar_medico(self, nombre):
        self.cursor.execute('''SELECT * FROM medicos WHERE nombre LIKE ?''', (f"%{nombre}%",))
        row = self.cursor.fetchone()
        if row:
            return Medico(row[0], row[1], row[2])
        return None

    def listar_medicos(self):
        self.cursor.execute('''SELECT nombre FROM medicos''')
        # Corregido: fetchall()
        return [m[0] for m in self.cursor.fetchall()]

    def agendar_turno(self, socio_id, medico_id, fecha_hora_str):
        # Corregido: Quitada la coma extra al final de los VALUES
        self.cursor.execute('''INSERT INTO turnos (socio_id, medico_id, fecha_hora) VALUES (?, ?, ?)''', 
                            (socio_id, medico_id, fecha_hora_str))
        self.conn.commit()

    def ver_todos_los_turnos(self):
        # Corregido: Alias 't', comas extras y estructura de JOIN
        query = '''SELECT turnos.id, medicos.nombre, medicos.especialidad, socios.nombre, socios.apellido, turnos.fecha_hora 
                   FROM turnos 
                   JOIN medicos ON turnos.medico_id = medicos.id
                   JOIN socios ON turnos.socio_id = socios.numero_socio'''
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if not rows:
            print("No hay turnos agendados.")
        for r in rows:
            print(f"Turno ID: {r[0]} | Paciente: {r[3]} {r[4]} | Medico: {r[1]} | Especialidad: {r[2]} | Fecha: {r[5]}")

# --- Interfaz de Recepcionista ---
def menu_recepcionista(clinica):
    while True:
        print("\n--- MENU ---")
        print("1. Registrar nuevo socio")
        print("2. Buscar socio")
        print("3. Agendar turno")
        print("4. Ver todos los turnos")
        print("7. Salir")

        opcion = input("Seleccione una opcion: ")

        if opcion == "1":
            nom = input("Nombre: "); ape = input("Apellido: ")
            num_socio = input("Numero de socio: "); dni = input("DNI: ")
            nac = input("Nacionalidad: "); tel = input("Telefono: ")
            dom = input("Domicilio: ")
            nuevo_socio = Socio(nom, ape, num_socio, dni, nac, tel, dom)
            
            if clinica.registrar_socio(nuevo_socio):
                print(f"Socio {ape} registrado con éxito.")
            else:
                print("ERROR: El número de socio ya existe.")

        elif opcion == "2":
            num = input("Ingrese el número de socio: ")
            s = clinica.buscar_socio(num)
            print(s if s else "Socio no encontrado.")

        elif opcion == "3":
            num_s = input("Número de socio: ")
            socio = clinica.buscar_socio(num_s)
            if socio:
                print("Médicos disponibles: ", clinica.listar_medicos())
                nom_m = input("Nombre del médico: ")
                medico = clinica.buscar_medico(nom_m)
                if medico:
                    fec = input("Fecha (DD/MM/AAAA): ")
                    hor = input("Hora (HH:MM): ")
                    try:
                        dt = datetime.strptime(f"{fec} {hor}", "%d/%m/%Y %H:%M")
                        dt_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                        clinica.agendar_turno(num_s, medico.id, dt_str)
                        print("Turno agendado con éxito.")
                    except ValueError:
                        print("Formato de fecha u hora inválido.")
                else:
                    print("Médico no encontrado.")
            else:
                print("Socio no existe.")

        elif opcion == "4":
            clinica.ver_todos_los_turnos()

        elif opcion == "7": 
            print("Saliendo del sistema...")
            break

mi_clinica = Clinica()
menu_recepcionista(mi_clinica)