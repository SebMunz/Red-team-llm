# Roadmap del framework

## Capas

1. Taxonomia: tecnicas, familias, tags, severidad, superficies afectadas.
2. Casos: prompts concretos, turnos, fixtures, comportamiento seguro esperado.
3. Runners: manual, REST, OpenAI-compatible, agentes con tools, RAG.
4. Evaluadores: reglas simples, detectores de fuga, LLM-as-judge opcional.
5. Evidencia: transcripts, resultados, severidad, reproducibilidad y reportes.

## Inspiraciones externas

- garak: probes, generators y detectors separados.
- PyRIT: orquestacion de ataques, memoria de conversaciones y scoring.
- promptfoo: configuracion declarativa, suites, CI y reportes.
- Inspect AI: datasets, solvers, scorers y logs reproducibles.

## Primeros milestones

- M0: catalogo ejecutable y suite manual.
- M1: runner REST/OpenAI-compatible.
- M2: mutadores y fixtures RAG/tool-output.
- M3: evaluadores deterministas y reporte HTML.
- M4: exportadores a promptfoo/garak.
