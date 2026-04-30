import os
import json
import google.generativeai as genai
from PIL import Image

def get_api_key():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f).get('google_api_key', '')
    return ""

def init_gemini():
    api_key = get_api_key()
    if not api_key:
        raise ValueError("No se encontró la API Key de Google Generative AI en config.json")
    genai.configure(api_key=api_key)

def extract_match_data_from_images(image_paths):
    """
    Analiza capturas de pantalla de Sofascore/Apuestas y extrae las métricas
    matemáticas esenciales en formato JSON.
    Intenta usar la versión Pro, con fallback a Flash.
    """
    init_gemini()
    
    # Intenta localizar el mejor modelo disponible (Priorizando Pro de las versiones más nuevas 2.x o 1.5)
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Use the proven model from the current dashboard version
    target_model = 'gemini-2.0-flash'
    
    try:
        model = genai.GenerativeModel(target_model)
    except Exception:
        # Fallback ultra-seguro
        model = genai.GenerativeModel('gemini-2.0-flash')

    prompt = """
    Eres un Analista Cuantitativo Deportivo de Élite ('Argus Quant Data Extractor').
    Tu tarea es observar estas capturas de pantalla (estadísticas de fútbol de sitios como Sofascore, o momios de Codere/Caliente) 
    y extraer datos crudos específicos en formato JSON estricto.

    Busca y extrae la siguiente información:
    1. Nombre del Equipo Local ('home_team').
    2. Nombre del Equipo Visitante ('away_team').
    3. Goles Esperados (xG) del Local ('xg_home'). Si no está la métrica xG directamente, calcula un estimado basado en Tiros a Puerta (aprox 0.11 xG por tiro) y Posesión, devolviendo un float. Mínimo 0.5.
    4. Goles Esperados (xG) del Visitante ('xg_away'). Misma regla.
    5. El momio Americano del Local ('odds'). Ej: +110 o -150. Si no aparece en la imagen, devuelve -110 por defecto.

    REGLA ESTRICTA: Tu respuesta DEBE SER ÚNICAMENTE UN OBJETO JSON VÁLIDO. No añadas Markdown (como ```json), ni saludos, ni explicaciones.
    
    Formato esperado:
    {
        "home_team": "Nombre",
        "away_team": "Nombre",
        "xg_home": 1.4,
        "xg_away": 0.8,
        "odds": -110
    }
    """
    
    pil_images = []
    for path in image_paths:
        try:
            pil_images.append(Image.open(path))
        except Exception as e:
            print(f"Error abriendo imagen {path}: {e}")
            
    if not pil_images:
        raise ValueError("No se pudieron cargar las imágenes proporcionadas.")

    # Convertir a inputs para el generador
    inputs = [prompt] + pil_images
    
    response = model.generate_content(inputs)
    
    # Limpieza del string de respuesta por si el modelo metió backticks de markdown
    raw_text = response.text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
        
    try:
        data = json.loads(raw_text.strip())
        data['model_used'] = target_model # Para debug en el UI
        return data
    except json.JSONDecodeError:
        raise ValueError(f"El modelo no devolvió un JSON válido. Respuesta cruda: {raw_text}")
