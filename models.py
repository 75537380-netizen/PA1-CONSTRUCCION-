"""
models.py
---------
Define los modelos de datos: Usuario, Categoria, Tarea y HorarioUsuario.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional


@dataclass
class Usuario:
    nombre_usuario: str
    contrasena_hash: str = ""
    id: Optional[int] = None
    fecha_registro: Optional[datetime] = None

    # Flask-Login interface
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @classmethod
    def desde_fila_bd(cls, fila: dict) -> "Usuario":
        return cls(
            id=fila["id"],
            nombre_usuario=fila["nombre_usuario"],
            contrasena_hash=fila.get("contrasena_hash", ""),
            fecha_registro=fila.get("fecha_registro"),
        )


@dataclass
class Categoria:
    nombre: str
    color: str = "#6c757d"
    usuario_id: Optional[int] = None
    id: Optional[int] = None

    @classmethod
    def desde_fila_bd(cls, fila: dict) -> "Categoria":
        return cls(
            id=fila["id"],
            nombre=fila["nombre"],
            color=fila.get("color", "#6c757d"),
            usuario_id=fila.get("usuario_id"),
        )


@dataclass
class Tarea:
    titulo: str
    descripcion: Optional[str] = None
    prioridad: str = "media"
    completada: bool = False
    fecha_limite: Optional[date] = None
    categoria_id: Optional[int] = None
    usuario_id: Optional[int] = None
    id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    nombre_categoria: Optional[str] = None
    color_categoria: Optional[str] = None

    PRIORIDADES_VALIDAS = ("baja", "media", "alta")

    def es_valida(self) -> bool:
        titulo_presente = bool(self.titulo and self.titulo.strip())
        prioridad_valida = self.prioridad in self.PRIORIDADES_VALIDAS
        return titulo_presente and prioridad_valida

    @classmethod
    def desde_fila_bd(cls, fila: dict) -> "Tarea":
        fecha_limite = fila.get("fecha_limite")
        if isinstance(fecha_limite, datetime):
            fecha_limite = fecha_limite.date()
        return cls(
            id=fila["id"],
            titulo=fila["titulo"],
            descripcion=fila.get("descripcion"),
            prioridad=fila.get("prioridad", "media"),
            completada=bool(fila.get("completada", False)),
            fecha_limite=fecha_limite,
            categoria_id=fila.get("categoria_id"),
            usuario_id=fila.get("usuario_id"),
            fecha_creacion=fila.get("fecha_creacion"),
            fecha_actualizacion=fila.get("fecha_actualizacion"),
            nombre_categoria=fila.get("nombre_categoria"),
            color_categoria=fila.get("color_categoria"),
        )

    @property
    def etiqueta_prioridad(self) -> str:
        mapa_clases = {"baja": "success", "media": "warning", "alta": "danger"}
        return mapa_clases.get(self.prioridad, "secondary")

    @property
    def etiqueta_estado(self) -> str:
        return "Completada" if self.completada else "Pendiente"

    @property
    def estado_deadline(self) -> Optional[str]:
        """Retorna 'vencida', 'pronto' o None segun la fecha limite."""
        if not self.fecha_limite or self.completada:
            return None
        hoy = date.today()
        dias_restantes = (self.fecha_limite - hoy).days
        if dias_restantes < 0:
            return "vencida"
        if dias_restantes <= 3:
            return "pronto"
        return None


@dataclass
class HorarioUsuario:
    usuario_id: int
    horario_base: str = ""
    contexto_horario: Optional[str] = None
    id: Optional[int] = None
    fecha_actualizacion: Optional[datetime] = None

    @classmethod
    def desde_fila_bd(cls, fila: dict) -> "HorarioUsuario":
        return cls(
            id=fila["id"],
            usuario_id=fila["usuario_id"],
            horario_base=fila.get("horario_base", "") or "",
            contexto_horario=fila.get("contexto_horario"),
            fecha_actualizacion=fila.get("fecha_actualizacion"),
        )
