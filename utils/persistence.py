import json
import os
import time

DATA_DIR = "data"
BANKROLL_FILE = os.path.join(DATA_DIR, "bankroll.json")

def init_data():
    """Inicializa la carpeta de datos si no existe."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_bankroll():
    """Carga el bankroll."""
    init_data()
    # Default ajustado a Real Bankroll solicitado
    default_data = {
        "initial_capital": 69.00,
        "current_bankroll": 100.00,
        "streak": [], 
        "last_loss_timestamp": 0,
        "history": []
    }
    
    if not os.path.exists(BANKROLL_FILE):
        save_bankroll(default_data)
        return default_data
    
    try:
        with open(BANKROLL_FILE, 'r') as f:
            data = json.load(f)
            # Migración: asegurar que existe initial_capital
            if "initial_capital" not in data: 
                data["initial_capital"] = 69.00
            # Migración: timestamp
            if "last_loss_timestamp" not in data: 
                data["last_loss_timestamp"] = 0
            if "history" not in data: 
                data["history"] = []
            return data
    except:
        return default_data

def save_bankroll(data):
    """Guarda el estado actual."""
    init_data()
    with open(BANKROLL_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def update_streak(result: str):
    """Agrega resultado a racha."""
    data = load_bankroll()
    data['streak'].insert(0, result)
    if len(data['streak']) > 5:
        data['streak'] = data['streak'][:5]
    if result == "L":
        data['last_loss_timestamp'] = time.time()
    save_bankroll(data)

def update_bankroll_value(new_amount: float):
    """Actualiza solo el valor monetario."""
    data = load_bankroll()
    data['current_bankroll'] = new_amount
    save_bankroll(data)

def save_pick_to_history(pick_data):
    """Guarda el pick completo."""
    data = load_bankroll()
    pick_data['timestamp'] = time.strftime("%Y-%m-%d %H:%M")
    data['history'].insert(0, pick_data)
    if len(data['history']) > 50:
        data['history'] = data['history'][:50]
    save_bankroll(data)

def reset_data():
    """Resetea a valores REALES (Challenge Reset)."""
    default_data = {
        "initial_capital": 69.00,
        "current_bankroll": 100.00, # Capital Ajustado
        "streak": [],
        "last_loss_timestamp": 0,
        "history": []
    }
    save_bankroll(default_data)
    return default_data

def check_tilt_mode():
    """Check Tilt."""
    data = load_bankroll()
    streak = data['streak']
    last_loss = data['last_loss_timestamp']
    if len(streak) >= 2 and streak[0] == "L" and streak[1] == "L":
        if (time.time() - last_loss) < 3600:
            return True, int(3600 - (time.time() - last_loss))
    return False, 0
