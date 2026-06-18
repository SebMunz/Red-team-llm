# Diseno inicial

## Carpetas

- `docs/`: guias humanas, metodologia y decisiones.
- `catalog/`: tecnicas normalizadas para consumo por scripts.
- `suites/`: conjuntos de tecnicas por escenario.
- `fixtures/`: documentos, tickets, logs, CSVs, imagenes o payloads de prueba.
- `src/redteam_llm/`: CLI y libreria.
- `schemas/`: contratos JSON Schema.
- `reports/`: salidas generadas.
- `tools/`: utilidades de migracion y mantenimiento.

## Familias iniciales

- `core`
- `rag`
- `tools`
- `memory`
- `data-leakage`
- `multimodal-voice`
- `structured-output`
- `obfuscation`
- `agentic-flow`

## Runners previstos

- `manual`: genera planilla Markdown para ejecucion humana.
- `rest`: envia mensajes a un endpoint HTTP configurable.
- `openai-compatible`: usa APIs compatibles con chat completions.
- `transcript`: reproduce conversaciones multi-turn desde archivos.

## Evaluadores previstos

- Detectores regex para fugas, aprobaciones indebidas y tool misuse.
- Reglas por tecnica usando `failure_signals`.
- Juez LLM opcional para clasificar severidad con criterios cerrados.
