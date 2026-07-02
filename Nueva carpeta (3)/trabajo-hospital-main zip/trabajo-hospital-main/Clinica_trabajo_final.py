import sqlite3
import os
import uuid
import hashlib
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uvicorn

#--- Funciones goblales

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#--- CLASES 

class Usuario():
    def __init__(self, nombre, apellido, dni, genero=None, fecha_nacimiento=None, nacionalidad=None, telefono=None, domicilio=None, email=None, password=None):
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
    def __init__(self,  nombre, apellido, dni, genero=None, fecha_nacimiento=None, nacionalidad=None, telefono=None, domicilio=None, email=None, password=None, nivel_acceso=None):
        super().__init__( nombre, apellido, dni, genero, fecha_nacimiento, nacionalidad, telefono, domicilio, email, password)
        self.nivel_acceso = nivel_acceso

class Recepcionista(Usuario):
    def __init__(self,  nombre, apellido, dni, genero=None, fecha_nacimiento=None, nacionalidad=None, telefono=None, domicilio=None, email=None, password=None, nivel_acceso=None):
        super().__init__( nombre, apellido, dni, genero, fecha_nacimiento, nacionalidad, telefono, domicilio, email, password)
        self.nivel_acceso = nivel_acceso

class Medico(Usuario):
    def __init__(self,  nombre, apellido, dni, genero=None, fecha_nacimiento=None, nacionalidad=None, telefono=None, domicilio=None, email=None, password=None, especialidad=None, nivel_acceso=None):
        super().__init__( nombre, apellido, dni, genero, fecha_nacimiento, nacionalidad, telefono, domicilio, email, password)
        self.especialidad = especialidad
        self.nivel_acceso = nivel_acceso

