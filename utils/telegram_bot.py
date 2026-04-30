import requests
import config
import threading
import time

def send_Argus_alert(message):
    """
    Envía una notificación push a Telegram.
    """
    if config.TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(f"[DEBUG TELEGRAM]: {message}")
        return False
        
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error enviando alerta Telegram: {e}")
        return False

def send_premium_diamond_alert(matchup, score, odds, stake_pct, reasoning, deep_link="https://t.me/ArgusAI_Bot"):
    """
    🥇 DISEÑO DE ALERTA DIAMANTE (Fase 18)
    Envía una alerta profesional con barra de progreso y botón de acción.
    """
    if config.TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print(f"[DEBUG VIP CHANNEL]: {matchup} - {score}/100")
        return False
        
    # Crear barra de progreso visual (ej: 🟦🟦🟦🟦⬜)
    filled = int(score / 20)
    bar = "🟦" * filled + "⬜" * (5 - filled)
    
    message = (
        f"🦁 *¡ALERTA DIAMANTE DETECTADA!* 🦁\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏆 *Evento:* {matchup}\n"
        f"📈 *Argus Score:* {score}/100 {bar}\n"
        f"💰 *Momio Recomendado:* {odds}\n"
        f"🛡️ *Stake Sugerido:* {stake_pct}%\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 *Argumento IA:* {reasoning}\n\n"
        f"🚀 _Análisis verificado por el Oráculo Argus v18.0_"
    )
    
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [[
                {"text": "📲 IR A LA APUESTA", "url": deep_link}
            ]]
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error en Alerta Premium: {e}")
        return False

def send_daily_summary(wins, losses, units):
    """
    📊 RESUMEN DE RENDIMIENTO DIARIO
    Publica el cuadro de honor de la jornada.
    """
    emoji = "🔥" if units > 0 else "❄️"
    message = (
        f"🌓 *RESUMEN DE LA JORNADA* 🌓\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Ganadas hoy: {wins}\n"
        f"❌ Perdidas hoy: {losses}\n"
        f"💰 Unidades: *{units:+.2f}* {emoji}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📍 _Total transparencia. Auditoría disponible._"
    )
    return send_Argus_alert(message)

class TelegramGhost:
    """
    Simulación del Bot 'Ghost' para comandos remotos.
    En una implementación real, esto usaría la librería python-telegram-bot
    con un Updater o Webhook.
    """
    def __init__(self, persistence_module, db_module):
        self.persistence = persistence_module
        self.database = db_module
        self._stop_event = threading.Event()

    def start_polling(self):
        """Inicia el bot en un hilo separado (Simulado)."""
        thread = threading.Thread(target=self._run, daemon=True)
        thread.start()

    def _run(self):
        print("Robot Ghost: Iniciando escucha de comandos...")
        while not self._stop_event.is_set():
            # Aquí iría el polling real de Telegram
            time.sleep(30)

    def handle_command(self, command, args):
        """
        Simulador de procesamiento de comandos.
        """
        if command == "/status":
            data = self.persistence.load_bankroll()
            return f"💰 *Status Real*: ${data['current_bankroll']}\n📈 *Winrate*: {len(data['streak'])} apuestas en racha."
            
        elif command == "/live":
             # Mock de resultados en vivo
             return "🎾 Berrettini 6-4, 3-2 (Live)\n🚨 Alerta: Línea movida a -180."
             
        elif command == "/record":
            # Formato: /record [monto] [resultado]
            if len(args) < 2: return "Uso: /record [monto] [WIN/LOSS]"
            
            # Anti-Tilt Móvil
            data = self.persistence.load_bankroll()
            streak = data['streak']
            if len(streak) >= 2 and streak[0] == "L" and streak[1] == "L":
                return "🚫 *MODO DISCIPLINA ACTIVADO*. Has perdido 2 seguidas. No puedes registrar más por ahora. Ve a tomar un café. ☕"
            
            # Registro (Simplificado)
            amount = float(args[0])
            res = args[1].upper()
            # self.database.log_bet(...)
            return f"✅ Apuesta de ${amount} registrada como {res} desde el móvil."

    def stop(self):
        self._stop_event.set()
