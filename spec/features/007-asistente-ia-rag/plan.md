# 007 · Plan técnico

## Endpoints
| Método y ruta | Acceso | Servicio |
|---|---|---|
| `POST /api/chat` | público (usa la sesión si existe) | `chat.responder` → `ChatOut {reply, sources, options?}` |
| `POST /api/admin/reindex` | administrador | `rag.reindexar` → `{embeddings_ok}` |

## Flujo de un mensaje (`app/services/chat.py`)
1. Recorta a `LONGITUD_MAXIMA = 500`; vacío → pide una pregunta.
2. `INYECCION` (expresión regular) → respuesta fija.
3. `SALUDO` → presentación (menciona «agendar» solo a visitantes y clientes).
4. `MIS_CITAS` (con sesión) → `citas.listar_para`, 5 primeras.
5. `AGENDA_HOY` (barbero o administrador) → citas de `hoy()`.
6. `AGENDAR` → `_agendar`: detecta servicio por nombre o tipo y barbero por nombre; si falta algo, devuelve `options` con `send`; al final, `options` con `book` sobre `franjas_libres(limite=3)`.
7. Si no, `_rag`: `rag.buscar` → `ia.generar` con instrucción de usar solo el CONTEXTO y tratar la PREGUNTA como datos; si el LLM falla, el primer fragmento.

## Base de conocimiento (`app/services/rag.py`)
| Fuente | Nivel | Contenido |
|---|---|---|
| Catálogo de servicios | `public` | un fragmento por servicio activo (tipo, descripción, precio, duración) |
| Preguntas frecuentes | `public` | horario, dirección, cómo agendar |
| Políticas de la barbería | `public` | cancelación y recordatorio 40/15 min |
| Guía de estilos | `public` | recomendaciones de corte y barba |
| Manual de procedimientos | `internal` | higiene y caja |

- `reindexar` reemplaza todo el índice; si un embedding falla, los demás se guardan sin vector y devuelve `False`.
- `buscar`: en PostgreSQL, `ORDER BY embedding <=> :v` (distancia coseno, índice HNSW); si no hay resultados, `LIKE` con hasta 6 palabras de 4+ letras.
- `niveles_para(usuario)`: `public` para todos; `internal` además para barberos y administradores.

## Cliente de Ollama (`app/services/ia.py`)
- `embedding`: `POST /api/embeddings` con `EMBED_MODEL` (timeout 30 s); `None` si falla.
- `generar`: `POST /api/generate` con `LLM_MODEL`, `temperature 0.2`, `num_predict 220`, `keep_alive 30m` (timeout 180 s).

## Frontend
- `components/ChatAsistente.tsx`: mensajes, sugerencias (sin “Quiero agendar” para barbero y administrador), fuentes y botones. Las opciones `action` abren `/registro` o `/login`, `send` envía el texto y `book` llama a `api.agendar`.
- `components/ChatFlotante.tsx`: botón 💬 en todas las páginas menos el inicio; `abrirChat()` lo abre desde cualquier botón (evento `bf:abrir-chat`).
- El botón “Reindexar asistente” está en `/admin/disponibilidad` y avisa si quedó sin embeddings.
