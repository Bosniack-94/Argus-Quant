import requests
import json
import os
import streamlit as st

def get_telegram_credentials():
    """Extracts Telegram bot token and chat ID from config or environment"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    token = ""
    chat_id = ""
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            cfg = json.load(f)
            token = cfg.get("telegram_bot_token", "")
            chat_id = cfg.get("telegram_chat_id", "")
            
    return token, chat_id

def send_alert(message_html: str, parse_mode="HTML"):
    """
    Sends a pre-formatted HTML or Markdown message to the configured Telegram chat.
    Returns True if successful, False otherwise.
    """
    token, chat_id = get_telegram_credentials()
    
    if not token or not chat_id:
        st.warning("⚠️ Faltan las credenciales de Telegram en config.json (telegram_bot_token, telegram_chat_id).")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_html,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Error Telegram API: {response.text}")
            return False
    except Exception as e:
        st.error(f"Fallo de conexión Telegram: {e}")
        return False

def format_vip_pick(match_title: str, prediction: str, odds: str, probability: float, ev_percentage: float) -> str:
    """
    Formats the EV Math into a beautiful HTML string ready for the Telegram channel.
    """
    html = f"💎 <b>ALERTA Argus ELITE</b> 💎\n\n"
    html += f"🏟 <b>Evento:</b> {match_title}\n"
    html += f"🎯 <b>Selección:</b> {prediction}\n"
    html += f"📈 <b>Momio:</b> {odds}\n\n"
    
    html += f"<i>--- Métricas Cuantitativas ---</i>\n"
    html += f"🧠 <b>Probabilidad Real:</b> {probability:.1f}%\n"
    html += f"🔥 <b>Valor Detectado (EV):</b> +{ev_percentage:.1f}%\n\n"
    
    if ev_percentage >= 15.0:
        html += f"⚠️ <b>ESTADO DE ALTA CONFIANZA</b> ⚠️\n"
        html += f"El algoritmo detectó un gran fallo en el mercado.\n\n"
        
    html += f"📡 <i>Enviado por Argus Quant Motor</i>"
    
    return html

def format_war_room_report(team_h: str, team_a: str, xgh: float, xga: float, top_3_markets: list) -> str:
    """
    Formats the 5-market advanced analysis into a Telegram-friendly HTML message.
    """
    html = f"🧪 <b>WAR ROOM: REPORTE AVANZADO</b> 🧪\n\n"
    html += f"⚽ <b>{team_h} vs {team_a}</b>\n"
    html += f"📊 <i>Goles Esperados (xG): {xgh:.2f} vs {xga:.2f}</i>\n\n"
    
    html += "🏆 <b>TOP 3 MERCADOS MATEMÁTICOS:</b>\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    for i, market in enumerate(top_3_markets):
        html += f"{medals[i]} <b>{market['name']}</b> ({market['prob']:.1f}%)\n"
    
    html += f"\n📡 <i>Enviado por Argus Quant Motor de Poisson</i>"
    return html
