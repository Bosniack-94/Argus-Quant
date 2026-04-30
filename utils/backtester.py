import pandas as pd
import numpy as np

class BacktestEngine:
    """
    Motor de Backtesting profesional para marketing y validación.
    Permite cargar datos históricos de ligas y simular la 'Selección Diamante'.
    """
    def __init__(self, initial_capital=100.0):
        self.initial_capital = initial_capital
        
    def run_simulation(self, df):
        """
        Ejecuta la simulación sobre un DataFrame con columnas: 
        Matchup, Odds, Result (W/L), Score (AI).
        """
        # Filtro Selección Diamante (Score > 90)
        diamantes = df[df['Score'] >= 90].copy()
        
        if diamantes.empty:
            return {
                "roi": 0, "winrate": 0, "drawdown": 0, "total_bets": 0, "final_equity": self.initial_capital
            }
            
        capital = self.initial_capital
        history = [capital]
        wins = 0
        
        # Simulación de Stake Fijo al 5% para backtesting estándar
        stake_pct = 0.05
        
        for _, row in diamantes.iterrows():
            stake = capital * stake_pct
            odds = float(row['Odds'])
            
            if row['Result'] == 'W':
                if odds > 0: profit = stake * (odds / 100)
                else: profit = stake * (100 / abs(odds))
                wins += 1
            else:
                profit = -stake
                
            capital += profit
            history.append(capital)
            
        # Métricas
        winrate = (wins / len(diamantes)) * 100
        roi = ((capital - self.initial_capital) / self.initial_capital) * 100
        
        # Calcular Max Drawdown
        history_arr = np.array(history)
        peak = np.maximum.accumulate(history_arr)
        drawdown = (peak - history_arr) / peak
        max_drawdown = np.max(drawdown) * 100
        
        return {
            "roi": roi,
            "winrate": winrate,
            "max_drawdown": max_drawdown,
            "total_bets": len(diamantes),
            "final_equity": capital,
            "equity_curve": history
        }

    def generate_demo_data(self):
        """Genera 50 partidos ficticios para demostración de backtesting."""
        data = []
        for i in range(50):
            score = np.random.randint(70, 98)
            odds = np.random.choice([-150, -200, +120, -110])
            # Simular que Diamantes (>90) tienen 80% Winrate
            if score >= 90:
                res = 'W' if np.random.random() < 0.8 else 'L'
            else:
                res = 'W' if np.random.random() < 0.5 else 'L'
                
            data.append({
                "Date": f"2024-01-{i%30+1}",
                "Matchup": f"Equipo {i} vs Rival {i}",
                "Score": score,
                "Odds": odds,
                "Result": res
            })
        return pd.DataFrame(data)
