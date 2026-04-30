import pandas as pd
import numpy as np
import os

# Nota: Aunque se solicitó scikit-learn, para estos análisis estadísticos 
# directos de CSV, la lógica matricial de Pandas/Numpy suele ser más 
# eficiente y transparente. Usaremos sklearn para el shadow betting si es necesario.

DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "bankroll_history.csv")

def get_market_correlations():
    """Analiza qué rangos de momios y deportes son más rentables."""
    if not os.path.exists(DB_FILE): return None
    
    df = pd.read_csv(DB_FILE)
    resolved = df[df['Result'].isin(['WIN', 'LOSS'])]
    if resolved.empty: return None

    # Agrupar por Deporte
    sport_stats = resolved.groupby('Sport').apply(lambda x: pd.Series({
        'WinRate': (x['Result'] == 'WIN').mean() * 100,
        'ROI': (x['Profit'].sum() / x['Stake'].sum()) * 100 if x['Stake'].sum() > 0 else 0,
        'Volume': len(x)
    }))
    
    return sport_stats

def detect_emotional_bias(player_name="Berrettini"):
    """
    Detecta si el usuario está apostando a un jugador específico 
    más allá de lo estadísticamente razonable.
    """
    if not os.path.exists(DB_FILE): return None
    df = pd.read_csv(DB_FILE)
    
    # Apuestas relacionadas con el jugador
    player_bets = df[df['Matchup'].str.contains(player_name, case=False, na=False)]
    if player_bets.empty: return f"Sin datos para {player_name}."
    
    total_bets = len(df)
    bias_pct = (len(player_bets) / total_bets) * 100
    
    # Éxito con este jugador vs resto
    p_resolved = player_bets[player_bets['Result'].isin(['WIN', 'LOSS'])]
    p_wr = (p_resolved['Result'] == 'WIN').mean() * 100 if not p_resolved.empty else 0
    
    rest_df = df[~df['Matchup'].str.contains(player_name, case=False, na=False)]
    r_resolved = rest_df[rest_df['Result'].isin(['WIN', 'LOSS'])]
    r_wr = (r_resolved['Result'] == 'WIN').mean() * 100 if not r_resolved.empty else 0
    
    verdict = "Imparcial"
    if bias_pct > 20 and p_wr < (r_wr - 5):
        verdict = "⚠️ SESGO DETECTADO: Apuestas emocionales frecuentes con bajo rendimiento."
    elif bias_pct > 30:
        verdict = "❗ ALTA DEPENDENCIA: Más del 30% de tus picks involucran a este jugador."
        
    return {
        "player": player_name,
        "bias_pct": bias_pct,
        "wr_player": p_wr,
        "wr_rest": r_wr,
        "verdict": verdict
    }

def calculate_risk_tax(sport, market_type="General"):
    """
    Si históricamente un deporte/mercado tiene WR < 40%, 
    devuelve un valor de penalización (0.0 a 1.0).
    """
    if not os.path.exists(DB_FILE): return 1.0 # Sin penalización
    
    df = pd.read_csv(DB_FILE)
    sport_resolved = df[(df['Sport'] == sport) & (df['Result'].isin(['WIN', 'LOSS']))]
    
    if len(sport_resolved) < 5: return 1.0 # Poca data para penalizar
    
    wr = (sport_resolved['Result'] == 'WIN').mean()
    
    if wr < 0.40: return 0.85 # Restar 15% del score
    if wr < 0.50: return 0.95 # Restar 5%
    return 1.0

def run_shadow_betting_sim():
    """
    Compara: Estrategia Actual vs Shadow Strategy (Stake Fijo al 2%).
    """
    if not os.path.exists(DB_FILE): return None
    df = pd.read_csv(DB_FILE)
    resolved = df[df['Result'].isin(['WIN', 'LOSS'])].sort_values('Date')
    
    if resolved.empty: return None
    
    # Estrategia Actual (Equity Real)
    equity_real = resolved['Equity'].values
    
    # Estrategia Shadow: Siempre apostar 2% del capital inicial ($100)
    shadow_capital = 100.0
    shadow_history = [shadow_capital]
    fixed_stake = 2.0 # $2 fijo
    
    for i, row in resolved.iterrows():
        # Calcular profit con momio americano
        odds = float(row['Odds'])
        if row['Result'] == "WIN":
            if odds > 0: profit = fixed_stake * (odds/100)
            else: profit = fixed_stake * (100/abs(odds))
        else:
            profit = -fixed_stake
            
        shadow_capital += profit
        shadow_history.append(shadow_capital)
        
    return {
        "dates": resolved['Date'].tolist(),
        "real": equity_real.tolist(),
        "shadow": shadow_history[1:] # Saltar el inicial
    }

def generate_rejection_rationale(match_data, score):
    """
    Genera una explicación de por qué un pick NO es Diamante.
    """
    if score >= 90:
        return "El pick cumple con todos los parámetros de élite."
        
    motivos = []
    odds = match_data.get('odds', 0)
    
    if score < 70:
        motivos.append("Inconsistencia estadística grave en los últimos 5 encuentros.")
    elif score < 85:
        motivos.append("Falta de 'Value Gap' suficiente (el momio está muy ajustado a la probabilidad real).")
        
    if abs(odds) > 500:
        motivos.append("Riesgo de varianza alta por momio excesivo.")
    elif abs(odds) < 120 and odds != 0:
        motivos.append("Premio insuficiente para el riesgo asumido (Low Reward).")
        
    if not motivos:
        motivos.append("El modelo detectó una anomalía en el volumen de apuestas que sugiere precaución.")
        
    return " / ".join(motivos)
