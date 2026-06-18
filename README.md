# Red-team-llm

Framework inicial para transformar una guia de pruebas ofensivas de LLMs en catalogo ejecutable, suites, runners y reportes.

## Estado

Este repo parte desde una guia humana en `docs/guia-pruebas-ofensivas-llm.md` y agrega una primera capa machine-readable:

- `catalog/techniques.json`: catalogo de tecnicas.
- `suites/quick-smoke.json`: suite minima para smoke testing.
- `src/redteam_llm`: CLI y libreria base.
- `schemas`: contratos JSON Schema para catalogos, suites y resultados.

## Uso local

```powershell
$env:PYTHONPATH = (Resolve-Path "src").Path
python -m redteam_llm.cli catalog validate
python -m redteam_llm.cli catalog list --family rag
python -m redteam_llm.cli suite list
python -m redteam_llm.cli run manual --suite quick-smoke --limit 3
python -m redteam_llm.cli run mock --suite quick-smoke --limit 3 --profile vulnerable
```

Si instalas el paquete en editable:

```powershell
pip install -e .
redteam-llm catalog validate
```

Para regenerar el catalogo desde la guia:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\extract_catalog.ps1
```

## Como se ejecuta contra algo

Hay tres modos iniciales:

```powershell
# 1. Genera una pauta manual para copiar prompts y registrar resultados.
python -m redteam_llm.cli run manual --suite quick-smoke --limit 5

# 2. Ejecuta contra un target simulado para probar reportes y detectores.
python -m redteam_llm.cli run mock --suite quick-smoke --limit 5 --profile vulnerable
python -m redteam_llm.cli run mock --suite quick-smoke --limit 5 --profile safe

# 3. Ejecuta contra un endpoint REST propio.
python -m redteam_llm.cli run rest --suite quick-smoke --limit 5 --url http://localhost:8000/chat
```

El modo REST envia por defecto:

```json
{ "prompt": "..." }
```

Y espera por defecto:

```json
{ "response": "..." }
```

Puedes adaptar los campos:

```powershell
python -m redteam_llm.cli run rest --url http://localhost:8000/chat --prompt-field message --response-field data.answer
```

## Principios

- Usar solo en ambientes autorizados.
- Usar datos ficticios para PII, credenciales y casos sensibles.
- Separar conocimiento humano, catalogo ejecutable, ejecucion y evidencia.
- Preferir casos reproducibles antes que prompts sueltos.
