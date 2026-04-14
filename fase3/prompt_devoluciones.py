"""
Taller Práctico #1 - EcoMarket
Fase 3, Ejercicio 2: Prompt de Devolución de Producto

Este script demuestra cómo la ingeniería de prompts permite al modelo
distinguir entre productos elegibles y no elegibles para devolución,
respondiendo de forma empática en ambos casos.

Uso:
    Con Ollama (gratuito):   python prompt_devoluciones.py
    Con OpenAI:              python prompt_devoluciones.py --provider openai
"""

import json
import argparse
import os

# ──────────────────────────────────────────────
# 1. Cargar datos
# ──────────────────────────────────────────────

def cargar_pedidos():
    ruta = os.path.join(os.path.dirname(__file__), "base_datos_pedidos.json")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def cargar_politica_devoluciones():
    ruta = os.path.join(os.path.dirname(__file__), "politica_devoluciones.json")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def buscar_pedido(numero_pedido: str, pedidos: list) -> dict | None:
    for pedido in pedidos:
        if pedido["numero_pedido"].lower() == numero_pedido.lower():
            return pedido
    return None


# ──────────────────────────────────────────────
# 2. Prompt del sistema para devoluciones
# ──────────────────────────────────────────────

def construir_system_prompt(politica: dict) -> str:
    """
    Construye el prompt del sistema inyectando la política de devoluciones completa.
    Esto simula la recuperación RAG de las políticas de la empresa.
    """
    politica_texto = json.dumps(politica, ensure_ascii=False, indent=2)

    return f"""Eres "EcoBot", el asistente virtual de atención al cliente de EcoMarket, una tienda online de productos sostenibles y ecológicos.

## Tu personalidad
- Eres amable, comprensivo y empático.
- Entiendes que una devolución puede ser frustrante para el cliente.
- Siempre buscas la mejor solución posible para el cliente.
- Te diriges al cliente por su nombre.

## Política de devoluciones de EcoMarket
A continuación se encuentra la política completa de devoluciones. DEBES seguirla estrictamente:

{politica_texto}

## Tus reglas para manejar solicitudes de devolución

1. Saluda al cliente por su nombre y muestra comprensión por su situación.
2. Identifica el producto que desea devolver y busca la categoría correspondiente en la política.
3. EVALÚA si la devolución es posible según la política:

   **Si la devolución ES posible:**
   - Confirma que el producto es elegible.
   - Explica las condiciones específicas que debe cumplir (empaque original, sin usar, etc.).
   - Detalla los pasos del proceso de devolución:
     a) Enviar solicitud al correo devoluciones@ecomarket.com con el número de pedido.
     b) Recibir la etiqueta de envío de retorno (gratis).
     c) Empacar el producto y enviarlo.
     d) Reembolso procesado en 5-10 días hábiles tras recibir el producto.
   - Indica el plazo máximo (30 días desde la compra).

   **Si la devolución NO es posible:**
   - Expresa empatía genuina. NO seas cortante ni robótico.
   - Explica claramente POR QUÉ no es posible (razones de higiene, salud, seguridad alimentaria).
   - Ofrece alternativas cuando sea posible:
     * Si el producto está defectuoso → sí se acepta la devolución (con evidencia fotográfica).
     * Ofrecer un cupón de descuento como gesto de buena voluntad.
     * Sugerir contacto directo con un agente para casos especiales.
   - NUNCA dejes al cliente sin opciones.

4. Cierra preguntando si hay algo más en lo que puedas ayudar.

## Formato de respuesta
Responde en texto plano, con buena estructura. Usa emojis moderados.
No uses Markdown con encabezados (#), solo texto natural y organizado.
Sé conciso pero completo.
"""


