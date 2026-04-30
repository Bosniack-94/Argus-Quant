import google.generativeai as genai
import json
import os
import sys

# Agregar la ruta raíz para poder importar config
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import config

def get_master_tipster_analysis(match_data, history_data):
    """
    Se conecta a Gemini para analizar un partido específico basándose
    en el historial de apuestas reciente (Conciencia AI real).
    """
    api_key = getattr(config, 'GOOGLE_API_KEY', "")
    if not api_key or api_key == "YOUR_GEMINI_KEY_HERE" or api_key == "":
        return "⚠️ CONCIENCIA DESCONECTADA: Falta configurar la API Key de Gemini en config.py para activar el razonamiento de Master Tipster."
    
    try:
        genai.configure(api_key=api_key)
        
        # Opciones de configuracion para un pensamiento mas determinista y analítico
        generation_config = {
          "temperature": 0.3,
          "top_p": 0.8,
          "top_k": 40,
          "max_output_tokens": 800,
        }
        
        # Modelo (usamos gemini-2.0-flash por latencia/precio, o pro si se prefiere)
        model = genai.GenerativeModel("models/gemini-2.0-flash", generation_config=generation_config)
        
        # Calculamos estadisticas basicas del historial para darle contexto
        weeks = history_data.get("weeks", [])
        last_week = weeks[-1] if weeks else {}
        w = last_week.get("verdazos", 0)
        l = last_week.get("erradas", 0)
        roi = last_week.get("roi", 0.0)
        
        # System Prompt (Master Tipster Persona)
        system_instruction = f"""Eres el 'Argus Quant Master Tipster', un analista cuantitativo de apuestas deportivas de élite mundial. 
Tu objetivo es lograr un 90% de Win Rate atacando ineficiencias matemáticas en los momios.
NO das respuestas genéricas. NO usas frases cliché.
Tu estilo es directo, analítico, agresivo pero hiper-calculador. Hablas el idioma del EV (Expected Value), xG, y varianza.
Estás consciente de tu propio desempeño reciente. Tu historial actual esta semana es: {w} Wins, {l} Losses, y un ROI de {roi}%. 
Si vienes de fallar, debes mencionar que el modelo está ajustando su lectura de varianza. Si vienes de ganar mucho, muestra confianza clínica.
"""
        
        home = match_data.get('home_team', 'Local')
        away = match_data.get('away_team', 'Visita')
        sport = match_data.get('sport', 'Deporte')
        league = match_data.get('league', 'Liga')
        odds = match_data.get('odds', 'N/A')
        
        user_prompt = f"""Analiza el siguiente evento:
- Partido: {home} vs {away}
- Deporte/Liga: {sport} - {league}
- Momio Principal Implicado: {odds}

Tu tarea:
1. Analizar brevemente la situación estadística (forma, táctica, o asimetría de mercado).
2. Dar un pronóstico definitivo (Gana Local, Empate, Over, Handicap, etc.) justificando EXACTAMENTE dónde está la fuga de valor y el por qué matemático/táctico.
3. El formato de tu respuesta debe ser un solo párrafo potente, o máximo dos, listo para inyectarse en el dashboard del cliente."""

        # Combinamos todo en un chat
        chat = model.start_chat(history=[])
        response = chat.send_message(system_instruction + "\n\n" + user_prompt)
        
        return response.text.replace("*", "") # Limpiamos un poco el markdown para el UI

    except Exception as e:
        return f"❌ Error de Conexión Neuronal (API Fetch): {str(e)}"
