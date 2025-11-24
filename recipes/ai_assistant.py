import os
import json
from openai import OpenAI, APIError, AuthenticationError, RateLimitError

# --- 1. Inicialización Global del Cliente ---
# Se intenta leer la clave de las variables de entorno (cargadas por settings.py)
API_KEY = os.getenv("OPENAI_API_KEY")

if API_KEY:
    try:
        # Se inicializa el cliente solo si la clave existe
        CLIENT = OpenAI(api_key=API_KEY)
        print("✅ Cliente de OpenAI inicializado correctamente.")
    except Exception as e:
        # Esto captura errores de inicialización inusuales
        print(f"❌ ERROR FATAL al inicializar OpenAI: {e}")
        CLIENT = None
else:
    # Si la clave no está en las variables de entorno
    CLIENT = None
    print("⚠️ API Key no encontrada. El servicio de IA estará desactivado.")
# ---------------------------------------------


def suggest_substitution(missing, substitute, recipe_title=None, recipe_text=None):
    """
    Llama al modelo GPT-5-nano para sugerir sustituciones culinarias.
    Utiliza el cliente global CLIENT.
    """

    # 1. Verificar si el cliente fue inicializado
    if CLIENT is None:
        return {
            "viable": "no disponible",
            "explicacion": "El servicio de IA no está disponible (API key no configurada).",
            "proporcion": "N/A",
            "ajustes": "N/A",
            "riesgos": "N/A",
            "confianza": 0.0
        }

    prompt = f"""
Eres un chef experto en sustituciones de ingredientes.

Usuario pregunta:
¿Puedo sustituir "{missing}" por "{substitute}" en la receta "{recipe_title or "sin título"}"?

Detalles de receta:
{recipe_text or "No se especifican más detalles."}

Responde SOLO un JSON válido con este formato EXACTO:

{{
  "viable": "si" | "no" | "depende",
  "explicacion": "texto en español",
  "proporcion": "formato de sustitución recomendado",
  "ajustes": "ajustes necesarios en sabor, textura o técnica",
  "riesgos": "posibles problemas",
  "confianza": 0.0
}}
"""

    try:
        # Asumo que 'responses.create' es un wrapper en tu librería
        response = CLIENT.responses.create(
            model="gpt-5-nano",
            input=prompt,
            response_format="json"
        )

        return json.loads(response.output_text)

    except AuthenticationError as e:
        # ❌ ERROR 401: Clave API inválida o expirada
        return {
            "viable": "no disponible",
            "explicacion": f"Error 401: Clave API inválida. Por favor, revisa la configuración.",
            "confianza": 0.0
        }
    except RateLimitError as e:
        # ❌ ERROR 429: Se ha excedido el límite de llamadas
        return {
            "viable": "no disponible",
            "explicacion": f"Error 429: Límite de llamadas excedido. Intenta de nuevo más tarde.",
            "confianza": 0.0
        }
    except APIError as e:
        # ❌ Captura otros errores de la API (servidor, modelo, etc.)
        return {
            "viable": "no disponible",
            "explicacion": f"Error de la API ({e.status_code}): El servicio de IA falló.",
            "confianza": 0.0
        }
    except Exception as e:
        # ❌ Captura errores no relacionados con la API (ej. JSON malformado)
        return {
            "viable": "no disponible",
            "explicacion": f"Error desconocido al procesar la respuesta: {str(e)}",
            "confianza": 0.0
        }