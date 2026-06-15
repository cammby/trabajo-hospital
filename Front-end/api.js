/**
 * api.js – Hospital Los Andes
 * Módulo central de comunicación con el backend.
 *
 * CÓMO CONECTAR AL BACKEND REAL:
 *   1. Cambiá API_BASE_URL por la URL de tu servidor (ej: "https://api.hospitallosandes.com/v1")
 *   2. Reemplazá getToken() para que lea el JWT real de tu sistema de autenticación.
 *   3. Las funciones de "mock" (simulación) están marcadas con // [MOCK] y deben eliminarse
 *      cuando el backend esté disponible.
 *
 * Todas las funciones devuelven una Promise y lanzan un Error con mensaje legible si falla.
 */

// ── Configuración ─────────────────────────────────────────────────────────────
const API_BASE_URL = "https://api.hospitallosandes.com/v1"; // ← cambiá esto

// ── Auth helpers ──────────────────────────────────────────────────────────────

/** Devuelve el token JWT almacenado en sessionStorage. */
function getToken() {
  return sessionStorage.getItem("auth_token") || null;
}

/** Guarda el token y los datos del usuario en sessionStorage. */
function saveSession(token, user) {
  sessionStorage.setItem("auth_token", token);
  sessionStorage.setItem("current_user", JSON.stringify(user));
}

/** Borra la sesión activa. */
function clearSession() {
  sessionStorage.removeItem("auth_token");
  sessionStorage.removeItem("current_user");
}

/** Devuelve el usuario actualmente autenticado, o null. */
export function getCurrentUser() {
  const raw = sessionStorage.getItem("current_user");
  return raw ? JSON.parse(raw) : null;
}

/** Devuelve true si el usuario actual es administrador. */
export function isAdmin() {
  const user = getCurrentUser();
  return user?.role === "admin";
}

// ── Fetch base ────────────────────────────────────────────────────────────────

/**
 * Realiza una petición HTTP al backend.
 * @param {string} endpoint  - Ruta relativa, ej: "/turnos"
 * @param {RequestInit} opts - Opciones de fetch (method, body, etc.)
 * @returns {Promise<any>}   - JSON parseado de la respuesta
 */
async function apiFetch(endpoint, opts = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...opts.headers,
  };

  const res = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...opts,
    headers,
  });

  if (!res.ok) {
    let msg = `Error ${res.status}`;
    try {
      const data = await res.json();
      msg = data.message || msg;
    } catch (_) {}
    throw new Error(msg);
  }

  // 204 No Content no tiene body
  if (res.status === 204) return null;
  return res.json();
}

// ══════════════════════════════════════════════════════════════════════════════
// AUTENTICACIÓN
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Inicia sesión con email y contraseña.
 * Espera que el backend devuelva { token, user: { id, nombre, email, role, ... } }
 *
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{ token: string, user: object }>}
 */
export async function login(email, password) {
  // [MOCK] ── Eliminar cuando el backend esté listo ──────────────────────────
  await delay(600);
  const mockUsers = [
    { id: 1, nombre: "Ana López",      email: "ana@hospital.com",   role: "user",  telefono: "11-2345-6789", dni: "30111222", fechaNacimiento: "1990-05-15" },
    { id: 2, nombre: "Dr. Administrador", email: "admin@hospital.com", role: "admin", telefono: "11-9876-5432", dni: "25000111", fechaNacimiento: "1975-03-20" },
  ];
  const found = mockUsers.find(u => u.email === email);
  if (!found || password !== "1234") throw new Error("Credenciales incorrectas");
  const token = `mock_token_${found.id}_${Date.now()}`;
  saveSession(token, found);
  return { token, user: found };
  // ── Fin MOCK ──────────────────────────────────────────────────────────────
  /*
  // REAL:
  const data = await apiFetch("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  saveSession(data.token, data.user);
  return data;
  */
}

/**
 * Cierra la sesión del usuario actual.
 * Opcionalmente llama al backend para invalidar el token.
 */
export async function logout() {
  clearSession();
  // REAL: await apiFetch("/auth/logout", { method: "POST" });
}

// ══════════════════════════════════════════════════════════════════════════════
// PERFIL DE USUARIO
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Obtiene el perfil completo del usuario autenticado.
 * @returns {Promise<object>} Datos del usuario
 */
