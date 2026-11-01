"""Importa todos los modelos para que queden registrados en Base.metadata (Alembic y pruebas)."""
from app.models.barbero_servicio import barbero_servicio
from app.models.cita import Cita
from app.models.conocimiento import FragmentoConocimiento
from app.models.disponibilidad import Disponibilidad
from app.models.servicio import Servicio
from app.models.usuario import Rol, Usuario

__all__ = ["Cita", "Disponibilidad", "FragmentoConocimiento", "Rol", "Servicio", "Usuario", "barbero_servicio"]
