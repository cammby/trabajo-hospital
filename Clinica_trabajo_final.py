import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- 1. CLASES DE DATOS ---
class Medico:
    def __init__(self, id_medico, nombre, especialidad):
        self.id = id_medico
        self.nombre = nombre
        self.especialidad = Black = especialidad

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


# --- 2. LÓGICA DE LA BASE DE DATOS (SQLITE) ---
class Clinica():
    def __init__(self, db_name="clinica.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self._crear_tablas()
        self._seed_medicos()
        self._seed_recepcionistas()
        self._seed_admin()

    def _crear_tablas(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS socios (
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
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS medicos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, especialidad TEXT)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS recepcionistas (
                            id_empleado TEXT PRIMARY KEY, nombre TEXT, apellido TEXT)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS administradores (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT UNIQUE NOT NULL, password TEXT NOT NULL)''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS turnos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, socio_id INTEGER, medico_id INTEGER, fecha_hora TEXT, 
                            FOREIGN KEY(socio_id) REFERENCES socios(id), FOREIGN KEY(medico_id) REFERENCES medicos(id))''')
        self.conn.commit()

    def _seed_medicos(self):
        self.cursor.execute('''SELECT COUNT(*) FROM medicos''')
        if self.cursor.fetchone()[0] == 0:
            medicos = [("García", "Pediatría"), ("Lopez", "Cardiologia"), ("Martinez", "Dermatologia")]
            # Corregido: 'especialidad' unificado
            self.cursor.executemany('''INSERT INTO medicos (nombre, especialidad) VALUES (?,?)''', medicos)
            self.conn.commit()

    def _seed_recepcionistas(self):
        self.cursor.execute('''SELECT COUNT(*) FROM recepcionistas''')
        if self.cursor.fetchone()[0] == 0:
            recepcionistas = [Recepcionista("Ana", "Perez", "R001"), Recepcionista("Luis", "Gomez", "R002")]
            self.cursor.executemany('''INSERT INTO recepcionistas (nombre, apellido, id_empleado) VALUES(?,?,?)''',[ (r.nombre, r.apellido, r.id_empleado) for r in recepcionistas ])
            self.conn.commit() 

    def _seed_admin(self):
        self.cursor.execute('''SELECT COUNT(*) FROM administradores''')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''INSERT INTO administradores (usuario, password) VALUES (?, ?)''', ("admin", "admin123"))
            self.conn.commit()

    def login_general(self, login_input, password):
        self.cursor.execute("SELECT id FROM administradores WHERE usuario = ? AND password = ?", (login_input, password))
        admin = self.cursor.fetchone()
        if admin:
            return {"id": admin[0], "rol": "admin"}
        
        self.cursor.execute("SELECT id FROM socios WHERE email = ? AND password = ?", (login_input, password))
        socio = self.cursor.fetchone()
        if socio:
            return {"id": socio[0], "rol": "paciente"}
        
        return None

    def registrar_socio(self, s):
        try:
            self.cursor.execute('''INSERT INTO socios(nombre,apellido,dni,nacionalidad,telefono,domicilio,
                                fecha_nacimiento,genero,ciudad,altura,codigo_postal,obra_social,email,password)
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (s.nombre, s.apellido, s.dni, s.nacionalidad, s.telefono, s.domicilio,
                                 s.fecha_nacimiento, s.genero, s.ciudad, s.altura, s.codigo_postal, s.obra_social, s.email, s.password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def buscar_socio_por_id(self, id_usuario: int):
        self.cursor.execute("SELECT * FROM socios WHERE id = ?", (id_usuario,))
        row = self.cursor.fetchone()
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
        try:
            self.cursor.execute('''
                UPDATE socios SET nombre=?, apellido=?, nacionalidad=?, telefono=?, domicilio=?,
                fecha_nacimiento=?, genero=?, ciudad=?, altura=?, codigo_postal=?, obra_social=? WHERE id=?
            ''', (datos.nombre, datos.apellido, datos.nacionalidad, datos.telefono, datos.domicilio,
                  datos.fecha_nacimiento, datos.genero, datos.ciudad, datos.altura, datos.codigo_postal, datos.obra_social, datos.id_usuario))
            self.conn.commit()
            return True
        except Exception:
            return False

    def verificar_password_actual(self, id_usuario: int, password_actual: str):
        self.cursor.execute("SELECT password FROM socios WHERE id = ?", (id_usuario,))
        row = self.cursor.fetchone()
        return row and row[0] == password_actual

    def actualizar_password(self, id_usuario: int, password_nueva: str, email: str):
        self.cursor.execute('UPDATE socios SET password=?, email=? WHERE id=?', (password_nueva, email, id_usuario))
        self.conn.commit()
        return True

    def listar_medicos_completo(self):
        # Corregido: 'especialidad' unificado
        self.cursor.execute('''SELECT id, nombre, especialidad FROM medicos''')
        return [{"id": m[0], "nombre": m[1], "especialidad": m[2]} for m in self.cursor.fetchall()]

    def buscar_turnos_por_socio(self, socio_id):
        # Corregido: 'especialidad' unificado
        query = '''SELECT turnos.id, medicos.nombre, medicos.especialidad, turnos.fecha_hora FROM turnos
                   JOIN medicos ON turnos.medico_id = medicos.id WHERE turnos.socio_id = ? ORDER BY turnos.fecha_hora'''
        self.cursor.execute(query, (socio_id,))
        return [{"id_turno": r[0], "medico": r[1], "especialidad": r[2], "fecha_hora": r[3]} for r in self.fetchall_custom()]

    def fetchall_custom(self):
        return self.cursor.fetchall()

    def agendar_turno(self, socio_id, medico_id, fecha_hora_str):
        self.cursor.execute('''SELECT id FROM turnos WHERE medico_id = ? AND fecha_hora = ?''', (medico_id, fecha_hora_str))
        if self.cursor.fetchone() is not None:
            return False
        self.cursor.execute('''INSERT INTO turnos (socio_id, medico_id, fecha_hora) VALUES (?, ?, ?)''', (socio_id, medico_id, fecha_hora_str))
        self.conn.commit()
        return True
    
    def cancelar_turnos(self, id_turno):
        self.cursor.execute('''SELECT id FROM turnos WHERE id = ?''', (id_turno,))
        if self.cursor.fetchone() is None:
            return False
        self.cursor.execute('''DELETE FROM turnos WHERE id = ?''', (id_turno,))
        self.conn.commit()
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

class TurnoIn(BaseModel):
    socio_id: int
    medico_id: int
    fecha_hora: str


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

@app.post("/api/turnos")
def api_agendar_turno(turno: TurnoIn):
    exito = mi_clinica.agendar_turno(turno.socio_id, turno.medico_id, turno.fecha_hora)
    if not exito:
        raise HTTPException(status_code=400, detail="El médico ya está ocupado en ese horario.")
    return {"status": "success", "mensaje": "Turno reservado exitosamente"}

@app.delete("/api/turnos/{id_turno}")
def api_cancelar_turno(id_turno: int):
    if not mi_clinica.cancelar_turnos(id_turno):
        raise HTTPException(status_code=404, detail="El turno no existe")
    return {"status": "success", "mensaje": "Turno cancelado con éxito"}