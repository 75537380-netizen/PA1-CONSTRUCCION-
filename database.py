"""
database.py
-----------
Capa de acceso a datos (DAL).
Maneja usuarios, categorias y tareas con manejo completo de excepciones.
"""

import mysql.connector
from mysql.connector import Error as MySQLError
from typing import List, Optional

from models import Tarea, Usuario, Categoria, HorarioUsuario


DB_CONFIG = {
    "host": "localhost",
    "database": "ucciluisproyecto",
    "user": "root",
    "password": "shadow1212",
    "charset": "utf8mb4",
    "use_unicode": True,
    "autocommit": False,
}


def obtener_conexion():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except MySQLError as error:
        raise MySQLError(f"No se pudo conectar a la base de datos: {error}") from error


def _asegurar_columna_orden(conexion) -> None:
    """Agrega columna orden a tareas si no existe aun."""
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.columns
            WHERE table_schema = 'ucciluisproyecto'
              AND table_name = 'tareas'
              AND column_name = 'orden'
        """)
        existe = cursor.fetchone()[0]
        if not existe:
            cursor.execute("ALTER TABLE tareas ADD COLUMN orden INT DEFAULT 0")
            conexion.commit()
    finally:
        if cursor: cursor.close()


def _asegurar_tabla_horarios(conexion) -> None:
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS horarios_usuario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL UNIQUE,
                horario_base TEXT,
                contexto_horario TEXT NULL,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
            """
        )
        conexion.commit()
    finally:
        if cursor:
            cursor.close()


# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------

