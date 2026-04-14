# Fase 1: Selección y Justificación del Modelo de IA

## 1. Modelo Seleccionado

**Solución híbrida: LLM open-source (LLaMA 3 / Mistral) con Retrieval-Augmented Generation (RAG), conectado a la base de datos interna de EcoMarket.**

La arquitectura propuesta no depende de un solo modelo, sino de un sistema compuesto por:

- Un **LLM open-source** (como LLaMA 3 8B o Mistral 7B) como motor de generación de lenguaje natural.
- Un **pipeline RAG** que recupera información en tiempo real desde las bases de datos de EcoMarket (catálogo de productos, estado de envíos, historial de clientes, políticas de devolución).
- Un **módulo de escalamiento** que detecta cuándo una consulta excede la capacidad del modelo y la transfiere a un agente humano con el contexto completo de la conversación.

## 2. ¿Por qué esta arquitectura y no otra?

### Descartando alternativas

| Alternativa | Razón para descartarla |
|---|---|
| **GPT-4 / Claude como API directa** | Costo elevado por volumen (miles de consultas diarias). Dependencia de un proveedor externo para datos sensibles de clientes. Sin embargo, podría usarse como modelo de respaldo para los casos complejos del 20%. |
| **Fine-tuning de un LLM con datos propios** | Requiere reentrenamiento constante cada vez que cambian los productos, precios o políticas. El catálogo de EcoMarket es dinámico (productos sostenibles con rotación frecuente), lo que hace que el fine-tuning quede desactualizado rápidamente. |
| **Chatbot basado en reglas (no IA generativa)** | No escala bien. Cada nueva pregunta requiere programar una nueva regla. No tiene la fluidez conversacional que esperan los clientes modernos. |

### Ventajas de la solución híbrida con RAG

1. **Precisión factual**: RAG permite al modelo consultar la base de datos en tiempo real. Cuando un cliente pregunta por su pedido #12345, el modelo no "adivina" la respuesta: la recupera directamente del sistema de EcoMarket. Esto minimiza el riesgo de alucinaciones.

2. **Fluidez conversacional**: El LLM se encarga de formular respuestas naturales, empáticas y adaptadas al tono de la marca. La combinación de datos reales + generación de lenguaje natural produce respuestas que son tanto precisas como humanas.

3. **Actualización sin reentrenamiento**: Al cambiar un producto o una política, solo se actualiza la base de datos. No hay necesidad de reentrenar el modelo, lo que reduce costos operativos y tiempo de mantenimiento.

4. **Escalamiento inteligente**: El sistema clasifica automáticamente las consultas. El 80% repetitivo (estado de pedido, devoluciones, características de producto) lo maneja el modelo. El 20% complejo (quejas, problemas técnicos) se escala a un agente humano, pero el agente recibe un resumen del contexto generado por la IA, lo que acelera también la atención humana.

## 3. Arquitectura Propuesta

```
┌─────────────────────────────────────────────────────────┐
│                    Cliente de EcoMarket                  │
│              (Chat web / Email / Redes sociales)         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Capa de Ingesta y Clasificación             │
│  - Recibe la consulta del cliente                       │
│  - Clasifica: ¿repetitiva (80%) o compleja (20%)?       │
│  - Si es compleja → escala a agente humano con contexto │
└─────────────────────┬───────────────────────────────────┘
                      │ (consulta repetitiva)
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   Pipeline RAG                          │
│  1. Embedding de la consulta del cliente                │
│  2. Búsqueda vectorial en la base de datos de EcoMarket│
│     - Catálogo de productos                             │
│     - Estado de envíos y pedidos                        │
│     - Políticas de devolución                           │
│  3. Contexto recuperado se inyecta en el prompt del LLM│
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│            LLM Open-Source (LLaMA 3 / Mistral)          │
│  - Recibe: prompt del sistema + contexto RAG + consulta │
│  - Genera respuesta natural, empática y precisa         │
│  - Aplica guardrails de seguridad y tono de marca       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 Respuesta al Cliente                     │
│  - Formato adaptado al canal (chat, email, RRSS)        │
│  - Log para métricas y mejora continua                  │
└─────────────────────────────────────────────────────────┘
```

## 4. Justificación según criterios clave

| Criterio | Evaluación |
|---|---|
| **Costo** | Bajo-medio. Un LLM open-source se puede ejecutar en infraestructura propia o en la nube con costos controlados. No se paga por token como con GPT-4. El costo principal es el servidor de inferencia. |
| **Escalabilidad** | Alta. El pipeline RAG es independiente del modelo, por lo que se pueden escalar los componentes de búsqueda y generación de forma separada. Se pueden agregar más réplicas del modelo según la demanda. |
| **Facilidad de integración** | Media-alta. Se requiere conectar el pipeline RAG con las bases de datos existentes de EcoMarket (probablemente vía APIs REST). Frameworks como LangChain o LlamaIndex simplifican enormemente esta integración. |
| **Calidad de respuesta** | Alta para consultas repetitivas (datos factuales + lenguaje natural). Media para consultas complejas (por eso se escalan a humanos). La combinación RAG + LLM minimiza alucinaciones y maximiza relevancia. |
| **Privacidad** | Los datos de clientes se procesan internamente (on-premise o en nube privada). No se envían a proveedores externos, lo que cumple con regulaciones de protección de datos. |
