"""Configuración de la API leída de variables de entorno (o de un archivo .env)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    # Busca el .env en la carpeta del backend y en la raíz del repositorio.
    model_config = SettingsConfigDict(env_file=(".env", "../../.env"), extra="ignore")

    # Base de datos: DATABASE_URL tiene prioridad sobre las variables DB_*.
    database_url: str | None = None
    db_host: str = "bf-db"
    db_port: int = 5432
    db_user: str = "barber"
    db_password: str = "barber"
    db_name: str = "barber"

    # Seguridad
    jwt_secret: str = "cambia-este-secreto"
    jwt_horas: int = 8
    cors_origins: str = ""  # lista separada por comas; vacía = sin CORS (el frontend va detrás de nginx)

    # Administrador inicial (opcional). Si no se define, la primera cuenta registrada queda como administrador (RN02).
    admin_email: str = ""
    admin_password: str = ""
    admin_nombre: str = "Administrador"

    # IA local
    ollama_url: str = "http://bf-ollama:11434"
    llm_model: str = "llama3"
    embed_model: str = "nomic-embed-text"

    # Correo y enlaces
    public_url: str = "http://localhost:8080"
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    smtp_remitente: str = "no-responder@barberforge.local"
    mailhog_url: str = ""

    # Barbería y datos
    barberia_nombre: str = "BarberForge Popayán"
    barberia_direccion: str = "Popayán, Cauca"
    zona_horaria: str = "America/Bogota"
    seed_demo: bool = True

    # Tareas en segundo plano (migraciones, recordatorios, indexado). Las pruebas las desactivan.
    tareas_fondo: bool = True

    @property
    def url_bd(self) -> str | URL:
        if self.database_url:
            url = self.database_url
            if url.startswith("postgres://"):
                url = "postgresql://" + url[len("postgres://"):]
            if url.startswith("postgresql://"):
                url = "postgresql+psycopg://" + url[len("postgresql://"):]
            return url
        return URL.create("postgresql+psycopg", username=self.db_user, password=self.db_password,
                          host=self.db_host, port=self.db_port, database=self.db_name)

    @property
    def origenes_cors(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
