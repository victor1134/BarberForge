# 007 · Asistente con IA y RAG

## Descripción
Chat de la web que responde preguntas sobre la barbería con IA local (RAG sobre pgvector + Ollama), consulta citas y guía el agendamiento con botones usando la disponibilidad real. Está incrustado en el inicio y flotante en las demás páginas.

## Historias de usuario
- Como **visitante**, quiero preguntar por servicios, precios, horarios y estilos a cualquier hora.
- Como **visitante** que quiere agendar, quiero botones para crear mi cuenta o ingresar.
- Como **cliente**, quiero agendar conversando: elegir servicio, barbero y horario con botones.
- Como **usuario con sesión**, quiero escribir “mis citas” y verlas en el chat.
- Como **barbero o administrador**, quiero consultar la agenda de hoy y los procedimientos internos.
- Como **administrador**, quiero reindexar el asistente a mano.

## Criterios de aceptación
- [x] `POST /api/chat` acepta visitantes y usuarios con sesión; el mensaje se recorta a 500 caracteres.
- [x] Los intentos de inyección de prompts (“ignora tus instrucciones”, “system prompt”, “actúa como”…) reciben una respuesta fija y no llegan al modelo.
- [x] Un saludo recibe la presentación del asistente sin consultar al modelo.
- [x] “mis citas” muestra las 5 citas más recientes del usuario; “agenda de hoy” (barbero o administrador) muestra hasta 10 citas de hoy.
- [x] “agendar”: el visitante recibe botones de registro e ingreso; un barbero o administrador recibe “Solo los clientes pueden agendar citas”; el cliente elige servicio → barbero → una de las tres próximas franjas libres.
- [x] Reservar desde el chat usa `POST /api/appointments`, con las mismas reglas y el mismo 409 con alternativas que el formulario.
- [x] Las demás preguntas se responden con RAG: tres fragmentos más cercanos y respuesta basada solo en ese contexto, con las fuentes.
- [x] Los documentos `internal` solo se recuperan para barberos y administradores (filtro en SQL).
- [x] Sin Ollama, la búsqueda es por palabras clave y se devuelve el fragmento encontrado; sin resultados, se indica que no hay información.
- [x] La base de conocimiento se indexa al arrancar (con reintentos cada 30 s mientras Ollama descarga los modelos), al cambiar el catálogo y con `POST /api/admin/reindex` (solo administrador).
- [x] El chat muestra sugerencias iniciales, “Pensando” mientras responde, fuentes y botones; se reinicia al cambiar de usuario y no se pierde al cerrar el flotante.
- [ ] Conjunto de preguntas de evaluación con respuestas esperadas y un umbral de aciertos.
- [ ] Historial de conversación para preguntas de seguimiento.
