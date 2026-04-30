import pandas as pd
import os
import datetime
from .persistence import load_bankroll, update_bankroll_value

DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "bankroll_history.csv")

def init_db():
    """Inicializa la base de datos CSV si no existe."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=[
            "Date", "Sport", "Matchup", "Pick", "Odds", "Stake", "Result", "Profit", "Equity", "Type"
        ])
        df.to_csv(DB_FILE, index=False)

def log_bet(sport, matchup, pick, odds, stake, result="PENDING", bet_type="AI"):
    """Registra una nueva apuesta."""
    init_db()
    
    # Cargar estado actual
    df = pd.read_csv(DB_FILE)
    
    # Migración rápida si la columna Type no existe
    if "Type" not in df.columns:
        df["Type"] = "AI"

    current_data = load_bankroll()
    current_equity = current_data['current_bankroll']
    
    new_row = {
        "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Sport": sport,
        "Matchup": matchup,
        "Pick": pick,
        "Odds": odds,
        "Stake": stake,
        "Result": result, # PENDING, WIN, LOSS, PUSH
        "Profit": 0.0, # Se actualiza al cerrar
        "Equity": current_equity,
        "Type": bet_type # AI, Intuition, o HostOverride
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    return True

def get_bet_history():
    """Retorna el historial completo como DataFrame."""
    init_db()
    df = pd.read_csv(DB_FILE)
    # Migración: Si no tiene Type, lo agregamos como AI
    if not df.empty and "Type" not in df.columns:
        df["Type"] = "AI"
        df.to_csv(DB_FILE, index=False)
    return df

def save_bet_history(df):
    """Guarda el DataFrame modificado (para ediciones en bloque)."""
    df.to_csv(DB_FILE, index=False)

AUDIT_FILE = os.path.join(DATA_DIR, "audit_log.csv")

def log_audit(matchup, odds, score):
    """Registra cada pick detectado por El Hunter para auditoría."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    if not os.path.exists(AUDIT_FILE):
        df = pd.DataFrame(columns=["Timestamp", "Matchup", "Odds", "Score"])
        df.to_csv(AUDIT_FILE, index=False)
        
    new_entry = {
        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Matchup": matchup,
        "Odds": odds,
        "Score": score
    }
    
    df = pd.read_csv(AUDIT_FILE)
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(AUDIT_FILE, index=False)

def update_pending_bet(index, new_result):
    """
    Actualiza el resultado de una apuesta y ajusta el Bankroll.
    Retorna el nuevo Bankroll.
    """
    df = pd.read_csv(DB_FILE)
    row = df.iloc[index]
    
    if row['Result'] != "PENDING" and row['Result'] != "OPEN":
        return None # Ya estaba cerrada
        
    stake = float(row['Stake'])
    odds = float(row['Odds'])
    
    profit = 0.0
    
    if new_result == "WIN":
        if odds > 0:
            profit = stake * (odds / 100)
        else:
            profit = stake * (100 / abs(odds))
    elif new_result == "LOSS":
        profit = -stake
    elif new_result == "PUSH":
        profit = 0.0
    
    # Actualizar CSV
    df.at[index, 'Result'] = new_result
    df.at[index, 'Profit'] = profit
    
    # Actualizar Equity en el registro (Snapshot del momento de cierre)
    # Esto es complejo retrospectivamente, asi que simplemente trackeamos el bankroll actual
    # y lo asignamos como el "Equity Resultante" de esa transacción.
    
    # Cargar Bankroll actual
    bk_data = load_bankroll()
    current_bk = bk_data['current_bankroll']
    
    # Logica de Flujo de Caja:
    # Asumimos que al registrar PENDING, el usuario RESTÓ el stake manualmente o el sistema lo hizo.
    # Si el sistema lo hizo, entonces:
    # WIN: Retorna Stake + Profit
    # LOSS: Retorna 0 (Stake ya se fue)
    # PUSH: Retorna Stake
    
    # SIMPLIFICACIÓN PROYECTO:
    # Vamos a asumir que el usuario gestiona su bankroll con el input manual O con esto.
    # Para ser consistentes:
    # WIN: Sumamos Stake + Profit al bankroll actual.
    # LOSS: No hacemos nada (asumiendo que el dinero ya "salió" o se ajusta con el resultado). 
    # ESPERA: Si restamos al inicio, en LOSS no sumamos nada. En WIN sumamos Todo.
    # Si NO restamos al inicio (Pending es virtual), en LOSS restamos Stake, en WIN sumamos Profit.
    
    # ELEGIMOS: Pending es VIRTUAL. El dinero no sale hasta que se cierra (o se marca loss).
    # WIN: Bankroll += Profit
    # LOSS: Bankroll -= Stake
    
    new_bk = current_bk
    if new_result == "WIN":
        new_bk += profit
    elif new_result == "LOSS":
        new_bk -= stake # El profit ya es negativo en el CSV, pero aqui operamos bankroll
       
    update_bankroll_value(new_bk)
    
    # Guardar nuevo equity en el registro para la curva
    df.at[index, 'Equity'] = new_bk
    df.to_csv(DB_FILE, index=False)
    
    return new_bk
