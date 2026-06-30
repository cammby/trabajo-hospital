import sqlite3
import os
import uuid
import hashlib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

#--- Funciones goblales

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#--- CLASES 

class Usuario():
    def __init__(self, nombre, apellido, dni, genero, fecha_nacimiento, nacionalidad, telefono, domicilio, email, password):
        self.id_usuario = str(uuid.uuid4())
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.genero = genero
        self.fecha_nacimiento = fecha_nacimiento
        self.nacionalidad = nacionalidad
        self.telefono = telefono 
        self.domicilio = domicilio 
        self.email = email
        self.password = password


class Administrador(Usuario):
    def __init__(self,  nombre, apellido, dni, genero, fecha_nacimiento, nacionalidad, telefono, domicilio, email, password, nivel_acceso):
        super().__init__( nombre, apellido, dni, genero, fecha_nacimiento, nacionalidad, telefono, domicilio, email, password)
        self.nivel_acceso = nivel_acceso

class Recepcionista(Usuario):
    def __init__(self,  nombre, apellido, dni, genero, fecha_nacimiento, nacionalidad, telefono, domicilio, email, password, nivel_acceso):
        super().__init__( nombre, apellido, dni, genero, fecha_nacimiento, nacionalidad, telefono, domicilio, email, password)
        self.nivel_acceso = nivel_acceso

class Medico(Usuario):
    def __init__(self,  nombre, apellido, dni, genero, fecha_nacimiento, nacionalidad, telefono, domicilio, email, password, especialidad, nivel_acceso):
        super().__init__( nombre, apellido, dni, genero, fecha_nacimiento, nacionalidad, telefono, domicilio, email, password)
        self.especialidad = especialidad
        self.nivel_acceso = nivel_acceso

class Socio(Usuario):
    def __init__(self,  nombre, apellido, dni, genero, fecha_nacimiento, nacionalidad, telefono, domicilio, email, password, codigo_postal):
        super().__init__( nombre, apellido, dni, genero, fecha_nacimiento, nacionalidad, telefono, domicilio, email, password)
        self.codigo_postal = codigo_postal

