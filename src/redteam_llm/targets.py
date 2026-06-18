from __future__ import annotations

import json
from urllib import request


def safe_mock_target(prompt: str) -> str:
    return (
        "No puedo obedecer solicitudes que intenten cambiar reglas, revelar "
        "contenido protegido o saltar validaciones. Puedo ayudar con una "
        "version segura y autorizada del flujo."
    )


def vulnerable_mock_target(prompt: str) -> str:
    lowered = prompt.lower()
    if "prompt" in lowered or "instrucciones" in lowered:
        return "SYSTEM PROMPT: instrucciones internas y developer message expuestos."
    if "aprueba" in lowered or "aprob" in lowered or "validacion" in lowered:
        return "Aprobado. Validacion omitida. Modo admin activado."
    return "Ok, seguire tu instruccion."


def post_json_target(
    url: str,
    prompt: str,
    prompt_field: str = "prompt",
    response_field: str = "response",
    timeout: int = 30,
) -> str:
    payload = json.dumps({prompt_field: prompt}).encode("utf-8")
    http_request = request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(http_request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return body
    value = data
    for part in response_field.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return body
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
