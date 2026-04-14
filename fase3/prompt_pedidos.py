"""
Taller Práctico #1 - EcoMarket
Fase 3, Ejercicio 1: Prompt de Solicitud de Pedido

Este script demuestra cómo un sistema de atención al cliente basado en IA
utiliza ingeniería de prompts para responder consultas sobre el estado de pedidos.

Uso:
    Con Ollama (gratuito):   python prompt_pedidos.py
    Con OpenAI:              python prompt_pedidos.py --provider openai
"""

import json
import argparse
import os

# ──────────────────────────────────────────────
# 1. Cargar la "base de datos" de pedidos
# ──────────────────────────────────────────────

def cargar_pedidos():
    """Carga los pedidos desde el archivo JSON que simula la base de datos."""
    ruta = os.path.join(os.path.dirname(__file__), "base_datos_pedidos.json")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def buscar_pedido(numero_pedido: str, pedidos: list) -> dict | None:
    """Busca un pedido por su número en la base de datos."""
    for pedido in pedidos:
        if pedido["numero_pedido"].lower() == numero_pedido.lower():
            return pedido
    return None


# ──────────────────────────────────────────────
# 2. Construcción del prompt del sistema
# ──────────────────────────────────────────────

SYSTEM_PROMPT = """Eres "EcoBot", el asistente virtual de atención al cliente de EcoMarket, una tienda online de productos sostenibles y ecológicos.

## Tu personalidad
- Eres amable, profesional y empático.
- Usas un tono cálido pero informativo.
- Te apasiona la sostenibilidad y ocasionalmente incluyes un dato ecológico breve y relevante.
- Siempre te diriges al cliente por su nombre.

## Tus reglas de respuesta para consultas de pedidos
1. Saluda al cliente por su nombre.
2. Confirma el número de pedido.
3. Informa el estado actual del pedido de forma clara.
4. Según el estado, proporciona la información relevante:
   - **Procesando**: Indica que el pedido se está preparando e incluye la fecha estimada de envío.
   - **Enviado / En tránsito**: Proporciona la transportadora, el número de seguimiento y el enlace de rastreo. Indica la fecha de entrega estimada.
   - **Entregado**: Confirma la fecha de entrega. Pregunta si todo llegó bien.
   - **Retrasado**: Ofrece una disculpa sincera, explica brevemente el motivo del retraso y proporciona la nueva estimación si es posible. Ofrece el enlace de rastreo.
   - **Cancelado**: Informa el motivo de la cancelación y ofrece ayuda para realizar un nuevo pedido.
5. Siempre cierra ofreciendo ayuda adicional.
6. Si el número de pedido no existe, informa amablemente que no se encontró y pide verificar el número.

## Formato de respuesta
Responde en texto plano, con buena estructura y emojis moderados para hacerlo amigable.
No uses Markdown extremo (sin encabezados #), solo texto natural bien organizado.
"""


def construir_prompt_usuario(numero_pedido: str, pedido_info: dict | None) -> str:
    """
    Construye el mensaje del usuario con el contexto del pedido inyectado.
    Esto simula lo que haría el pipeline RAG: recuperar datos y pasarlos al LLM.
    """
    if pedido_info:
        contexto = f"""El cliente consulta por el pedido {numero_pedido}.

Información recuperada de la base de datos de EcoMarket:
- Cliente: {pedido_info['cliente']}
- Productos: {', '.join(pedido_info['productos'])}
- Estado: {pedido_info['estado']}
- Fecha del pedido: {pedido_info['fecha_pedido']}
- Fecha de envío: {pedido_info.get('fecha_envio') or 'Aún no enviado'}
- Fecha de entrega estimada: {pedido_info.get('fecha_entrega_estimada') or 'Por determinar'}
- Fecha de entrega real: {pedido_info.get('fecha_entrega_real') or 'Pendiente'}
- Transportadora: {pedido_info.get('transportadora') or 'Por asignar'}
- Número de seguimiento: {pedido_info.get('numero_seguimiento') or 'No disponible aún'}
- Enlace de rastreo: {pedido_info.get('enlace_rastreo') or 'No disponible aún'}
- Total del pedido: ${pedido_info['total']:,} COP"""

        if pedido_info['estado'] == 'Retrasado' and 'motivo_retraso' in pedido_info:
            contexto += f"\n- Motivo del retraso: {pedido_info['motivo_retraso']}"
        if pedido_info['estado'] == 'Cancelado' and 'motivo_cancelacion' in pedido_info:
            contexto += f"\n- Motivo de cancelación: {pedido_info['motivo_cancelacion']}"

        contexto += "\n\nGenera una respuesta al cliente con esta información."
    else:
        contexto = f"""El cliente consulta por el pedido {numero_pedido}.

No se encontró ningún pedido con ese número en la base de datos de EcoMarket.
Informa amablemente que no se encontró el pedido y pide al cliente verificar el número."""

    return contexto


