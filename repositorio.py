"""
repositorio.py
Todas las operaciones de base de datos del sistema, escritas con el ORM.
Las páginas (interfaz) NO escriben SQL: llaman a estas funciones.
  C (Create) -> crear_*      R (Read) -> listar_* / obtener_*
  U (Update) -> actualizar_* D (Delete) -> eliminar_*
Cada función abre su propia sesión, así es seguro llamarlas desde hilos.
"""
from datetime import date, datetime
from sqlalchemy import or_, func, text
from modelos import SessionLocal, Usuario, Ciudadano, Configuracion, Reporte, Respaldo

# Si la tabla tramites tiene una columna de fecha (ej. "fecha_registro"),
# escriba aquí su nombre y el reporte de Trámites respetará el rango de fechas.
COLUMNA_FECHA_TRAMITES = None


def _texto(valor):
    """Convierte None en cadena vacía para mostrar en la interfaz."""
    return "" if valor is None else str(valor)


# =====================================================================
# USUARIOS
# =====================================================================
def listar_usuarios(filtro=""):
    """READ: lista usuarios (usuario, nombre, rol, estado); filtra si hay texto."""
    with SessionLocal() as s:
        q = s.query(Usuario.usuario, Usuario.nombre_completo, Usuario.rol, Usuario.estado)
        if filtro:
            p = f"%{filtro}%"
            q = q.filter(or_(Usuario.usuario.like(p),
                             Usuario.nombre_completo.like(p),
                             Usuario.rol.like(p)))
        return [tuple(fila) for fila in q.all()]


def obtener_usuario(usuario):
    """READ: devuelve los datos de un usuario como diccionario (o None)."""
    with SessionLocal() as s:
        u = s.get(Usuario, usuario)
        if u is None:
            return None
        return {"nombre_completo": _texto(u.nombre_completo), "usuario": _texto(u.usuario),
                "correo": _texto(u.correo), "rol": _texto(u.rol), "estado": _texto(u.estado)}


def existe_usuario(usuario, excluir=None):
    """Valida que no haya dos usuarios con el mismo nombre de usuario."""
    with SessionLocal() as s:
        q = s.query(func.count(Usuario.usuario)).filter(Usuario.usuario == usuario)
        if excluir:
            q = q.filter(Usuario.usuario != excluir)
        return q.scalar() > 0


def crear_usuario(datos):
    """CREATE: inserta un usuario nuevo. 'datos' es un diccionario de columnas."""
    with SessionLocal() as s:
        s.add(Usuario(**datos))
        s.commit()


def actualizar_usuario(usuario_original, datos):
    """UPDATE: modifica los campos recibidos de un usuario existente."""
    with SessionLocal() as s:
        u = s.get(Usuario, usuario_original)
        if u is None:
            return False
        for campo, valor in datos.items():
            setattr(u, campo, valor)
        s.commit()
        return True


def eliminar_usuario(usuario):
    """DELETE: borra un usuario. Devuelve True si existía."""
    with SessionLocal() as s:
        u = s.get(Usuario, usuario)
        if u is None:
            return False
        s.delete(u)
        s.commit()
        return True


def validar_login(usuario, contrasena):
    """Comprueba usuario y contraseña (usado por la pantalla de inicio de sesión)."""
    with SessionLocal() as s:
        u = s.query(Usuario).filter_by(usuario=usuario, contrasena=contrasena).first()
        return u is not None


# =====================================================================
# CIUDADANOS
# =====================================================================
CAMPOS_CIUDADANO = ["cedula", "nombres", "apellidos", "fecha_nacimiento", "genero",
                    "departamento", "municipio", "direccion", "telefono", "correo"]


def _preparar_ciudadano(datos):
    """Convierte la fecha escrita 'AAAA-MM-DD' en un objeto date para el ORM."""
    datos = dict(datos)
    f = datos.get("fecha_nacimiento")
    if isinstance(f, str):
        datos["fecha_nacimiento"] = date.fromisoformat(f) if f.strip() else None
    return datos


def listar_ciudadanos(filtro=""):
    """READ: lista ciudadanos (id, cédula, nombres, apellidos, municipio, estado)."""
    with SessionLocal() as s:
        q = s.query(Ciudadano.id_ciudadano, Ciudadano.cedula, Ciudadano.nombres,
                    Ciudadano.apellidos, Ciudadano.municipio, Ciudadano.estado)
        if filtro:
            p = f"%{filtro}%"
            q = q.filter(or_(Ciudadano.cedula.like(p), Ciudadano.nombres.like(p),
                             Ciudadano.apellidos.like(p)))
        return [tuple(fila) for fila in q.all()]


def obtener_ciudadano(id_ciudadano):
    """READ: todos los datos de un ciudadano como diccionario (o None)."""
    with SessionLocal() as s:
        c = s.get(Ciudadano, id_ciudadano)
        if c is None:
            return None
        datos = {campo: _texto(getattr(c, campo)) for campo in CAMPOS_CIUDADANO}
        datos["estado"] = _texto(c.estado)
        return datos


def existe_cedula(cedula, excluir_id=None):
    """Valida que no se repita la cédula entre ciudadanos."""
    with SessionLocal() as s:
        q = s.query(func.count(Ciudadano.id_ciudadano)).filter(Ciudadano.cedula == cedula)
        if excluir_id:
            q = q.filter(Ciudadano.id_ciudadano != excluir_id)
        return q.scalar() > 0


