"""Cliente de Ollama (IA local): embeddings y generación de texto."""
import logging

import httpx

from app.config import get_settings

log = logging.getLogger(__name__)


def embedding(texto: str) -> list[float] | None:
    """Vector del texto, o None si Ollama no responde o aún no descargó el modelo."""
    s = get_settings()
    try:
        r = httpx.post(f"{s.ollama_url}/api/embeddings", json={"model": s.embed_model, "prompt": texto}, timeout=30)
        r.raise_for_status()
        return r.json()["embedding"]
    except (httpx.HTTPError, KeyError, ValueError) as e:
        log.debug("embedding no disponible: %s", e)
        return None


def generar(prompt: str) -> str:
    s = get_settings()
    r = httpx.post(f"{s.ollama_url}/api/generate", timeout=180,
                   json={"model": s.llm_model, "prompt": prompt, "stream": False, "keep_alive": "30m",
                         "options": {"temperature": 0.2, "num_predict": 220}})
    r.raise_for_status()
    return r.json()["response"].strip()