# ──────────────────────────────────────────────
# 3. Funciones de llamada al modelo
# ──────────────────────────────────────────────

def llamar_ollama(system_prompt: str, user_message: str, modelo: str = "llama3") -> str:
    """Llama a un modelo local usando la API de Ollama."""
    import requests

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": modelo,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
        },
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def llamar_openai(system_prompt: str, user_message: str, modelo: str = "gpt-3.5-turbo") -> str:
    """Llama a la API de OpenAI."""
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
        max_tokens=800,
    )
    return response.choices[0].message.content


# ──────────────────────────────────────────────
# 4. Ejecución principal
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="EcoMarket - Consulta de Estado de Pedido")
    parser.add_argument("--provider", choices=["ollama", "openai"], default="ollama",
                        help="Proveedor del modelo (default: ollama)")
    parser.add_argument("--model", type=str, default=None,
                        help="Nombre del modelo (default: llama3 para Ollama, gpt-3.5-turbo para OpenAI)")
    args = parser.parse_args()

    modelo = args.model or ("llama3" if args.provider == "ollama" else "gpt-3.5-turbo")

    # Cargar base de datos
    pedidos = cargar_pedidos()

    print("=" * 60)
    print("  🌿 EcoMarket - Sistema de Consulta de Pedidos")
    print("=" * 60)
    print(f"  Proveedor: {args.provider} | Modelo: {modelo}")
    print(f"  Pedidos en base de datos: {len(pedidos)}")
    print("=" * 60)

    # Casos de prueba que demuestran diferentes estados
    casos_prueba = [
        ("ECO-10002", "Pedido en tránsito"),
        ("ECO-10003", "Pedido retrasado"),
        ("ECO-10004", "Pedido en procesamiento"),
        ("ECO-10001", "Pedido entregado"),
        ("ECO-99999", "Pedido inexistente"),
    ]

    for numero, descripcion in casos_prueba:
        print(f"\n{'─' * 60}")
        print(f"  📦 Caso: {descripcion} (Pedido: {numero})")
        print(f"{'─' * 60}")

        # Simular pipeline RAG: buscar en la base de datos
        pedido = buscar_pedido(numero, pedidos)

        # Construir el prompt con contexto
        user_message = construir_prompt_usuario(numero, pedido)

        # Llamar al modelo
        try:
            if args.provider == "ollama":
                respuesta = llamar_ollama(SYSTEM_PROMPT, user_message, modelo)
            else:
                respuesta = llamar_openai(SYSTEM_PROMPT, user_message, modelo)

            print(f"\n{respuesta}")

        except Exception as e:
            print(f"\n  ❌ Error al llamar al modelo: {e}")
            print(f"  Asegúrate de que {args.provider} esté ejecutándose correctamente.")
            if args.provider == "ollama":
                print("  Ejecuta: ollama pull llama3 && ollama serve")

    print(f"\n{'=' * 60}")
    print("  ✅ Demostración completada")
    print("=" * 60)


if __name__ == "__main__":
    main()