def crear_ciudadano(datos):
    """CREATE: inserta un ciudadano y devuelve su nuevo id."""
    with SessionLocal() as s:
        c = Ciudadano(**_preparar_ciudadano(datos))
        s.add(c)
        s.commit()
        return c.id_ciudadano


def actualizar_ciudadano(id_ciudadano, datos):
    """UPDATE: modifica los campos recibidos de un ciudadano."""
    with SessionLocal() as s:
        c = s.get(Ciudadano, id_ciudadano)
        if c is None:
            return False
        for campo, valor in _preparar_ciudadano(datos).items():
            setattr(c, campo, valor)
        s.commit()
        return True


def eliminar_ciudadano(id_ciudadano):
    """DELETE: borra un ciudadano. Devuelve True si existía."""
    with SessionLocal() as s:
        c = s.get(Ciudadano, id_ciudadano)
        if c is None:
            return False
        s.delete(c)
        s.commit()
        return True


# =====================================================================
# CONFIGURACIÓN
# =====================================================================
def obtener_configuracion():
    """READ: devuelve la configuración general (primera fila) o None."""
    with SessionLocal() as s:
        c = s.query(Configuracion).first()
        if c is None:
            return None
        return {"nombre": _texto(c.nombre_institucion), "idioma": _texto(c.idioma),
                "tema": _texto(c.tema)}


def guardar_configuracion(nombre, idioma, tema):
    """UPDATE: guarda la configuración (fila con id_configuracion = 1)."""
    with SessionLocal() as s:
        c = s.get(Configuracion, 1)
        if c is None:
            return False
        c.nombre_institucion = nombre
        c.idioma = idioma
        c.tema = tema
        s.commit()
        return True


# =====================================================================
# PANEL PRINCIPAL (estadísticas y trámites recientes)
# =====================================================================
def contar_estadisticas():
    """Cantidad de usuarios, ciudadanos y trámites para las tarjetas del panel."""
    with SessionLocal() as s:
        resultado = {
            "usuarios": s.query(func.count(Usuario.usuario)).scalar(),
            "ciudadanos": s.query(func.count(Ciudadano.id_ciudadano)).scalar(),
            "tramites": 0,
        }
        try:
            resultado["tramites"] = s.execute(text("SELECT COUNT(*) FROM tramites")).scalar()
        except Exception:
            s.rollback()  # si la tabla tramites no existe, queda en 0
        return resultado


def tramites_recientes(limite=5):
    """Últimos trámites registrados: devuelve (encabezados, filas)."""
    try:
        with SessionLocal() as s:
            r = s.execute(text(f"SELECT * FROM tramites ORDER BY 1 DESC LIMIT {int(limite)}"))
            encabezados = [c.upper() for c in r.keys()]
            return encabezados, [tuple(f) for f in r.fetchall()]
    except Exception:
        return [], []


# =====================================================================
# REPORTES
# =====================================================================
def datos_reporte(tipo, inicio, fin):
    """Obtiene los datos de un reporte: devuelve (encabezados, filas)."""
    with SessionLocal() as s:
        if tipo == "Registros de ciudadanos":
            filas = s.query(Ciudadano.cedula, Ciudadano.nombres, Ciudadano.apellidos,
                            Ciudadano.municipio, Ciudadano.estado).all()
            encabezados = ["CÉDULA", "NOMBRES", "APELLIDOS", "MUNICIPIO", "ESTADO"]
        elif tipo == "Usuarios del sistema":
            filas = s.query(Usuario.usuario, Usuario.nombre_completo, Usuario.correo,
                            Usuario.rol, Usuario.estado).all()
            encabezados = ["USUARIO", "NOMBRE", "CORREO", "ROL", "ESTADO"]
        elif tipo == "Trámites":
            sql = "SELECT * FROM tramites"
            params = {}
            if COLUMNA_FECHA_TRAMITES:
                sql += f" WHERE DATE({COLUMNA_FECHA_TRAMITES}) BETWEEN :ini AND :fin"
                params = {"ini": inicio, "fin": fin}
            r = s.execute(text(sql), params)
            encabezados = [c.upper() for c in r.keys()]
            filas = r.fetchall()
        else:
            raise ValueError("Tipo de reporte no válido")
        return encabezados, [tuple(f) for f in filas]


def registrar_reporte(tipo, inicio, fin):
    """CREATE: deja constancia en la tabla reportes de que se generó un reporte."""
    with SessionLocal() as s:
        s.add(Reporte(tipo_reporte=tipo, fecha_inicio=inicio, fecha_fin=fin))
        s.commit()


# =====================================================================
# RESPALDOS
# =====================================================================
def listar_respaldos():
    """READ: últimos 50 respaldos (fecha, base de datos, descripción)."""
    with SessionLocal() as s:
        filas = (s.query(Respaldo.fecha_respaldo, Respaldo.nombre_bd, Respaldo.descripcion)
                 .order_by(Respaldo.fecha_respaldo.desc()).limit(50).all())
        return [tuple(f) for f in filas]


def registrar_respaldo(nombre_bd, descripcion):
    """CREATE: guarda en el historial que se hizo un respaldo."""
    with SessionLocal() as s:
        s.add(Respaldo(fecha_respaldo=datetime.now().replace(microsecond=0),
                       nombre_bd=nombre_bd, descripcion=descripcion))
        s.commit()