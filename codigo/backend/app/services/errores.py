"""Errores de dominio. Los servicios los lanzan y main.py los traduce a respuestas HTTP."""
from typing import Any


class ErrorDominio(Exception):
    status_code = 400

    def __init__(self, mensaje: str, **extra: Any):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.extra = extra

    def detalle(self) -> str | dict[str, Any]:
        # Sin datos extra, "detail" es un texto; con datos extra (p. ej. alternativas), un objeto.
        return {"message": self.mensaje, **self.extra} if self.extra else self.mensaje


class DatosInvalidos(ErrorDominio):
    status_code = 400


class NoAutenticado(ErrorDominio):
    status_code = 401


class CredencialesInvalidas(ErrorDominio):
    status_code = 401


class SinPermiso(ErrorDominio):
    status_code = 403


class NoEncontrado(ErrorDominio):
    status_code = 404


class Conflicto(ErrorDominio):
    status_code = 409
