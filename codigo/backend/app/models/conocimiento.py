from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base

DIMENSION_EMBEDDING = 768  # nomic-embed-text

NIVEL_PUBLICO = "public"
NIVEL_INTERNO = "internal"


class FragmentoConocimiento(Base):
    """Fragmento de la base de conocimiento del asistente (RAG) con su embedding."""

    __tablename__ = "knowledge_chunks"
    __table_args__ = (
        Index("kc_hnsw", "embedding", postgresql_using="hnsw",
              postgresql_ops={"embedding": "vector_cosine_ops"}),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    access_level: Mapped[str] = mapped_column(Text)
    # En PostgreSQL es vector(768) con pgvector; en SQLite (pruebas) se guarda como JSON.
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(DIMENSION_EMBEDDING).with_variant(JSON(), "sqlite"))