class Socio(Usuario):
    def __init__(self,  nombre, apellido, dni, genero=None, fecha_nacimiento=None, nacionalidad=None, telefono=None, domicilio=None, email=None, password=None, codigo_postal=None):
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
                       codigo_postal TEXT
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

         
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS HistorialClinico(
                       id TEXT PRIMARY KEY,
                       socio_id TEXT NOT NULL,
                       medico_id TEXT NOT NULL,
                       fecha_hora TEXT NOT NULL,
                       diagnostico TEXT NOT NULL,
                       observaciones TEXT,
                       FOREIGN KEY (socio_id) REFERENCES Socios(id),
                       FOREIGN KER (medicos_id) REFERENCES Medicos(id) 
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
                return {"data": usuario, "rol": tabla}
        return None

    def login_general(self, login_input, password):
        cursor = self.conn.cursor()
        try:
            for tabla in ["Administradores", "Recepcionistas", "Medicos", "Socios"]:
                cursor.execute(f"SELECT id, nombre, apellido, email, password, dni FROM {tabla} WHERE email = ?", (login_input,))
                row = cursor.fetchone()
                if row and row[4] == hash_password(password):
                    return {
                        "id": row[0],
                        "nombre": row[1],
                        "apellido": row[2],
                        "email": row[3],
                        "dni": row[5],
                        "rol": tabla,
                    }
            return None
        finally:
            cursor.close()

    def registrar_socio(self, s):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id FROM Socios WHERE email = ?", (s.email,))
            if cursor.fetchone():
                return False
            cursor.execute("SELECT COUNT(*) FROM Socios WHERE dni = ?", (s.dni,))
            cantidad_dnis = cursor.fetchone()[0]
            if cantidad_dnis >= 2:
                return False
            cursor.execute('''INSERT INTO Socios(id, nombre, apellido, dni, genero, fecha_nacimiento,
                           nacionalidad, telefono, domicilio, email, password, codigo_postal)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                           (s.id_usuario, s.nombre, s.apellido, s.dni, s.genero, s.fecha_nacimiento, 
                            s.nacionalidad, s.telefono, s.domicilio, s.email, hash_password(s.password), s.codigo_postal))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al registrar socio: {e}")
            return False
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
        cursor = self.conn.cursor()
        try:
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
                "nombre": f"{m[1]} {m[2]}",
                "especialidad": m[3]
            }
            for m in cursor.fetchall()
        ]
        cursor.close()
        return resultado
    def registrar_medicos_admin(self, m):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id FROM Medicos WHERE email = ?", (m.email,))
            if cursor.execute():
                return False
            cursor.execute(''' INSERT INTO Medicos(id, nombre, apellido, dni ,genero, fecha_nacimiento, nacionalidad,
                            telefono, domicilio, email, password, nivel_acceso, especialidad)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (m.id_usuario, m.nombre, m.apellido, m.dni, m.genero, m.fecha_nacimiento,
                            m.nacionalidad, m.telefono, m.domicilio, m.email, hash_password(m.password),"Medico", m.especialidad))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al registrar medico: {e}")
            return False
        finally:
            cursor.close()
    def agregar_entrada_historial(self, socio_id: str, medico_id: str, diagnostico: str, tratamiento: str, observciones: str):
        cursor = self.conn.cursor()
        try:
            id_historial = str(uuid.uuid4())
            fecha_actual = datetime.now(.strftime("%Y-%m-%d  %H:%M:%S"))

            cursor.execute('''
                           INSERT INTO Hsitorialclinico (id, socio_id, medico_id, fecha_hora, diagnostico, tratamiento, observaciones)
                           VALUES (?, ?, ?, ?, ?, ?, ?,)
                           ''', (id_historial, socio_id, medico_id, fecha_actual, diagnostico, tratamiento,observciones)
                           )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al guardar historial clinico: {e}")
            return False
        finally:
            cursor.close()


    def obtener_historial_completo_paciente(self, socio_id: str):
        cursor = self.conn.cursor()
        query = '''
                SELEC H.fecha_hora, H.diagnostico, H.tratamiento, H.observaciones, M.nombre, M.apellido, M.especialidad
                FROM HistorialClinico H
                INNER JOIN Medicos M ON H.medicos_id = M.id
                WHERE H.socio_id = ?
                ORDER BY H.fecha_hora DESC 
                '''
        cursor.execute(query, (socio_id,))
        resultado = [
            {
                "fecha_hora" : r[0],
                "diagnostico" : r[1],
                "tratamiento" : r[2],
                "observaciones" : r[3],
                "medico" : f"{r[4]} {r[5]} {r[6]}"
            } for r in cursor.fetchall()
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
    
     def modificar_medicos_admin(self, id_medico, datos):
        cursor = self.conn.cursor()
        try:
            camps = ",".join([f"{k} = ?" for k in datos.keys()])
            valores = list(datos.values())
            valores.append(id_medico)

            cursor.execute(f" UPDATE Medicos SET {camps} WHERE id = ?", valores)
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al modificar medico: {e}")
            return False
        finally:
            cursor.close()

    
    def eliminar_medicos_admin(self, id_medico):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM Medicos WHERE id = ?", (id_medico,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar medico: {e}")
            return False
        finally:
            cursor.close()    

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
                 INSERT INTO Turnos (id, socio_id, medico_id, especialidad, profesional,
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

    def agendar_turno_paciente_seguro(self, socio_id, medico_id, fecha_hora_str):
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
                    INSERT INTO Turnos (id, socio_id, medico_id, especialidad, profesional, fecha_hora, estado)
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

    def cancelar_turno(self, id_turno):
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

    def listar_turnos_para_recepcion(self, fecha: Optional[str] = None):
        cursor = self.conn.cursor()
        try:
            if fecha:
                query = '''
                        SELECT T.id, T.especialidad, T.profesional, T.fecha_hora, T.estado, S.nombre, S.apellido
                        FROM Turnos T
                        LEFT JOIN Socios S On T.socios_id = S.id
                        WHERE T.fecha_hora LIKE ?
                        ORDER BY T.fecha_hora ASC                                                   
                        '''
                cursor.execute(query, (f"{fecha}%",))
            else:
                query = '''
                        SELECT T.id, T.especialidad, T.profesional, T.fecha_hora, T.estado, S.nombre, S.apellido
                        FROM Turnos T
                        LEFT JOIN Socios S ON T.socios_id = S.id
                        ORDER BY T.fecha_hora ASC                
                        '''
                cursor.execute(query)
            resultado = [
                {
                    "id_turno" : r[0],
                    "especialidad" : r[1],
                    "profsional" : r[2],
                    "fecha_hora" : r[3],
                    "estado": r[4],
                    "paciente": f"{r[5]} {r[6]}" if  r[5] else "Sin asignar (Disponible)"  
                } for r in cursor.fetchall()
            ]
            return resultado
        finally:
            cursor.close()

    
     def actualizar_estado_turno_recepcion(self, id_turno: str, nuevo_estado: str):
         cursor = self.conn.cursor()
         try:
             cursor.execute("SELECT id FROM Turnos WHERE id = ?", (nuevo_estado,))
             self.conn.commit()
             return cursor.rowcount > 0
         except sqlite3.Error as e:
             print(f"Error al actualizar estado del turno: {e}")
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

class AdminMedicoIn(BaseModel):
    nombre: str
    apellido: str
    dni: str
    especialidad: str
    email: str
    password: str
    genero: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    nacionalidad: Optional[str] = None
    telefono: Optional[str] = None
    domicilio: Optional[str] = None

class AdminMedicoUpdateIn(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    especialidad: Optional[str] = None
    telefono: Optional[str] = None
    domicilio: Optional[str] = None
    email: Optional[str] = None

class AdminSocioUpdateIn(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    domicilio: Optional[str] = None
    codigo_postal: Optional[str] = None

class CambiarEstadoTurnoIn(BaseModel):
    estado: str

class HistorialClinicoIn(BaseModel):
    socio_id: str
    medico_id: str
    diagnostico: str
    tratamiento: Optional[str] = None
    observaciones: Optional[str] = None

# --- ENDPOINTS ---

@app.post("/api/inicio_sesion")
def api_login(datos: LoginIn):
    resultado = mi_clinica.login_general(datos.login_input, datos.password)
    if not resultado:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return resultado

@app.post("/api/login")
def api_login_alias(datos: LoginIn):
    return api_login(datos)

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

@app.post("/api/registrar_usuario")
def api_registrar_socio_alias(socio: SocioIn):
    return api_registrar_socio(socio)

@app.get("/api/usuario/perfil/{id_usuario}")
def api_obtener_perfil(id_usuario: str):
    p = mi_clinica.buscar_socio_por_id(id_usuario)
    if not p: 
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "nombre": p.nombre, "apellido": p.apellido, "dni": p.dni,
        "nacionalidad": p.nacionalidad, "telefono": p.telefono, "domicilio": p.domicilio,
        "fecha_nacimiento": p.fecha_nacimiento, "genero": p.genero,
        "codigo_postal": p.codigo_postal,
        "email": p.email
    }

@app.put("/api/usuario/perfil")   # por hacer
def api_actualizar_perfil(datos: PerfilUpdateIn):
    if not mi_clinica.actualizar_datos_personales(datos):
        raise HTTPException(status_code=400, detail="Error al actualizar datos")
    return {"status": "success"}

@app.put("/api/usuario/cuenta")
def api_actualizar_cuenta(datos: CuentaUpdateIn):
    if not mi_clinica.verificar_password_actual("Socios", str(datos.id_usuario), datos.password_actual):
        raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")
    mi_clinica.actualizar_password(str(datos.id_usuario), datos.password_nueva)
    return {"status": "success"}

@app.get("/api/medicos")  # por hacer
def api_listar_medicos():
    return mi_clinica.listar_medicos_completo()

@app.get("/api/usuario/turnos/{socio_id}")
def api_obtener_turnos_socio(socio_id: str):
    return mi_clinica.buscar_turnos_por_socio(socio_id)

@app.post("/api/turnos")
def api_agendar_turno(turno: TurnoIn):
    exito, mensaje = mi_clinica.agendar_turno_paciente_seguro(
        socio_id=turno.socio_id,
        medico_id=turno.medico_id,
        fecha_hora_str=turno.fecha_hora
    )
    if not exito:
        raise HTTPException(status_code=400, detail=mensaje)
    return {"status": "success", "mensaje": mensaje}

@app.delete("/api/turnos/{id_turno}")
def api_cancelar_turno(id_turno: str):
    if not mi_clinica.cancelar_turno(id_turno):
        raise HTTPException(status_code=404, detail="El turno no existe")
    return {"status": "success", "mensaje": "Turno cancelado con éxito"}

# ================== ENDPOINS EXCLUSIVOS PARA ADMINISTRADORES ==================
@app.get("/api/admin/pacientes")
def admin_listar_pacientes():
    return mi_clinica.listar_todos_los_socios()


@app.get("/api/admin/medicos")
def admin_modificar_paciente(id_paciente: str, datos: AdminSocioUpdateIn):
    datos_dict = {k: v for k, v in datos.model_dump().items() if v is not None}
    if not datos_dict:
        raise HTTPException(status_code=400, detail="No se enviaron campos para modificar")
    
    if not mi_clinica.modificar_socio_admin(id_paciente, datos_dict):
        raise HTTPException(status_code=404, detail = "Paciente no encontrado o error al modificar")
    return {"status": "success", "mensaje": "Paciente modificado con exito"}

@app.delete("/api/admin/pacientes/{id_paciente}")
def admin_eliminar_paciente(id_paciente: str):
    if not mi_clinica.eliminar_socio_admin(id_paciente):
        raise HTTPException(status_code=404, detail="Paciente no existe")
    return {"status": "success", "mensaje": "Paciente eliminado con exito"}


@app.get("/api/admin/turnos")
def admin_listar_turnos():
    return mi_clinica.listar_todos_los_turnos_admin()

@app.post("/api/admin/medicos")
def admin_registrar_medico(medico: AdminMedicoIn):
    nuevo_medico= Medico(
        nombre = medico.nombre, apellido = medico.apellido, dni = medico.dni,
        especialidad = medico.especialidad, email = medico.email, password = medico.password,
        genero = medico.genero, fecha_nacimiento = medico.fecha_nacimiento, nacionalidad = medico.nacionalidad,
        telefono = medico.telofono, domicilio = medico.domicilio,
    )
    if not mi_clinica.registrar_medicos_admin(nuevo_medico):
        raise HTTPException(status_code=400, detail="El DNI o Email del medico ya se encuentra registrado.")
    return {"status": "success", "mensaje": "Medico registrado con exito"}

@app.put("/api/admin/medicos/{id_medicos}")
def admin_modificar_medicos(id_medicos: str, datos: AdminMedicoUpdateIn):
    datos_dict = {k: v for k, v in datos.model_dump().items() if v is not None}
    if not datos_dict:
        raise HTTPException(status_code=400, detail="No se enviaron campos para modificar")
    return {"status": "success", "mensaje": "Medico modificado con exito"}

@app.delete("/api/admin/medicos")
def admin_eliminar_medico(id_medico: str):
    if not mi_clinica.eliminar_medicos_admin(id_medico):
        raise HTTPException(status_code=404, detail= "Medico no existe")
    return {"status": "success", "mensaje": "Medico eliminado con exito"}

@app.get("/api/admin/estadisticas")
def admin_obetener_estadisticas():
    return mi_clinica.obtener_estadisticas_sistema()

# ========= ENDPOINTS EXCLUSIVOS PARA RECEPCIONISTAS =========
@app.get("/api/recepcion/turnos")
def recepcion_ver_agenda(fecha: Optional[str] = None):
    return mi_clinica.listar_turnos_para_recepcion(fecha)

@app.patch("/api/recepcion/turnos/{id_turno}/estado")
def recepcion_cambiar_estado(id_turno: str, datos: CambiarEstadoTurnoIn):
    if not mi_clinica.actualizar_estado_turno_recepcion(id_turno, datos.estado):
        raise HTTPException(status_code=404, details= "Turno no encontado")
    return {"status": "success", "mensaje": "estado del turno actualizado con exito"} 

# ========= ENDPOINST EXCLUSIVOS PARA MEDICOS ========

@app.get("/api/medico/{medico_id}/turnos")
def api_medico_agenda(medico_id: str, fecha: Optional[str] = None):
    if not fecha:
        fecha = datetime.now().strftime("%Y-%m-%d")
    return mi_clinica.listar_turnos_del_dia_medico(medico_id, fecha)

@app.get("/ape/medicos/paciente/{socio_id}/historal")
def api_medicor_ver_historial(socio_id: str):
    return mi_clinica.obtener_historial_completo_paciente(socio_id)

@app.post("/api/medico/historial")
def api_medico_guardar_consulta(datos: HistorialClinicoIn):
    exito = mi_clinica.agregar_entrada_historial(
        socio_id = datos.socio_id,
        medico_id = datos.medico_id,
        diagnostico = datos.diagnostico,
        tratamiento = datos.tratamiento,
        observciones = datos.observaciones
    )
    if not exito:
        raise HTTPException(status_code=500, detail="No se pudo registrar la consulta en el historial.")
    return{"status": "success", "mensaje": "Consulta guardada con exito en el historial"}

# ==================== SERVIR FRONTEND ====================

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ==================== RUTAS DE PÁGINAS ====================

@app.get("/")
async def serve_login():
    return FileResponse(str(BASE_DIR / "inicio_sesion.html"))

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse(str(BASE_DIR / "pagina_principal.html"))

@app.get("/sign")
async def serve_sign():
    return FileResponse(str(BASE_DIR / "registrar_usuario.html"))

@app.get("/recuperar-contraseña")
async def serve_recuperar():
    return FileResponse(str(BASE_DIR / "recuperar_contrasenia.html"))

@app.get("/turnos_hospital")
async def serve_turnos_hospital():
    return FileResponse(str(BASE_DIR / "pagina_principal.html"))

if __name__ == "__main__":
    uvicorn.run("Clinica_trabajo_final:app", host="127.0.0.1", port=8000, reload=False)
