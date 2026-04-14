# Taller Práctico #1 — Optimización de la Atención al Cliente en EcoMarket

## Descripción

Este repositorio contiene la solución al Taller Práctico #1 del curso, centrado en diseñar una solución de IA generativa para optimizar el servicio de atención al cliente de **EcoMarket**, una empresa de e-commerce de productos sostenibles.

## Estructura del Repositorio

```
taller-ecomarket/
├── README.md                          # Este archivo
├── fase1_seleccion_modelo.md          # Selección y justificación del modelo de IA
├── fase2_evaluacion_critica.md        # Fortalezas, limitaciones y riesgos éticos
└── fase3/
    ├── requirements.txt               # Dependencias de Python
    ├── base_datos_pedidos.json        # Base de datos simulada de pedidos
    ├── politica_devoluciones.json     # Política de devoluciones por categoría
    ├── prompt_pedidos.py              # Prompt de consulta de estado de pedido
    └── prompt_devoluciones.py         # Prompt de devolución de producto
```

## Cómo ejecutar la Fase 3

### Requisitos previos

- Python 3.8 o superior
- Una API key de OpenAI **o** acceso a un modelo local vía [Ollama](https://ollama.com)

### Opción A: Usando un modelo open-source con Ollama (recomendado, gratuito)

1. Instala Ollama desde https://ollama.com
2. Descarga un modelo:
   ```bash
   ollama pull llama3
   ```
3. Instala las dependencias:
   ```bash
   cd fase3
   pip install -r requirements.txt
   ```
4. Ejecuta los scripts:
   ```bash
   python prompt_pedidos.py
   python prompt_devoluciones.py
   ```

### Opción B: Usando la API de OpenAI

1. Configura tu API key como variable de entorno:
   ```bash
   export OPENAI_API_KEY="tu-api-key-aquí"
   ```
2. Instala las dependencias:
   ```bash
   cd fase3
   pip install -r requirements.txt
   ```
3. Ejecuta los scripts con el flag `--provider openai`:
   ```bash
   python prompt_pedidos.py --provider openai
   python prompt_devoluciones.py --provider openai
   ```

## Autor

Estudiante — Curso de Inteligencia Artificial Generativa