export async function getUserProfile() {
  // [MOCK] ─────────────────────────────────────────────────────────────────
  await delay(400);
  const user = getCurrentUser();
  if (!user) throw new Error("No hay sesión activa");
  return user;
  // ── Fin MOCK ──────────────────────────────────────────────────────────────
  // REAL: return apiFetch("/usuarios/me");
}

/**
 * Actualiza los datos del perfil del usuario.
 * @param {object} datos - Campos a actualizar (nombre, telefono, etc.)
 * @returns {Promise<object>} Usuario actualizado
 */
export async function updateUserProfile(datos) {
  // [MOCK] ─────────────────────────────────────────────────────────────────
  await delay(500);
  const user = getCurrentUser();
  if (!user) throw new Error("No hay sesión activa");
  const updated = { ...user, ...datos };
  saveSession(getToken(), updated);
  return updated;
  // ── Fin MOCK ──────────────────────────────────────────────────────────────
  /*
  // REAL:
  const updated = await apiFetch("/usuarios/me", {
    method: "PATCH",
    body: JSON.stringify(datos),
  });
  // Actualizar el usuario en sesión con los nuevos datos
  saveSession(getToken(), updated);
  return updated;
  */
}

// ══════════════════════════════════════════════════════════════════════════════
// TURNOS (vista usuario)
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Obtiene todos los turnos disponibles para que el usuario pueda ver y agendar.
 * Sólo devuelve turnos en estado "pendiente" que no tengan userId asignado.
 *
 * @returns {Promise<Array>} Lista de turnos disponibles
 */
export async function getTurnosDisponibles() {
  // [MOCK] ─────────────────────────────────────────────────────────────────
  await delay(500);
  const todos = getMockTurnos();
  return todos.filter(t => t.estado === "pendiente" && !t.userId);
  // ── Fin MOCK ──────────────────────────────────────────────────────────────
  // REAL: return apiFetch("/turnos?disponibles=true");
}

/**
 * Obtiene los turnos agendados por el usuario actual.
 * @returns {Promise<Array>} Lista de turnos del usuario
 */
export async function getMisTurnos() {
  // [MOCK] ─────────────────────────────────────────────────────────────────
  await delay(400);
  const user = getCurrentUser();
  if (!user) throw new Error("No autenticado");
  const todos = getMockTurnos();
  return todos.filter(t => t.userId === user.id);
  // ── Fin MOCK ──────────────────────────────────────────────────────────────
  // REAL: return apiFetch("/turnos/mis-turnos");
}

/**
 * Agenda (reserva) un turno disponible para el usuario autenticado.
 * @param {number} turnoId - ID del turno a agendar
 * @returns {Promise<object>} Turno actualizado
 */
export async function agendarTurno(turnoId) {
  // [MOCK] ─────────────────────────────────────────────────────────────────
  await delay(400);
  const user = getCurrentUser();
  if (!user) throw new Error("No autenticado");
  const turnos = getMockTurnos();
  const idx = turnos.findIndex(t => t.id === turnoId);
  if (idx === -1) throw new Error("Turno no encontrado");
  if (turnos[idx].estado !== "pendiente") throw new Error("El turno ya no está disponible");
  turnos[idx] = { ...turnos[idx], estado: "confirmada", userId: user.id };
  setMockTurnos(turnos);
  return turnos[idx];
  // ── Fin MOCK ──────────────────────────────────────────────────────────────
  /*
  // REAL:
  return apiFetch(`/turnos/${turnoId}/agendar`, { method: "POST" });
  */
}

/**
 * Cancela un turno previamente agendado.
 * @param {number} turnoId - ID del turno a cancelar
 * @returns {Promise<object>} Turno actualizado con estado "cancelado"
 */
export async function cancelarTurno(turnoId) {
  // [MOCK] ─────────────────────────────────────────────────────────────────
  await delay(400);
  const user = getCurrentUser();
  if (!user) throw new Error("No autenticado");
  const turnos = getMockTurnos();
  const idx = turnos.findIndex(t => t.id === turnoId);
  if (idx === -1) throw new Error("Turno no encontrado");
  if (turnos[idx].userId !== user.id && !isAdmin())
    throw new Error("No tenés permiso para cancelar este turno");
  turnos[idx] = { ...turnos[idx], estado: "cancelado" };
  setMockTurnos(turnos);
  return turnos[idx];
  // ── Fin MOCK ──────────────────────────────────────────────────────────────
  /*
  // REAL:
  return apiFetch(`/turnos/${turnoId}/cancelar`, { method: "POST" });
  */
}

