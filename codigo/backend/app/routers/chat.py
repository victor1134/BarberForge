from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencias import get_current_user_opcional, require_roles
from app.db import get_db
from app.models import Rol, Usuario
from app.schemas.chat import ChatIn, ChatOut
from app.schemas.comun import ReindexOut
from app.services import chat, rag

router = APIRouter(prefix="/api", tags=["asistente"])


@router.post("/chat", response_model=ChatOut, response_model_exclude_none=True)
def conversar(datos: ChatIn, usuario: Usuario | None = Depends(get_current_user_opcional),
              db: Session = Depends(get_db)) -> ChatOut:
    return chat.responder(db, usuario, datos.message)


@router.post("/admin/reindex", response_model=ReindexOut)
def reindexar(_: Usuario = Depends(require_roles(Rol.ADMIN)), db: Session = Depends(get_db)) -> ReindexOut:
    return ReindexOut(embeddings_ok=rag.reindexar(db))
