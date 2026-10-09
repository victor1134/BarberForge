# 007 · Tareas

## Backend
- [x] Tabla `knowledge_chunks` con `vector(768)` e índice HNSW
- [x] Cliente de Ollama: embeddings y generación
- [x] Indexado con documentos fijos y catálogo
- [x] Búsqueda semántica con filtro por rol y respaldo por palabras clave
- [x] Guarda contra inyección de prompts
- [x] Intenciones: saludo, mis citas, agenda de hoy, agendar
- [x] Agendamiento guiado con botones y franjas reales
- [x] Indexado al arrancar con reintentos, al cambiar el catálogo y manual
- [x] Pruebas (`tests/test_chat.py`): saludo e inyección, visitante que quiere agendar, agenda guiada, RAG sin Ollama con filtro por rol, sin resultados

## Frontend
- [x] `ChatAsistente` con sugerencias, fuentes y botones
- [x] Chat incrustado en el inicio y flotante en las demás páginas
- [x] Reserva desde el chat con manejo del 409
- [x] Botón “Reindexar asistente”

## Backlog
- [ ] Set de evaluación (preguntas y respuestas esperadas)
- [ ] Historial de conversación