// ══════════════════════════════════════════════════════════════════════════════
// TURNOS (vista administrador)
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Obtiene TODOS los turnos (solo admins).
 * @returns {Promise<Array>}
 */
export async function getTodosLosTurnos() {
  if (!isAdmin()) throw new Error("Acceso denegado: se requiere rol administrador");
  // [MOCK] ─────────────────────────────────────────────────────────────────
  await delay(400);
  return getMockTurnos();
  // ── Fin MOCK ──────────────────────────────────────────────────────────────
  // REAL: return apiFetch("/admin/turnos");
}

/**
 * Crea un turno nuevo (solo admins).
 * @param {object} datos - { especialidad, profesional, fecha, hora, estado }
 * @returns {Promise<object>} Turno creado
 */
export async function crearTurno(datos) {
  if (!isAdmin()) throw new Error("Acceso denegado");
  // [MOCK] ─────────────────────────────────────────────────────────────────
  await delay(400);
  const turnos = getMockTurnos();
  const nuevoId = Math.max(...turnos.map(t => t.id), 0) + 1;
  const nuevo = { id: nuevoId, userId: null, ...datos };
  turnos.push(nuevo);
  setMockTurnos(turnos);
  return nuevo;
  // ── Fin MOCK ──────────────────────────────────────────────────────────────
  /*
  // REAL:
  return apiFetch("/admin/turnos", {
    method: "POST",
    body: JSON.stringify(datos),
  });
  */
}

/**
 * Edita un turno existente (solo admins).
 * @param {number} turnoId
 * @param {object} datos - Campos a actualizar
 * @returns {Promise<object>} Turno actualizado
 */
export async function editarTurno(turnoId, datos) {
  if (!isAdmin()) throw new Error("Acceso denegado");
  // [MOCK] ─────────────────────────────────────────────────────────────────
  await delay(400);
  const turnos = getMockTurnos();
  const idx = turnos.findIndex(t => t.id === turnoId);
  if (idx === -1) throw new Error("Turno no encontrado");
  turnos[idx] = { ...turnos[idx], ...datos };
  setMockTurnos(turnos);
  return turnos[idx];
  // ── Fin MOCK ──────────────────────────────────────────────────────────────
  /*
  // REAL:
  return apiFetch(`/admin/turnos/${turnoId}`, {
    method: "PATCH",
    body: JSON.stringify(datos),
  });
  */
}

/**
 * Elimina un turno (solo admins).
 * @param {number} turnoId
 * @returns {Promise<null>}
 */
export async function eliminarTurno(turnoId) {
  if (!isAdmin()) throw new Error("Acceso denegado");
  // [MOCK] ─────────────────────────────────────────────────────────────────
  await delay(300);
  const turnos = getMockTurnos();
  setMockTurnos(turnos.filter(t => t.id !== turnoId));
  return null;
  // ── Fin MOCK ──────────────────────────────────────────────────────────────
  // REAL: return apiFetch(`/admin/turnos/${turnoId}`, { method: "DELETE" });
}

// ══════════════════════════════════════════════════════════════════════════════
// HELPERS DE MOCK (simulación de base de datos en localStorage)
// ══════════════════════════════════════════════════════════════════════════════

const STORAGE_KEY = "hospital_turnos";

function getMockTurnos() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (raw) return JSON.parse(raw);
  // Datos de ejemplo
  const inicial = [
    { id:1, especialidad:"Cardiología",    profesional:"Dr. Martínez",   fecha:"2026-07-15", hora:"09:00", estado:"pendiente",  userId: null },
    { id:2, especialidad:"Pediatría",      profesional:"Dra. López",     fecha:"2026-07-18", hora:"14:30", estado:"pendiente",  userId: null },
    { id:3, especialidad:"Ginecología",    profesional:"Dra. Sánchez",   fecha:"2026-07-20", hora:"10:00", estado:"pendiente",  userId: null },
    { id:4, especialidad:"Clínica Médica", profesional:"Dr. Gómez",      fecha:"2026-07-22", hora:"08:30", estado:"pendiente",  userId: null },
    { id:5, especialidad:"Traumatología",  profesional:"Dr. Rodríguez",  fecha:"2026-07-25", hora:"16:00", estado:"pendiente",  userId: null },
    { id:6, especialidad:"Neurología",     profesional:"Dra. Fernández", fecha:"2026-07-28", hora:"11:15", estado:"pendiente",  userId: null },
  ];
  setMockTurnos(inicial);
  return inicial;
}

function setMockTurnos(arr) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
