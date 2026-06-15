# trabajo-hospital

front documentacion

Plan de diseño:

Paleta: Azul institucional #1b77e5 (ya existente), blanco #FFFFFF, gris claro #F0F4FA, verde confirmado #22C55E, rojo cancelar #EF4444, amarillo pendiente #F59E0B
Tipografía: Libre Baskerville (ya cargada) para títulos, sistema sans-serif para UI
Firma: Las tarjetas de turno tienen una barra lateral de color que cambia según el estado del turno
Calendario: Embebido de Google Calendar en el aside
Se crearon 2 archivos, ejecutó un comando, archivo leídoSe crearon 2 archivos, ejecutó un comando, archivo leídoAcá tenés los dos archivos.

index.html — Página de pacientes

Aside izquierdo: Iframe de Google Calendar ya integrado. Tiene una nota explicando cómo conectar tu propio calendario (en Google Calendar → Configuración → tu calendario → "Integrar calendario" → copiás el src del iframe y lo pegás en el HTML).
Grilla de turnos: Cards con barra de color según estado (amarillo = pendiente, verde = confirmada, rojo = cancelado), especialidad, médico, fecha y hora.
Botones: "Agendar" (confirma el turno) y "Cancelar" — se deshabilitan según el estado.
Filtros: Por especialidad, franja horaria (mañana/mediodía/tarde) y fecha.


admin.html — Panel administrador

Formulario lateral: Agregar turno con validación de campos obligatorios, selector de especialidades con opción personalizada, fecha, hora y estado inicial.
Tabla de gestión: Muestra todos los turnos con filtros por estado (tabs) y buscador por especialidad/médico.
Acciones por fila: Editar (carga los datos en el formulario), cambiar estado (Pendiente ↔ Confirmado) y Eliminar (con modal de confirmación).
Stats: Contadores de total, pendientes, confirmadas y canceladas en tiempo real.


Comunicación entre páginas: Ambas usan localStorage con la clave hospital_turnos, así que los cambios que hace el admin se reflejan en la página de pacientes al recargarla (o en tiempo real si están abiertas en paralelo en el mismo navegador).

Ahora creo los 4 archivos. Empiezo con el módulo JS de API:Se crearon 3 archivosSe crearon 3 archivosAPI service module for Hospital Los Andesapi.jsUpdated index.html with API integration and mis-turnos panelindex.htmlUpdated admin.html with API integration and role guardadmin.htmlListo.crear la página de perfil de usuario (perfil.Todavía no, me falta crear la página de perfil de usuario (perfil.html). Ya tengo listos los otros 3 archivos. Un momento...Creó un archivo, archivo leídoCreó un archivo, archivo leídoListo. Te entrego 4 archivos, todos en la misma carpeta para que funcionen juntos:

api.js — Módulo central (ES Module)

Funciones para login/logout, perfil, turnos disponibles, mis turnos, y operaciones de admin.
Cada función tiene su versión mock (simulada con localStorage) y el equivalente real comentado para que lo reemplaces cuando tengas el backend.
Maneja el token JWT en sessionStorage.

index.html — Página principal (actualizada)

Muestra un login overlay al entrar. Usuarios de prueba: ana@hospital.com / 1234 y admin@hospital.com / 1234.
El link Panel Admin en el menú solo aparece si el usuario es administrador.
Nueva vista Mis Turnos con tabs para filtrar por estado (confirmados, pendientes, cancelados). Los turnos se marcan como cancelados en lugar de eliminarse.
Los datos vienen de api.js, no de localStorage directo.

admin.html — Panel administrador (actualizado)

Al cargar, verifica el rol: si no hay sesión redirige al inicio, si hay sesión pero no es admin muestra una pantalla de "Acceso restringido".
Solo llega al panel quien tenga role: "admin".

perfil.html — Página de perfil de usuario (nueva)

Muestra nombre, email, rol con un avatar con iniciales.
Permite editar datos personales, dirección y obra social con validación.
Sección para cambiar contraseña con indicador de fortaleza.
Botón para cerrar sesión en todos los dispositivos.