def crear_usuario(nombre_usuario: str, contrasena_hash: str) -> int:
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre_usuario, contrasena_hash) VALUES (%s, %s)",
            (nombre_usuario, contrasena_hash),
        )
        conexion.commit()
        return cursor.lastrowid
    except MySQLError as error:
        if conexion:
            conexion.rollback()
        raise MySQLError(f"Error al crear usuario: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def obtener_usuario_por_nombre(nombre_usuario: str) -> Optional[Usuario]:
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))
        fila = cursor.fetchone()
        return Usuario.desde_fila_bd(fila) if fila else None
    except MySQLError as error:
        raise MySQLError(f"Error al obtener usuario: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def obtener_usuario_por_id(usuario_id: int) -> Optional[Usuario]:
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
        fila = cursor.fetchone()
        return Usuario.desde_fila_bd(fila) if fila else None
    except MySQLError as error:
        raise MySQLError(f"Error al obtener usuario #{usuario_id}: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def existe_nombre_usuario(nombre_usuario: str) -> bool:
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT 1 FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))
        return cursor.fetchone() is not None
    except MySQLError as error:
        raise MySQLError(f"Error al verificar usuario: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


# ---------------------------------------------------------------------------
# Categorias
# ---------------------------------------------------------------------------

def obtener_categorias_usuario(usuario_id: int) -> List[Categoria]:
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM categorias WHERE usuario_id = %s ORDER BY nombre",
            (usuario_id,),
        )
        return [Categoria.desde_fila_bd(f) for f in cursor.fetchall()]
    except MySQLError as error:
        raise MySQLError(f"Error al obtener categorias: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def crear_categoria(categoria: Categoria) -> int:
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO categorias (nombre, color, usuario_id) VALUES (%s, %s, %s)",
            (categoria.nombre, categoria.color, categoria.usuario_id),
        )
        conexion.commit()
        return cursor.lastrowid
    except MySQLError as error:
        if conexion: conexion.rollback()
        raise MySQLError(f"Error al crear categoria: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def eliminar_categoria(categoria_id: int, usuario_id: int) -> bool:
    """Elimina solo si pertenece al usuario (seguridad)."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "DELETE FROM categorias WHERE id = %s AND usuario_id = %s",
            (categoria_id, usuario_id),
        )
        conexion.commit()
        return cursor.rowcount > 0
    except MySQLError as error:
        if conexion: conexion.rollback()
        raise MySQLError(f"Error al eliminar categoria: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


# ---------------------------------------------------------------------------
# Tareas
# ---------------------------------------------------------------------------

def obtener_todas_las_tareas(usuario_id: int, filtro_estado: Optional[str] = None) -> List[Tarea]:
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        _asegurar_columna_orden(conexion)
        cursor = conexion.cursor(dictionary=True)

        base_sql = """
            SELECT t.*, c.nombre AS nombre_categoria, c.color AS color_categoria
            FROM tareas t
            LEFT JOIN categorias c ON t.categoria_id = c.id
            WHERE t.usuario_id = %s
        """

        if filtro_estado == "pendiente":
            sql = base_sql + " AND t.completada = FALSE ORDER BY t.orden ASC, t.fecha_creacion DESC"
        elif filtro_estado == "completada":
            sql = base_sql + " AND t.completada = TRUE ORDER BY t.orden ASC, t.fecha_creacion DESC"
        else:
            sql = base_sql + " ORDER BY t.orden ASC, t.fecha_creacion DESC"

        cursor.execute(sql, (usuario_id,))
        return [Tarea.desde_fila_bd(f) for f in cursor.fetchall()]

    except MySQLError as error:
        raise MySQLError(f"Error al obtener tareas: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def obtener_tarea_por_id(tarea_id: int, usuario_id: int) -> Optional[Tarea]:
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """SELECT t.*, c.nombre AS nombre_categoria, c.color AS color_categoria
               FROM tareas t LEFT JOIN categorias c ON t.categoria_id = c.id
               WHERE t.id = %s AND t.usuario_id = %s""",
            (tarea_id, usuario_id),
        )
        fila = cursor.fetchone()
        return Tarea.desde_fila_bd(fila) if fila else None
    except MySQLError as error:
        raise MySQLError(f"Error al obtener tarea #{tarea_id}: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def insertar_tarea(tarea: Tarea) -> int:
    if not tarea.es_valida():
        raise ValueError("La tarea no es valida.")
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        sql = """
            INSERT INTO tareas (titulo, descripcion, prioridad, completada, fecha_limite, categoria_id, usuario_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            tarea.titulo.strip(), tarea.descripcion, tarea.prioridad,
            tarea.completada, tarea.fecha_limite, tarea.categoria_id, tarea.usuario_id,
        ))
        conexion.commit()
        return cursor.lastrowid
    except MySQLError as error:
        if conexion: conexion.rollback()
        raise MySQLError(f"Error al insertar tarea: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def actualizar_tarea(tarea: Tarea) -> bool:
    if not tarea.es_valida():
        raise ValueError("La tarea no es valida.")
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        sql = """
            UPDATE tareas SET titulo=%s, descripcion=%s, prioridad=%s, completada=%s,
                fecha_limite=%s, categoria_id=%s
            WHERE id=%s AND usuario_id=%s
        """
        cursor.execute(sql, (
            tarea.titulo.strip(), tarea.descripcion, tarea.prioridad,
            tarea.completada, tarea.fecha_limite, tarea.categoria_id,
            tarea.id, tarea.usuario_id,
        ))
        conexion.commit()
        return cursor.rowcount > 0
    except MySQLError as error:
        if conexion: conexion.rollback()
        raise MySQLError(f"Error al actualizar tarea #{tarea.id}: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def cambiar_estado_tarea(tarea_id: int, usuario_id: int, nuevo_estado: bool) -> bool:
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE tareas SET completada = %s WHERE id = %s AND usuario_id = %s",
            (nuevo_estado, tarea_id, usuario_id),
        )
        conexion.commit()
        return cursor.rowcount > 0
    except MySQLError as error:
        if conexion: conexion.rollback()
        raise MySQLError(f"Error al cambiar estado de tarea #{tarea_id}: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def eliminar_tarea(tarea_id: int, usuario_id: int) -> bool:
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM tareas WHERE id = %s AND usuario_id = %s", (tarea_id, usuario_id))
        conexion.commit()
        return cursor.rowcount > 0
    except MySQLError as error:
        if conexion: conexion.rollback()
        raise MySQLError(f"Error al eliminar tarea #{tarea_id}: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def actualizar_orden_tareas(usuario_id: int, ids_ordenados: list) -> None:
    """Actualiza el campo orden de las tareas segun la lista recibida."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        for posicion, tarea_id in enumerate(ids_ordenados):
            cursor.execute(
                "UPDATE tareas SET orden = %s WHERE id = %s AND usuario_id = %s",
                (posicion, tarea_id, usuario_id),
            )
        conexion.commit()
    except MySQLError as error:
        if conexion: conexion.rollback()
        raise MySQLError(f"Error al reordenar tareas: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def obtener_tareas_pendientes_para_plan(usuario_id: int) -> List[Tarea]:
    """Obtiene tareas pendientes ordenadas por prioridad y fecha limite para el plan de IA."""
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        sql = """
            SELECT t.*, c.nombre AS nombre_categoria, c.color AS color_categoria
            FROM tareas t
            LEFT JOIN categorias c ON t.categoria_id = c.id
            WHERE t.usuario_id = %s AND t.completada = FALSE
            ORDER BY
                FIELD(t.prioridad, 'alta', 'media', 'baja'),
                t.fecha_limite IS NULL,
                t.fecha_limite ASC
        """
        cursor.execute(sql, (usuario_id,))
        return [Tarea.desde_fila_bd(f) for f in cursor.fetchall()]
    except MySQLError as error:
        raise MySQLError(f"Error al obtener tareas para plan: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


# ---------------------------------------------------------------------------
# Horario del usuario
# ---------------------------------------------------------------------------

def obtener_horario_usuario(usuario_id: int) -> HorarioUsuario:
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        _asegurar_tabla_horarios(conexion)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM horarios_usuario WHERE usuario_id = %s",
            (usuario_id,),
        )
        fila = cursor.fetchone()
        if fila:
            return HorarioUsuario.desde_fila_bd(fila)
        return HorarioUsuario(usuario_id=usuario_id)
    except MySQLError as error:
        raise MySQLError(f"Error al obtener horario del usuario: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()


def guardar_horario_usuario(usuario_id: int, horario_base: str, contexto_horario: Optional[str]) -> None:
    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        _asegurar_tabla_horarios(conexion)
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO horarios_usuario (usuario_id, horario_base, contexto_horario)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                horario_base = VALUES(horario_base),
                contexto_horario = VALUES(contexto_horario)
            """,
            (usuario_id, horario_base, contexto_horario),
        )
        conexion.commit()
    except MySQLError as error:
        if conexion: conexion.rollback()
        raise MySQLError(f"Error al guardar horario del usuario: {error}") from error
    finally:
        if cursor: cursor.close()
        if conexion and conexion.is_connected(): conexion.close()