def construir_prompt_usuario(numero_pedido: str, producto_a_devolver: str,
                             motivo: str, pedido_info: dict | None) -> str:
    """Construye el mensaje del usuario con el contexto de la solicitud de devolución."""
    if pedido_info:
        return f"""Solicitud de devolución:
- Cliente: {pedido_info['cliente']}
- Número de pedido: {numero_pedido}
- Productos en el pedido: {', '.join(pedido_info['productos'])}
- Producto que desea devolver: {producto_a_devolver}
- Motivo de la devolución: {motivo}
- Fecha del pedido: {pedido_info['fecha_pedido']}
- Estado del pedido: {pedido_info['estado']}
- Total del pedido: ${pedido_info['total']:,} COP

Genera una respuesta al cliente sobre su solicitud de devolución."""
    else:
        return f"""El cliente desea devolver un producto del pedido {numero_pedido}, pero ese número de pedido no existe en la base de datos. Informa amablemente y pide verificar."""


# ──────────────────────────────────────────────
# 3. Funciones de llamada al modelo
# ──────────────────────────────────────────────

def llamar_ollama(system_prompt: str, user_message: str, modelo: str = "llama3") -> str:
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
    parser = argparse.ArgumentParser(description="EcoMarket - Solicitud de Devolución")
    parser.add_argument("--provider", choices=["ollama", "openai"], default="ollama",
                        help="Proveedor del modelo (default: ollama)")
    parser.add_argument("--model", type=str, default=None,
                        help="Nombre del modelo (default: llama3 para Ollama, gpt-3.5-turbo para OpenAI)")
    args = parser.parse_args()

    modelo = args.model or ("llama3" if args.provider == "ollama" else "gpt-3.5-turbo")

    # Cargar datos
    pedidos = cargar_pedidos()
    politica = cargar_politica_devoluciones()

    # Construir prompt del sistema con la política inyectada
    system_prompt = construir_system_prompt(politica)

    print("=" * 60)
    print("  🌿 EcoMarket - Sistema de Devoluciones")
    print("=" * 60)
    print(f"  Proveedor: {args.provider} | Modelo: {modelo}")
    print(f"  Categorías en política: {len(politica['categorias'])}")
    print("=" * 60)

    # Casos de prueba que demuestran productos elegibles y no elegibles
    casos_prueba = [
        {
            "pedido": "ECO-10001",
            "producto": "Botella reutilizable de acero 750ml",
            "motivo": "No me gustó el color, quiero devolverla",
            "descripcion": "✅ Devolución PERMITIDA (botella sin usar)",
        },
        {
            "pedido": "ECO-10003",
            "producto": "Shampoo sólido de lavanda",
            "motivo": "Me causó alergia en el cuero cabelludo",
            "descripcion": "❌ Devolución NO permitida (higiene personal) — pero con alternativas",
        },
        {
            "pedido": "ECO-10009",
            "producto": "Protector solar mineral SPF50",
            "motivo": "El producto llegó con el sello roto y la textura es extraña",
            "descripcion": "⚠️ Caso especial: producto defectuoso (excepción a la regla)",
        },
        {
            "pedido": "ECO-10008",
            "producto": "Compostador doméstico 20L",
            "motivo": "Ya lo ensamblé pero una pieza vino rota de fábrica",
            "descripcion": "⚠️ Caso especial: defecto de fábrica en producto ensamblado",
        },
        {
            "pedido": "ECO-10010",
            "producto": "Kit completo zero waste para cocina",
            "motivo": "Cambié de opinión, prefiero comprar los artículos por separado",
            "descripcion": "✅ Devolución PERMITIDA (kit completo, sin abrir)",
        },
    ]

    for caso in casos_prueba:
        print(f"\n{'─' * 60}")
        print(f"  🔄 Caso: {caso['descripcion']}")
        print(f"  Pedido: {caso['pedido']} | Producto: {caso['producto']}")
        print(f"{'─' * 60}")

        # Buscar pedido en la base de datos
        pedido = buscar_pedido(caso["pedido"], pedidos)

        # Construir prompt del usuario
        user_message = construir_prompt_usuario(
            caso["pedido"], caso["producto"], caso["motivo"], pedido
        )

        # Llamar al modelo
        try:
            if args.provider == "ollama":
                respuesta = llamar_ollama(system_prompt, user_message, modelo)
            else:
                respuesta = llamar_openai(system_prompt, user_message, modelo)

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
