import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- 1. CLASES DE DATOS ---
class Medico:
    def __init__(self, id_medico, nombre, especialidad):
        self.id = id_medico
        self.nombre = nombre
        self.especialidad = especialidad

class Socio:
    def __init__(self, nombre, apellido, dni, nacionalidad, telefono, domicilio, email, password,
                 fecha_nacimiento="", genero="", ciudad="", altura="", codigo_postal="", obra_social=""):
        self.id = None
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.nacionalidad = nacionalidad
        self.telefono = telefono
        self.domicilio = domicilio
        self.fecha_nacimiento = fecha_nacimiento
        self.genero = genero
        self.ciudad = ciudad
        self.altura = altura
        self.codigo_postal = codigo_postal
        self.obra_social = obra_social
        self.email = email
        self.password = password

class Recepcionista:
    def __init__(self, nombre, apellido, id_empleado):
        self.nombre = nombre
        self.apellido = apellido
        self.id_empleado = id_empleado

# --- 2. LÓGICA DE LA BASE DE DATOS (ARQUITECTURA BLINDADA) ---
class Clinica():
    def __init__(self, db_name="clinica.db"):
        # timeout=30 le da tiempo a los hilos concurrentes de esperar si la DB está ocupada temporalmente
        self.conn = sqlite3.connect(db_name, check_same_thread=False, timeout=30)
        self._crear_tablas()
        self._migrar_tablas()  
        self._seed_medicos()
        self._seed_recepcionistas()
        self._seed_admin()

    def _crear_tablas(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute('''CREATE TABLE IF NOT EXISTS socios (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            apellido TEXT NOT NULL,
                            dni TEXT UNIQUE NOT NULL,
                            nacionalidad TEXT,  
                            telefono TEXT, 
                            domicilio TEXT,
                            fecha_nacimiento TEXT,
                            genero TEXT,
                            ciudad TEXT,
                            altura TEXT,
                            codigo_postal TEXT,
                            obra_social TEXT,
                            email TEXT UNIQUE,
                            password TEXT NOT NULL)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS medicos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, especialidad TEXT)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS recepcionistas (
                            id_empleado TEXT PRIMARY KEY, nombre TEXT, apellido TEXT)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS administradores (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT UNIQUE NOT NULL, password TEXT NOT NULL)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS turnos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            socio_id INTEGER NULL, 
                            medico_id INTEGER NULL, 
                            especialidad TEXT NOT NULL,
                            profesional TEXT NOT NULL,
                            fecha TEXT NOT NULL,
                            hora TEXT NOT NULL,
                            estado TEXT NOT NULL,
                            FOREIGN KEY(socio_id) REFERENCES socios(id), 
                            FOREIGN KEY(medico_id) REFERENCES medicos(id))''')
        self.conn.commit()
        cursor.close()

    def _migrar_tablas(self):
        cursor = self.conn.cursor()
        columnas_nuevas = [
            ("especialidad", "TEXT DEFAULT 'General'"),
            ("profesional", "TEXT DEFAULT 'Por asignar'"),
            ("fecha", "TEXT DEFAULT ''"),
            ("hora", "TEXT DEFAULT ''"),
            ("estado", "TEXT DEFAULT 'pendiente'")
        ]
        for col, tipo in columnas_nuevas:
            try:
                cursor.execute(f"ALTER TABLE turnos ADD COLUMN {col} {tipo};")
            except sqlite3.OperationalError:
                pass  
        self.conn.commit()
        cursor.close()

    def _seed_medicos(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM medicos''')
        if cursor.fetchone()[0] == 0:
            medicos = [("Dr. García", "Pediatría"), ("Dr. Lopez", "Cardiología"), ("Dra. Martinez", "Dermatología")]
            cursor.executemany('''INSERT INTO medicos (nombre, especialidad) VALUES (?,?)''', medicos)
            self.conn.commit()
        cursor.close()

    def _seed_recepcionistas(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM recepcionistas''')
        if cursor.fetchone()[0] == 0:
            recepcionistas = [Recepcionista("Ana", "Perez", "R001"), Recepcionista("Luis", "Gomez", "R002")]
            cursor.executemany('''INSERT INTO recepcionistas (nombre, apellido, id_empleado) VALUES(?,?,?)''',[ (r.nombre, r.apellido, r.id_empleado) for r in recepcionistas ])
            self.conn.commit() 
        cursor.close()

    def _seed_admin(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM administradores''')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''INSERT INTO administradores (usuario, password) VALUES (?, ?)''', ("admin", "admin123"))
            self.conn.commit()
        cursor.close()

    def login_general(self, login_input, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, usuario FROM administradores WHERE usuario = ? AND password = ?", (login_input, password))
        admin = cursor.fetchone()
        if admin:
            cursor.close()
            return {"id": admin[0], "nombre": admin[1], "rol": "admin"} 
        
        cursor.execute("SELECT id, nombre FROM socios WHERE email = ? AND password = ?", (login_input, password))
        socio = cursor.fetchone()
        cursor.close()
        if socio:
            return {"id": socio[0], "nombre": socio[1], "rol": "paciente"}
        
        return None

    def registrar_socio(self, s):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''INSERT INTO socios(nombre,apellido,dni,nacionalidad,telefono,domicilio,
                                fecha_nacimiento,genero,ciudad,altura,codigo_postal,obra_social,email,password)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (s.nombre, s.apellido, s.dni, s.nacionalidad, s.telefono, s.domicilio,
                                 s.fecha_nacimiento, s.genero, s.ciudad, s.altura, s.codigo_postal, s.obra_social, s.email, s.password))
            self.conn.commit()
            exito = True
        except sqlite3.IntegrityError:
            exito = False
        finally:
            cursor.close()
        return exito

    def buscar_socio_por_id(self, id_usuario: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM socios WHERE id = ?", (id_usuario,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            socio = Socio(
                nombre=row[1], apellido=row[2], dni=row[3], nacionalidad=row[4], telefono=row[5], domicilio=row[6],
                fecha_nacimiento=row[7], genero=row[8], ciudad=row[9], altura=row[10], codigo_postal=row[11], obra_social=row[12],
                email=row[13], password=row[14]
            )
            socio.id = row[0]
            return socio
        return None

    def actualizar_datos_personales(self, datos):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                UPDATE socios SET nombre=?, apellido=?, nacionalidad=?, telefono=?, domicilio=?,
                fecha_nacimiento=?, genero=?, ciudad=?, altura=?, codigo_postal=?, obra_social=? WHERE id=?
            ''', (datos.nombre, datos.apellido, datos.nacionalidad, datos.telefono, datos.domicilio,
                  datos.fecha_nacimiento, datos.genero, datos.ciudad, datos.altura, datos.codigo_postal, datos.obra_social, datos.id_usuario))
            self.conn.commit()
            exito = True
        except Exception:
            exito = False
        finally:
            cursor.close()
        return exito

    def verificar_password_actual(self, id_usuario: int, password_actual: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT password FROM socios WHERE id = ?", (id_usuario,))
        row = cursor.fetchone()
        cursor.close()
        return row and row[0] == password_actual

    def actualizar_password(self, id_usuario: int, password_nueva: str, email: str):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE socios SET password=?, email=? WHERE id=?', (password_nueva, email, id_usuario))
        self.conn.commit()
        cursor.close()
        return True

    def listar_medicos_completo(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT id, nombre, especialidad FROM medicos''')
        resultado = [{"id": m[0], "nombre": m[1], "especialidad": m[2]} for m in cursor.fetchall()]
        cursor.close()
        return resultado

    # --- LÓGICA DE TURNOS TOTALMENTE ATÓMICA ---

    def listar_todos_los_turnos_admin(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, especialidad, profesional, fecha, hora, estado FROM turnos")
        resultado = [{
            "id": r[0],
            "especialidad": r[1],
            "profesional": r[2],
            "fecha": r[3],
            "hora": r[4],
            "estado": r[5]
        } for r in cursor.fetchall()]
        cursor.close()
        return resultado

    def buscar_turnos_por_socio(self, socio_id):
        cursor = self.conn.cursor()
        query = '''SELECT id, profesional, especialidad, fecha, hora FROM turnos WHERE socio_id = ? ORDER BY fecha, hora'''
        cursor.execute(query, (socio_id,))
        resultado = [{
            "id_turno": r[0], 
            "medico": r[1], 
            "especialidad": r[2], 
            "fecha_hora": f"{r[3]} {r[4]}".strip()
        } for r in cursor.fetchall()]
        cursor.close()
        return resultado

    def crear_turno_admin_seguro(self, especialidad, profesional, fecha, hora, estado):
        """ Valida e inserta un turno desde el Panel Admin usando transacciones atómicas """
        cursor = self.conn.cursor()
        try:
            cursor.execute("BEGIN IMMEDIATE") # Bloqueo seguro de escritura concurrente
            cursor.execute(
                "SELECT id FROM turnos WHERE profesional = ? AND fecha = ? AND hora = ? AND estado != 'cancelado'",
                (profesional, fecha, hora)
            )
            if cursor.fetchone():
                self.conn.rollback()
                return False, f"El profesional {profesional} ya tiene un turno asignado para esa fecha y hora."

            cursor.execute(
                "INSERT INTO turnos (especialidad, profesional, fecha, hora, estado) VALUES (?, ?, ?, ?, ?)",
                (especialidad, profesional, fecha, hora, estado)
            )
            self.conn.commit()
            return True, "Turno agregado correctamente"
        except Exception as e:
            self.conn.rollback()
            return False, f"Error de base de datos: {str(e)}"
        finally:
            cursor.close()

    def agendar_turno_paciente_seguro(self, socio_id, medico_id, fecha_hora_str):
        """ Valida la agenda y ocupa el lugar creado por el admin o crea uno nuevo si no existía """
        cursor = self.conn.cursor()
        try:
            # Parsear fecha y hora
            fecha = fecha_hora_str
            hora = "00:00"
            if " " in fecha_hora_str:
                fecha, hora = fecha_hora_str.split(" ", 1)
            elif "T" in fecha_hora_str:
                fecha, hora = fecha_hora_str.split("T", 1)

            cursor.execute("BEGIN IMMEDIATE") # Bloqueo seguro para evitar que dos se metan a la vez

            # 1. Validar que el paciente no tenga otro turno confirmado a esa misma hora
            cursor.execute(
                "SELECT id FROM turnos WHERE socio_id = ? AND fecha = ? AND hora = ? AND estado = 'confirmada'",
                (socio_id, fecha, hora)
            )
            if cursor.fetchone():
                self.conn.rollback()
                return False, f"Ya tienes otro turno confirmado el día {fecha} a las {hora} hs."

            # Obtener datos del médico para cruzar por ID o por Nombre de texto
            cursor.execute("SELECT nombre, especialidad FROM medicos WHERE id = ?", (medico_id,))
            med = cursor.fetchone()
            if not med:
                self.conn.rollback()
                return False, "El médico seleccionado no existe."
            profesional = med[0]
            especialidad = med[1]

            # 2. Validar si el turno YA ESTÁ RESERVADO por otro paciente real
            cursor.execute(
                """SELECT id FROM turnos 
                   WHERE (medico_id = ? OR profesional = ?) 
                     AND fecha = ? 
                     AND hora = ? 
                     AND socio_id IS NOT NULL 
                     AND estado = 'confirmada'""", 
                (medico_id, profesional, fecha, hora)
            )
            if cursor.fetchone():
                self.conn.rollback()
                return False, "El médico ya está ocupado con otro paciente en ese horario."

            # 3. Buscar si existe el "casillero vacío" que creó el Administrador
            cursor.execute(
                """SELECT id FROM turnos 
                   WHERE (medico_id = ? OR profesional = ?) 
                     AND fecha = ? 
                     AND hora = ? 
                     AND socio_id IS NULL""", 
                (medico_id, profesional, fecha, hora)
            )
            turno_existente = cursor.fetchone()

            if turno_existente:
                # REUTILIZAR EL CASILLERO: Si el admin ya creó el espacio, lo usamos para el paciente
                id_turno = turno_existente[0]
                cursor.execute(
                    """UPDATE turnos 
                       SET socio_id = ?, medico_id = ?, especialidad = ?, profesional = ?, estado = 'confirmada' 
                       WHERE id = ?""",
                    (socio_id, medico_id, especialidad, profesional, id_turno)
                )
            else:
                # CREAR DESDE CERO: Si el admin no había creado el horario, dejamos que se cree uno nuevo
                cursor.execute(
                    """INSERT INTO turnos (socio_id, medico_id, especialidad, profesional, fecha, hora, estado) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                    (socio_id, medico_id, especialidad, profesional, fecha, hora, "confirmada")
                )

            self.conn.commit()
            return True, "Turno reservado exitosamente"
        except Exception as e:
            self.conn.rollback()
            return False, f"Error de base de datos: {str(e)}"
        finally:
            cursor.close() # 🌟 CORRECCIÓN: Cerramos el cursor pase lo que pase para liberar memoria
    
    def editar_turno_admin_seguro(self, id_turno, datos: dict):
        """ Modifica un turno validando colisiones en el mismo bloque transaccional """
        cursor = self.conn.cursor()
        try:
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute("SELECT profesional, fecha, hora, estado FROM turnos WHERE id = ?", (id_turno,))
            turno_actual = cursor.fetchone()
            if not turno_actual:
                self.conn.rollback()
                return False, "El turno no existe"
                
            prof_actual, fecha_actual, hora_actual, estado_actual = turno_actual

            nuevo_prof = datos.get("profesional", prof_actual)
            nueva_fecha = datos.get("fecha", fecha_actual)
            nueva_hora = datos.get("hora", hora_actual)
            nuevo_estado = datos.get("estado", estado_actual)

            if nuevo_estado != "cancelado":
                cursor.execute(
                    "SELECT id FROM turnos WHERE profesional = ? AND fecha = ? AND hora = ? AND id != ? AND estado != 'cancelado'",
                    (nuevo_prof, nueva_fecha, nueva_hora, id_turno)
                )
                if cursor.fetchone():
                    self.conn.rollback()
                    return False, f"No se puede modificar: El profesional {nuevo_prof} ya tiene otro turno asignado el {nueva_fecha} a las {nueva_hora} hs."

            campos_validos = {k: v for k, v in datos.items() if k in ["especialidad", "profesional", "fecha", "hora", "estado"]}
            if campos_validos:
                claves = ", ".join([f"{k} = ?" for k in campos_validos.keys()])
                valores = list(campos_validos.values())
                valores.append(id_turno)
                cursor.execute(f"UPDATE turnos SET {claves} WHERE id = ?", valores)
            
            self.conn.commit()
            return True, "Turno actualizado correctamente"
        except Exception as e:
            self.conn.rollback()
            return False, f"Error de base de datos: {str(e)}"
        finally:
            cursor.close()

    def cancelar_turnos(self, id_turno):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT id FROM turnos WHERE id = ?''', (id_turno,))
        if cursor.fetchone() is None:
            cursor.close()
            return False
        cursor.execute('''DELETE FROM turnos WHERE id = ?''', (id_turno,))
        self.conn.commit()
        cursor.close()
        return True

# --- 3. CONFIGURACIÓN DE FASTAPI Y CORS ---
app = FastAPI()
mi_clinica = Clinica()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. MODELOS PYDANTIC ---
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

# --- 5. ENDPOINTS DE LA API ---

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
    if not p: raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"nombre": p.nombre, "apellido": p.apellido, "dni": p.dni, "nacionalidad": p.nacionalidad, "telefono": p.telefono, "domicilio": p.domicilio, "fecha_nacimiento": p.fecha_nacimiento, "genero": p.genero, "ciudad": p.ciudad, "altura": p.altura, "codigo_postal": p.codigo_postal, "obra_social": p.obra_social, "email": p.email}

@app.put("/api/usuario/perfil")
def api_actualizar_perfil(datos: PerfilUpdateIn):
    if not mi_clinica.actualizar_datos_personales(datos): raise HTTPException(status_code=400, detail="Error al actualizar datos")
    return {"status": "success"}

@app.put("/api/usuario/cuenta")
def api_actualizar_cuenta(datos: CuentaUpdateIn):
    if not mi_clinica.verificar_password_actual(datos.id_usuario, datos.password_actual): raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")
    mi_clinica.actualizar_password(datos.id_usuario, datos.password_nueva, datos.email)
    return {"status": "success"}

@app.get("/api/medicos")
def api_listar_medicos():
    return mi_clinica.listar_medicos_completo()

@app.get("/api/usuario/turnos/{socio_id}")
def api_obtener_turnos_socio(socio_id: int):
    return mi_clinica.buscar_turnos_por_socio(socio_id)

# --- ENDPOINTS POLIMÓRFICOS ALTAMENTE ENCAPSULADOS ---

@app.get("/api/turnos")
def api_listar_todos_los_turnos():
    return mi_clinica.listar_todos_los_turnos_admin()

@app.post("/api/turnos")
def api_crear_o_agendar_turno(payload: dict):
    if "profesional" in payload:
        # Petición Panel Admin
        exito, mensaje = mi_clinica.crear_turno_admin_seguro(
            especialidad=payload.get("especialidad"),
            profesional=payload.get("profesional"),
            fecha=payload.get("fecha"),
            hora=payload.get("hora"),
            estado=payload.get("estado", "pendiente")
        )
        if not exito:
            raise HTTPException(status_code=400, detail=mensaje)
        return {"status": "success", "mensaje": mensaje}
    else:
        # Petición Sección Pacientes
        socio_id = payload.get("socio_id")
        medico_id = payload.get("medico_id")
        fecha_hora = payload.get("fecha_hora")
        
        if not socio_id or not medico_id or not fecha_hora:
            raise HTTPException(status_code=400, detail="Datos de agendamiento incompletos")
        
        exito, mensaje = mi_clinica.agendar_turno_paciente_seguro(socio_id, medico_id, fecha_hora)
        if not exito:
            raise HTTPException(status_code=400, detail=mensaje)
        return {"status": "success", "mensaje": mensaje}

@app.put("/api/turnos/{id_turno}")
def api_editar_turno(id_turno: int, datos: dict):
    exito, mensaje = mi_clinica.editar_turno_admin_seguro(id_turno, datos)
    if not exito:
        raise HTTPException(status_code=400, detail=mensaje)
    return {"status": "success", "mensaje": mensaje}

@app.delete("/api/turnos/{id_turno}")
def api_cancelar_turno(id_turno: int):
    if not mi_clinica.cancelar_turnos(id_turno):
        raise HTTPException(status_code=404, detail="El turno no existe")
    return {"status": "success", "mensaje": "Turno eliminado con éxito"}