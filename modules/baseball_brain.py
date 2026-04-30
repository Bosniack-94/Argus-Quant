class BaseballBrain:
    def __init__(self):
        self.name = "BASEBALL BRAIN"
        self.sport = "Baseball"

    def analyze_game(self,
                     equipo: str, # Equipo analizado (se asume favorito)
                     rival: str,
                     pitcher_era: float, # ERA del abridor del equipo
                     rival_era: float,   # ERA del abridor rival
                     carreras_ultimos_10: float, # Promedio de carreras anotadas
                     ganados_ultimos_10: int, # Racha (0-10)
                     es_liga_bateo: bool = False, # True para LMB/NPB en estadios de bateo
                     cuota_americana: int = -150 # Para referencia
                     ):
        """
        Analiza un partido de Béisbol (MLB, NPB, LMB).
        
        Reglas de Puntuación:
        1. Duelo de Pitcheo: Si ERA A < 3.50 y ERA B > 5.00 (+25 pts).
        2. Poder de Bateo: SI gano > 5.5 carreras prom. en ultimos 10 (+10 pts).
        3. Racha: Si ganó 7 de ultimos 10 (+10 pts).
        4. Factor Bullpen/Estadio: Si es LMB/NPB y estadio bateador (+15 pts a OVER).
        """
        
        score = 0
        over_score = 0
        reasons = []

        # --- Base Score Inicial ---
        score = 50 

        # --- 1. DUELO DE PITCHEO (FACTOR ABRIDOR) ---
        if pitcher_era < 3.50 and rival_era > 5.00:
            score += 25
            reasons.append(f"Ventaja Masiva Pitcheo (ERA {pitcher_era} vs {rival_era}): +25 pts")
        elif pitcher_era < rival_era:
            score += 10
            reasons.append("Ventaja Pitcheo: +10 pts")
        
        # Analisis especifico para Totales basado en Pitchers
        if pitcher_era > 5.00 and rival_era > 5.00:
            over_score += 20
            reasons.append("Ambos Pitchers Malos (>5.00 ERA): Alerta OVER")
        elif pitcher_era < 3.00 and rival_era < 3.00:
            over_score -= 20 # Señal de Under
            reasons.append("Duelo de Ases (<3.00 ERA): Alerta UNDER")

        # --- 2. PODER DE BATEO ---
        if carreras_ultimos_10 > 5.5:
            score += 10
            over_score += 10
            reasons.append(f"Bateo Caliente ({carreras_ultimos_10} carreras/juego): +10 pts")

        # --- 3. RACHA ---
        if ganados_ultimos_10 >= 7:
            score += 10
            reasons.append("Racha Ganadora (7+ de 10): +10 pts")
        elif ganados_ultimos_10 <= 3:
            score -= 10
            reasons.append("Slump (Mala racha): -10 pts")

        # --- 4. FACTOR BULLPEN/ESTADIO (LMB/NPB) ---
        if es_liga_bateo:
            over_score += 15
            reasons.append("Liga/Estadio de Bateo: +15 pts al OVER")

        # --- LÓGICA DE RECOMENDACIÓN INTELIGENTE ---
        recomendacion = "NO BET"
        tipo_apuesta = "Moneyline"
        color = "#FF0000" # Rojo es riesgo/no bet

        # Prioridad 1: Duelo de Ases (F5 UNDER)
        if pitcher_era < 3.00 and rival_era < 3.00:
            recomendacion = "🛡️ BAJAS 1ra MITAD (F5 UNDER)"
            tipo_apuesta = "F5 Total < 4.5"
            color = "#C0C0C0" # Plata
            score = 70 # Ajuste visual

        # Prioridad 2: Duelo de Pitchers Malos (OVER)
        elif (over_score >= 20) or (pitcher_era > 5.00 and rival_era > 5.00):
            recomendacion = "🔥 ALTAS (OVER)"
            tipo_apuesta = "Total > 8.5"
            color = "#00FFFF" # Cyan
            score = 75

        # Prioridad 3: Run Line (Paliza probable)
        elif score > 85:
            recomendacion = "💎 RUN LINE -1.5"
            tipo_apuesta = "Run Line -1.5"
            color = "#00FF00" # Verde Fuerte

        # Prioridad 4: Moneyline (Ganar normal)
        elif score >= 60:
            recomendacion = "🥇 GANA (MONEYLINE)"
            tipo_apuesta = "Moneyline"
            color = "#FFD700" # Dorado
            
        else:
            recomendacion = "🚫 NO BET (RIESGO)"
            tipo_apuesta = "TBD"
            color = "#FF4444"

        return {
            "sport": self.sport,
            "matchup": f"{equipo} vs {rival}",
            "pick": f"{recomendacion}",
            "score": score,
            "reasons": reasons,
            "recommendation": recomendacion,
            "bet_type": tipo_apuesta,
            "color": color
        }

# Pruebas rápidas
if __name__ == "__main__":
    brain = BaseballBrain()
    # Caso: Yankees (Ace) vs Rockies (Malo), Estadio Coors Field (Bateo)
    res = brain.analyze_game(
        equipo="Yankees", rival="Rockies",
        pitcher_era=2.90,
        rival_era=6.10,
        carreras_ultimos_10=6.2,
        ganados_ultimos_10=8,
        es_liga_bateo=True # Coors Field effect
    )
    print(res)
