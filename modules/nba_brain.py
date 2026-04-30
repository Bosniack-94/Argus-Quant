class NBABrain:
    def __init__(self):
        self.name = "NBA BRAIN"
        self.sport = "NBA"

    def analyze_game(self,
                     equipo: str, # Equipo analizado (se asume favorito o local)
                     rival: str,
                     es_local: bool,
                     dias_descanso: int, # 0 = Back-to-Back
                     promedio_puntos_equipo: float,
                     promedio_puntos_rival: float,
                     ganados_ultimos_5: int, # 0-5
                     linea_apuesta: float = 0.0 # Spread (ej. -5.5) o Total (220.5) opcional
                     ):
        """
        Analiza un partido de NBA enfocado en Cansancio y Ritmo (Pace).
        
        Reglas de Puntuación:
        1. Back-to-Back: Si jugó ayer (0 días descanso) -> -20 pts (Cansancio).
        2. Factor Cancha: Si es local -> +10 pts.
        3. Potencial Puntos (Pace): Si la suma de promedios > 230 -> +15 pts (Señal ALTAS).
        4. Racha: Si ganó >= 4 de últimos 5 -> +10 pts (Momentum).
        """
        
        score = 0
        over_score = 0 # Puntaje específico para totales (Altas/Bajas)
        reasons = []

        # --- Base Score Inicial ---
        score = 50 # Empezamos neutro en NBA

        # --- 1. BACK-TO-BACK (CANSANCIO) ---
        if dias_descanso == 0:
            score -= 20
            over_score -= 10 # Cansancio suele bajar el ritmo
            reasons.append("⚠️ Back-to-Back (Cansancio): -20 pts")
        elif dias_descanso >= 2:
            score += 5
            reasons.append("Descanso óptimo (+2 días): +5 pts")

        # --- 2. FACTOR CANCHA ---
        if es_local:
            score += 10
            reasons.append("Juega en Casa (Local): +10 pts")

        # --- 3. POTENCIAL DE PUNTOS (PACE / ALTAS) ---
        total_proyectado = promedio_puntos_equipo + promedio_puntos_rival
        if total_proyectado > 230:
            score += 15 # Equipos ofensivos suelen ganar
            over_score += 25 # Señal fuerte de Over
            reasons.append(f"Ritmo Alto (Proy. {total_proyectado} pts): +15 pts / Potencial OVER")
        elif total_proyectado < 210:
            over_score -= 20 # Señal de Under
            reasons.append(f"Ritmo Lente/Defensivo: Posible UNDER")

        # --- 4. RACHA (MOMENTUM) ---
        if ganados_ultimos_5 >= 4:
            score += 10
            reasons.append("Racha Ganadora (4+ de 5): +10 pts")
        elif ganados_ultimos_5 <= 1:
            score -= 10
            reasons.append("Mala Racha (1 o menos): -10 pts")

        # --- LÓGICA DE RECOMENDACIÓN INTELIGENTE ---
        recomendacion = "NO BET"
        tipo_apuesta = "Moneyline"
        color = "#FF0000" # Rojo

        # Prioridad 1: Altos Puntos (Over)
        # Si el score de over es muy alto (pace > 230 + descanso ok)
        if over_score >= 15 and total_proyectado > 230:
            recomendacion = "🔥 ALTAS (OVER)"
            tipo_apuesta = f"Total > {int(total_proyectado - 5)}" # Margen de seguridad
            color = "#00FFFF" # Cyan
            score = 80 # Ajuste visual para que destaque
            
        # Prioridad 2: Spread / Handicap (Favorito Sólido)
        elif score > 85:
            spread_sugerido = -5.5 # Valor default lógico si es muy favorito
            recomendacion = f"💎 HANDICAP {spread_sugerido}"
            tipo_apuesta = "Spread / Hándicap"
            color = "#00FF00" # Verde Fuerte
            
        # Prioridad 3: Moneyline (Ganar normal)
        elif score >= 60:
            recomendacion = "🥇 GANA (MONEYLINE)"
            tipo_apuesta = "Moneyline"
            color = "#FFD700" # Dorado
            
        # Prioridad 4: Bajas / Under (Score bajo o Pace lento)
        elif score < 50:
            if total_proyectado < 210:
                recomendacion = "🛡️ BAJAS (UNDER)"
                tipo_apuesta = "Total < 210"
                color = "#C0C0C0" # Plata
                score = 60 # Ajuste para que no se vea tan rojo si es una recomendación válida
            else:
                recomendacion = "🚫 NO BET (RIESGO)"
                tipo_apuesta = "TBD"
                color = "#FF4444" # Rojo Riesgo

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
    brain = NBABrain()
    # Caso: Lakers (Local, Descansado) vs Warriors (Pace alto), ambos anotan mucho.
    res = brain.analyze_game(
        equipo="Lakers", rival="Warriors",
        es_local=True,
        dias_descanso=2,
        promedio_puntos_equipo=118,
        promedio_puntos_rival=115, # Suma 233 -> Over
        ganados_ultimos_5=4
    )
    print(res)