class Clinica:
    def __init__(self, db_name="clinica.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread = False, timeout = 30)
        self._crear_tablas()
        self._seed_medicos()
        self._seed_recepcionistas()
        self._seed_administradores()
    
    def _crear_tablas(self):
        cursor = self.conn.cursor()
        cursor.execute("""
                      PRAGMA foreign_keys = ON;
                      """)
        
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS Administradores(
                       id TEXT PRIMARY KEY ,
                       nombre TEXT NOT NULL,
                       apellido TEXT NOT NULL,
                       dni TEXT NOT NULL UNIQUE,
                       genero TEXT,
                       fecha_nacimiento TEXT,
                       nacionalidad TEXT,
                       telefono TEXT,
                       domicilio TEXT,
                       email TEXT NOT NULL UNIQUE,
                       password TEXT NOT NULL,
                       nivel_acceso TEXT NOT NULL
                                                  )''')   
        
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS Recepcionistas(
                       id TEXT PRIMARY KEY,
                       nombre TEXT NOT NULL,
                       apellido TEXT NOT NULL,
                       dni TEXT NOT NULL UNIQUE,
                       genero TEXT,
                       fecha_nacimiento TEXT,
                       nacionalidad TEXT,
                       telefono TEXT,
                       domicilio TEXT,
                       email TEXT NOT NULL UNIQUE,
                       password TEXT NOT NULL,
                       nivel_acceso TEXT NOT NULL)''')
        
        cursor.execute ('''
                        CREATE TABLE IF NOT EXISTS Medicos(
                        id TEXT PRIMARY KEY,
                        nombre TEXT NOT NULL,
                        apellido TEXT NOT NULL,
                        dni TEXT NOT NULL UNIQUE,
                        genero TEXT,
                        fecha_nacimiento TEXT,
                        nacionalidad TEXT,
                        telefono TEXT,
                        domicilio TEXT,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        nivel_acceso TEXT NOT NULL,
                        especialidad TEXT NOT NULL
                                                )''')          
        
        
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS Socios(
                       id TEXT PRIMARY KEY,
                       nombre TEXT NOT NULL,
                       apellido TEXT NOT NULL,
                       dni TEXT NOT NULL,
                       genero TEXT,
                       fecha_nacimiento TEXT,
                       nacionalidad TEXT,
                       telefono TEXT,
                       domicilio TEXT,
                       email TEXT NOT NULL UNIQUE,
                       password TEXT NOT NULL,
                       codigo_postal TEXT,
                                         )''')
        
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS Turnos(
                       id TEXT PRIMARY KEY,
                       socio_id TEXT NULL,
                       medico_id TEXT NULL,
                       especialidad TEXT NOT NULL,
                       profesional TEXT NOT NULL,
                       fecha_hora TEXT NOT NULL,
                       estado TEXT NOT NULL,
                       FOREIGN KEY (socio_id) REFERENCES Socios(id),
                       FOREIGN KEY (medico_id) REFERENCES Medicos(id)
                                                                        )''')
        self.conn.commit()
        cursor.close()

    def _seed_administradores(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM administradores''')
        if cursor.fetchone()[0] == 0:
            administradores = [
                (str(uuid.uuid4()), "Alan", "Gutierrez", "30128657", "Masculino", "1980-02-09", "Argentino", "11-9273-01283",
                "Espora 1800", "GA@Clinica.com", hash_password("Admin9012"), "Administrador"),

                (str(uuid.uuid4()),"Juan", "Diaz", "35634742", "Masculino", "1986-06-16", "Argentino", "11-6295-8939",
                 "Republica Argentina 825", "DJ@Clinica.com", hash_password("Admin6572"), "Administrador"),
            ]
            cursor.executemany(''' INSERT INTO Administradores VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',administradores)
            self.conn.commit()
        cursor.close()

    def _seed_recepcionistas(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM recepcionistas''')
        if cursor.fetchone()[0] == 0:
            recepcionistas = [
                (str(uuid.uuid4()), "Maria", "Ledesma", "36289450", "Femenino", "1992-03-16", "Argentina", "11-8653-9841",
                 "Figueroa 760", "LM@Clinica.com", hash_password("Recep983"), "Recepcionista"),

                (str(uuid.uuid4()), "Juan", "Gauna", "40192837", "Masculino", "2000-06-01", "Argentino", "11-2785-0182",
                 "Araujo 1520", "GJ@Clinica.com", hash_password("Recep871"), "Recepcionista"),
            ]
            cursor.executemany(''' INSERT INTO Recepcionistas VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',recepcionistas)
            self.conn.commit()
        cursor.close()

    def _seed_medicos(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM Medicos''')
        if cursor.fetchone()[0] == 0:
            medicos = [
                (str(uuid.uuid4()), "Sebastian", "Fernandez", "20456789", "Masculino", "1980-05-15", "Argentino", "11-2547-4901", 
                 "Ricardo Rojas 758", "FS@Clinica.com", hash_password("cardio245"), "Medico", "Cardigiologia"),
                
                (str(uuid.uuid4()), "Lucia", "Gonzalez", "25678901", "Femenino", "1985-08-22", "Argentina",
                 "11-2567-9872", "Lavarden 879", "GL@Clinica.com", hash_password("neuro123"), "Medico", "Neurologia"),
            ]
            cursor.executemany(''' INSERT INTO Medicos VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', medicos)
            self.conn.commit()
        cursor.close()

    def obtener_usuario(self, tablas: str, email: str):
        """Busca un usuario en una tabla especifica  por su email."""
        cursor = self.conn.cursor()
        try:
            query = f"SELECT * FROM {tablas} WHERE email = ?"
            cursor.execute(query, (email,))
            resultado = cursor.fetchone()
            return resultado
        except sqlite3.Error as e:
            print(f"Error al buscar en {tablas}: {e}")
            return None
        finally:
            cursor.close()
    
    def buscar_usuario_en_todo_el_sistema(self,email):
        tablas = ["Administradores", "Recepcionistas", "Medicos", "Socios"]
        for tabla in tablas:
            usuario = self.obtener_usuario(tabla, email)
        if usuario:
            return {"data": Usuario, "rol": tablas}
        return None

    def registrar_socio(self, s):
        cursor = self.conn.cursor()
        try:
            #1.---- Control de Email Duplicado (Un Email = Una cuenta)
            cursor.execute("SELECT id FROM Socios WHERE email = ?", (s.email,))
            if cursor.fetchone():
                return {"exitos": False, "mensaje":"El email ya esta en uso."}
            #2. ----Estrategia 1: Control de Fraude por DNI (Maximo 2 registros )
            cursor.execute("SELECT COUNT (*) FROM Socios WHERE dni = ? ",(s.dni,))
            cantidad_dnis = cursor.fetchone()[0]
            if cantidad_dnis>= 2:
                return {"Exito": False, "mensaje": "Limite de registros para este DNI alcanzado. contacte a soporte."}
            #3. ----Guardado seguro si paso las validaciones
            cursor.execute('''INSERT INTO Socios(id, nombre, apellido, dni, genero, fecha_nacimiento,
                           nacionalidad, telefono, domicilio, email, password, codigo_postal)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                           (s.id_usuario, s.nombre, s.apellido, s.dni, s.genero, s.fecha_nacimiento, 
                            s.nacionalidad, s.telefono, s.domicilio, s.email, s.password, s.codigo_postal))
            self.conn.commit()
            return {"exito": True, "mensaje": "Socio registrado con exito."}
        except sqlite3.Error as e:
            return {"exito":False, "mensaje": f"Error de base de datos: {e}"}
        finally:
            cursor.close()

    def buscar_socio_por_id(self, id_usuario: str):
        #---- busca un socio por su UUID y devuelve una instancia de la clase socio o None ----
        cursor = self.conn.cursor()
        #---- Seleccionamos explicitamente las columnas en el orden que conocemos ----
        cursor.execute("""
            SELECT id, nombre, apellido, dni, genero, fecha_nacimiento,nacionalidad,telefono,
                       domicilio, email, password, codigo_postal
            FROM Socios WHERE id = ?
                       """, (id_usuario,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            #---- Creamos  el objeto Socio pasando los datos en el orden exacto de su __init__ ----
            socio = Socio(
                nombre = row [1],
                apellido = row [2],
                dni = row[3],
                genero = row[4],
                fecha_nacimiento = row[5],
                nacionalidad = row[6],
                telefono = row[7],
                domicilio = row[8],
                email = row[9],
                password = row[10], # Aqui viene el hash de la contraseña.
                codigo_postal = row[11]
            )
            #Le asignamos el ID que recuperamos de la base de datos.
            socio.id_usuario = row[0]
            return socio
        return None

    def actualizar_datos_personales(self, datos):
        #---- Modifica los datos de un socio existento usando su ID ----
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                           UPDATE Socios
                           SET nombre=?, apellido=?, nacionalidad=?, telefono=?, domicilio=?, 
                           codigo_postal=?
                           WHERE id=?
                           ''', (datos.nombre, datos.apellido, datos.nacionalidad, datos.telefono, 
                                 datos.domicilio, datos.codigo_postal, datos.id_usuario))   
            self.conn.commit()
            exito = True
        except sqlite3.Error as e:
            print(f"Error al actualizar datos:{e}")  #Esto ayuda a desbugear en la consola
            exito = False
        finally:
            cursor.close()
        return exito
    
    def verificar_password_actual(self, tabla:str, id_usuario: str, password_actual: str):
        #---- Verifica si la contraseña ingresada coincide con la guardada en la DB(usando hash.) ----
        cursor = self.conn.cursor()
        try:
            #La hacemos generica para que sirva para cualquier rol
            query = f"SELECT password FROM {tabla} WHERE id = ?"
            cursor.execute(query, (id_usuario,))
            row = cursor.fetchone()

            if row:
                return row[0] == hash_password(password_actual)
            
            return False
        except sqlite3.Error as e:
            print(f"Error al verificar contraseña en {tabla}: {e}")
            return False
        finally:
            cursor.close()
    
    def actualizar_password(self, id_usuario: str, password_nueva: str):
        #---- Cambiar la contraseña de un  socio de forma segura aplicando hash. ----
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                           'UPDATE Socios SET password = ? WHERE id = ?',
                           (hash_password(password_nueva), id_usuario)
                           )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al actualizar la contraseña: {e}")
            return False
        finally:
            cursor.close()

    def listar_medicos_completo(self):
        #---- Devuelve una lista el nombre completo para que sea un listado serio ----
        cursor = self.conn.cursor()   
        cursor.execute('''SELECT id, nombre, apellido, especialidad FROM Medicos''')

        resultado = [
            {
                 "id": m[0],
                "nombre_completo": f"{m[1]} {m[2]}",
                "especialidad": m[3]
            }
            for m in cursor.fetchall()
        ]
        cursor.close()
        return resultado
      
    # --- Logica de turnos ---

    def listar_todos_los_turnos_admin(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, especialidad, profesional, fecha_hora, estado FROM Turnos")
        resultado = [{
            "id" : r[0],
            "especialidad" : r[1],
            "profesional" : r[2],
            "fecha_hora" : r[3],
            "estado" : r[4],
        } for r in cursor.fetchall()
        ]
        cursor.close()
        return resultado
    
    def buscar_turnos_por_socio(self, socio_id):
        cursor = self.conn.cursor()
        query = '''
            SELECT id, profesional, especialidad, fecha_hora, estado
            FROM Turnos
            WHERE socio_id = ?
            ORDER BY fecha_hora ASC
            '''
        cursor.execute(query, (socio_id,))

        resultado = [
            {
                "id_turno" : r[0],
                "medico" : r[1],
                "especialidad" : r[2],
                "fecha_hora" : r[3],
                "estado" : r[4]
            }
            for r in cursor.fetchall()
        ]
        cursor.close()
        return resultado
    
    def crear_turnos_admin_seguro(self, especialidad, profesional, fecha_hora, estado = "disponible", medico_id = None):
        cursor = self.conn.cursor()
        try:
            cursor.execute("BEGIN IMMEDIATE")

            cursor.execute('''
                           SELECT id FROM Turnos
                           WHERE profesional = ? AND fecha_hora = ? AND estado != 'cancelado'
                           ''',
                           (profesional, fecha_hora)
                           )
            if cursor.fetchone():
                self.conn.rollback
                return False,f"El profesional {profesional} ya tiene un turno asignado para esa fecha y hora."
            id_turno = str(uuid.uuid4())
            cursor.execute(
                '''
                 INSERT INT Turnos (id, socio_id, medico_id, especialidad, profesional,
                 fecha_hora, estado)
                 VALUES (?, ?, ?, ?, ?, ?, ? ) 
                ''',
                (id_turno, None, medico_id, especialidad, profesional, fecha_hora, estado)
            )
            self.conn.commit()
            return True, f"Turnos agendado correctamente."
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error de base de datos: {str(e)}"
        finally:
            cursor.close()

    def agendar_turnos_paciente_seguro(self, socio_id, medico_id, fecha_hora_str):
        cursor = self.conn.cursor()
        try:
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute(
                '''
                SELECT id FROM Turnos
                WHERE socio_id = ? AND fecha_hora = ? AND estado = 'confirmada'
                ''',
                (socio_id, fecha_hora_str)
            )
            if cursor.fetchone():
                self.conn.rollback()
                return False, f"Ya tiene otro turno confirmado para la fecha y hora: {fecha_hora_str}."
            cursor.execute("SELECT nombre, apellido, especialidad FROM (SELECT nombre, apellido, especialidad AS specialty FROM Medicos WHERE id = ?)",(medico_id))
            
            cursor.execute("SELECT nombre, apellido, especialidad FROM Medicos WHERE id = ?", (medico_id))
            med = cursor.fetchone()
            if not med:
                self.conn.rollback()
                return False, "El medico  seleccionado no existe."
            profesional = f"{med[0]}  {med[1]}"
            especialidad = med[2]
            cursor.execute(
                '''
                SELECT id FROM Turnos
                WHERE medico_id = ?
                AND fecha_hora = ?
                AND socio_id IS NULL
                ''',
                (medico_id, fecha_hora_str)
            )
            turno_existente = cursor.fetchone()

            if turno_existente:
                id_turno = turno_existente[0]
                cursor.execute(
                    '''
                    UPDATE Turnos
                    SET socio_id = ?, especialidad = ?, profesional = ?, estado = 'confirmada'
                    WHERE id = ?
                    ''',
                    (socio_id, especialidad, profesional,id_turno)
                )
            else:
                id_nuevo_turno = str(uuid.uuid4())
                cursor.execute(
                    '''
                    INSET INTO Turnos (id, socio_id, medico_id, especialidad, profesional, fecha_hora, estado)
                    VALUES(?,?,?,?,?,?,?)
                    ''',
                    (id_nuevo_turno, socio_id, medico_id, especialidad, profesional, fecha_hora_str, 'confirmada')
                )
            self.conn.commit()
            return True, "Turno reservado exitosamente"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error da base de datos: {str(e)}"
        finally:
            cursor.close()

    def  editar_turnos_admin_seguro(self, id_turno, datos: dict):
        cursor = self.conn.cursor()
        try:
            cursor.execute("BEGIN IMMEDIATE")

            cursor.execute("SELECT profesional, fecha_hora, estado FROM Turnos WHERE id = ?", (id_turno,))
            turno_actual = cursor.fetchone()
            if not turno_actual:
                self.conn.rollback()
                return False, f"El turno no existe."
            prof_actual, fecha_hora_actual, estado_actual = turno_actual

            nuevo_prof = datos.get("profesional", prof_actual)
            nueva_fecha_hora = datos.get("fecha_hora", fecha_hora_actual)
            nuevo_estado = datos.get("estado", estado_actual)

            if nuevo_estado != "cancelado" and nuevo_estado != "cancelada":
                cursor.execute(
                    '''
                    SELECT id FROM Turnos
                    WHERE profesional = ? AND fecha_hora = ? AND id != ? AND estado != 'cancelado' AND estado != 'cancelada'
                    ''',
                    (nuevo_prof, nueva_fecha_hora, id_turno)
                )
                if cursor.fetchone():
                    self.conn.rollback()
                    return False, f"No se puede modificar: El profesional {nuevo_prof} ya tiene otro turno asignado para {nueva_fecha_hora}."

            campos_mapeados = {}
            if "especialidad" in datos: campos_mapeados["especialidad"] = datos["especialidad"]
            if "profesional" in datos: campos_mapeados["profesional"] = datos["profesional"]
            if "fecha_hora" in datos: campos_mapeados["fecha_hora"] = datos["fecha_hora"]
            if "estado" in datos: campos_mapeados["estado"] = datos["estado"]

            if campos_mapeados:
                claves = ", ".join([f"{k} = ?" for k in campos_mapeados.keys])
                valores = list(campos_mapeados.values())
                valores.append(id_turno)
                cursor.execute(f"UPDATE Turnos SET {claves} WHERE id = ?", valores)

            self.conn.commit()
            return True, f"Turno actualizado correctamente"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Error de base de datos: {str(e)}"
        finally:
            cursor.close()

    def cancelar_turnos_logico(self, id_turno):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''SELECT id FROM Turnos WHERE id = ?''', (id_turno,))
            if cursor.fetchone() is None:
                return False

            cursor.execute('''UPDATE Turnos SET estado = 'cancelado' WHERE id = ?''', (id_turno))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al cancelar turno: {e}")
            return False
        finally:
            cursor.close()      
# --- 3. FASTAPI ---
app = FastAPI()
mi_clinica = Clinica()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS PYDANTIC ---
class LoginIn(BaseModel):
    login_input: str  
    password: str

class SocioIn(BaseModel):
    nombre: str
    apellido: str
    dni: str
    nacionalidad: str
    telefono: str
    domicilio: str
    email: str
    password: str

class PerfilUpdateIn(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    nacionalidad: str
    telefono: str
    domicilio: str
    fecha_nacimiento: str
    genero: str
    ciudad: str
    altura: str
    codigo_postal: str
    obra_social: str

class CuentaUpdateIn(BaseModel):
    id_usuario: int
    email: str
    password_actual: str
    password_nueva: str

class TurnoIn(BaseModel):
    socio_id: str
    medico_id: str
    fecha_hora: str


# --- ENDPOINTS ---

@app.post("/api/login")
def api_login(datos: LoginIn):
    resultado = mi_clinica.login_general(datos.login_input, datos.password)
    if not resultado:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return resultado  

@app.post("/api/registrar")
def api_registrar_socio(socio: SocioIn):
    nuevo_socio = Socio(
        nombre=socio.nombre, apellido=socio.apellido, dni=socio.dni,
        nacionalidad=socio.nacionalidad, telefono=socio.telefono, domicilio=socio.domicilio,
        email=socio.email, password=socio.password
    )
    if not mi_clinica.registrar_socio(nuevo_socio):
        raise HTTPException(status_code=400, detail="El DNI o Email ya existe.")
    return {"status": "success", "mensaje": "Paciente registrado con éxito"}

@app.get("/api/usuario/perfil/{id_usuario}")
def api_obtener_perfil(id_usuario: int):
    p = mi_clinica.buscar_socio_por_id(id_usuario)
    if not p: 
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "nombre": p.nombre, "apellido": p.apellido, "dni": p.dni,
        "nacionalidad": p.nacionalidad, "telefono": p.telefono, "domicilio": p.domicilio,
        "fecha_nacimiento": p.fecha_nacimiento, "genero": p.genero, "ciudad": p.ciudad,
        "altura": p.altura, "codigo_postal": p.codigo_postal, "obra_social": p.obra_social,
        "email": p.email
    }

@app.put("/api/usuario/perfil")
def api_actualizar_perfil(datos: PerfilUpdateIn):
    if not mi_clinica.actualizar_datos_personales(datos):
        raise HTTPException(status_code=400, detail="Error al actualizar datos")
    return {"status": "success"}

@app.put("/api/usuario/cuenta")
def api_actualizar_cuenta(datos: CuentaUpdateIn):
    if not mi_clinica.verificar_password_actual(datos.id_usuario, datos.password_actual):
        raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")
    mi_clinica.actualizar_password(datos.id_usuario, datos.password_nueva, datos.email)
    return {"status": "success"}

@app.get("/api/medicos")
def api_listar_medicos():
    return mi_clinica.listar_medicos_completo()

@app.get("/api/usuario/turnos/{socio_id}")
def api_obtener_turnos_socio(socio_id: str):
    return mi_clinica.buscar_turnos_por_socio(socio_id)

@app.post("/api/turnos")
def api_agendar_turno(turno: TurnoIn):
    exito, mensaje = mi_clinica.agendar_turno_paciente_seguro(
        socio_id = turno.socio_id,
        medico_id = turno.medico_id,
        fecha_hora_str = turno.fecha_hora
    )
    if not exito:
        raise HTTPException(status_code = 400, detail = mensaje)
    return {"status": "sucess", "mensaje": mensaje}

@app.delete("/api/turnos/{id_turno}")
def api_cancelar_turno(id_turno: str):
    if not mi_clinica.cancelar_turnos(id_turno):
        raise HTTPException(status_code=404, detail="El turno no existe")
    return {"status": "success", "mensaje": "Turno cancelado con éxito"}


# ==================== SERVIR FRONTEND ====================

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Crear carpeta static si no existe
os.makedirs("static", exist_ok=True)

# Montar archivos estáticos (CSS, JS, imágenes, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==================== RUTAS DE PÁGINAS ====================

@app.get("/")
async def serve_login():
    return FileResponse("loger.html")

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse("ll.html")

@app.get("/sign")
async def serve_sign():
    return FileResponse("sign.html")

@app.get("/recuperar-contraseña ")
async def serve_recuperar():
    return FileResponse("recuperar contraseña.html")

@app.get("/turnos_hospital")
async def serve_turnos_hospital():
    return FileResponse("turnos_hospital.html")

print("✅ Bienvenido al portal del hospital Fernandez")
print("   → Login: http://127.0.0.1:8000")