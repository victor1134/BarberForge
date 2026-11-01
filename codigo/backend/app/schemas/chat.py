from pydantic import BaseModel


class ChatIn(BaseModel):
    message: str


class ReservaChat(BaseModel):
    barber_id: int
    service_id: int
    date: str
    time: str


class OpcionChat(BaseModel):
    """Botón que el asistente ofrece: enviar un texto, abrir una página o reservar una franja."""

    label: str
    send: str | None = None
    action: str | None = None  # "registro" | "login"
    book: ReservaChat | None = None


class ChatOut(BaseModel):
    reply: str
    sources: list[str] = []
    options: list[OpcionChat] | None = None
