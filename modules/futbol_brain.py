class FutbolBrain:
    def __init__(self):
        self.name = "FUTBOL BRAIN"
        self.sport = "Futbol"

    def analizar_partido(self,
                         equipo_local: str,
                         equipo_visitante: str,
                         es_local: bool,
                         goles_ultimos_3: bool,
                         promedio_goles_recibidos: float,
                         invicto_h2h_2_anos: bool,
                         posicion_tabla: int,
                         ganados_ultimos_5: int,
                         cuota_americana: int,
                         # --- NUEVOS PARÁMETROS SHARK MODE ---
                         es_eliminatoria: bool = False, # Champions/Playoffs
                         porterias_cero_5: int = 0, # Clean Sheets últimos 5
                         experiencia_dt: int = 5 # 1-10 (10 = Ancelotti/Guardiola)
                         ):
        """
        Analiza un partido de fútbol con Lógica de Blindaje para Playoffs.
        """
        
        score = 0
        reasons = []
        
        # --- 1. FACTOR LOCALÍA ---
        if es_local:
            score += 10
            reasons.append("Factor Cancha (Localía): +10 pts")

        # --- 2. RACHA DE GOLES (AJUSTE PLAYOFFS) ---
        if goles_ultimos_3:
            # En eliminatorias, los goles valen menos si la defensa es clave
            if es_eliminatoria:
                score += 5
                reasons.append("Ataque Constante (Ajustado x Playoff): +5 pts")
            else:
                score += 10
                reasons.append("Ataque Constante: +10 pts")

        # --- 3. MURO DEFENSIVO & PORTERÍAS A CERO ---
        # Prioridad en Playoffs: Clean Sheets > Promedio Goles
        if es_eliminatoria:
            if porterias_cero_5 >= 3:
                score += 25
                reasons.append(f"🛡️ Muralla Playoff ({porterias_cero_5} Clean Sheets): +25 pts")
            elif promedio_goles_recibidos < 0.8:
                score += 15
                reasons.append("Defensa Sólida: +15 pts")
        else:
            if promedio_goles_recibidos < 0.7:
                score += 20
                reasons.append(f"🛡️ Super Defensa (<0.7): +20 pts")
            elif promedio_goles_recibidos < 1.0:
                score += 15

        # --- 4. EXPERIENCIA DT (CLAVE EN CHAMPIONS) ---
        if es_eliminatoria:
            if experiencia_dt >= 8:
                score += 15
                reasons.append(f"🧠 Factor DT Experto (Nivel {experiencia_dt}): +15 pts")
            elif experiencia_dt <= 4:
                score -= 10
                reasons.append("⚠️ DT Novato en Playoff: -10 pts")

        # --- 5. H2H & RACHA ---
        if invicto_h2h_2_anos: score += 10
        if ganados_ultimos_5 >= 4: score += 15
        if posicion_tabla <= 3: score += 10

        # --- LÓGICA DE RECOMENDACIÓN ---
        recomendacion = "NO BET"
        color = "#FAFAFA"
        tipo_apuesta = "Resultado Final"

        # Ajuste de BTTS (Ambos Anotan) para Playoffs
        # Si es eliminatoria, castigamos la predicción de goles si no hay stats ofensivas brutales
        riesgo_btts = False
        if es_eliminatoria and (promedio_goles_recibidos < 1.0 or porterias_cero_5 >= 2):
            riesgo_btts = True # Riesgo de 0-0 o 1-0 táctico

        if score >= 85:
            recomendacion = "🛡️ APUESTA DE ALTA CONFIANZA"
            color = "#39FF14"
            if riesgo_btts:
                reasons.append("⚠️ ALERTA: Partido Táctico/Cerrado (Posible Under)")
        elif score >= 70:
            recomendacion = "💎 GANA DIRECTO"
            color = "#00FF00"
        elif score >= 60:
            recomendacion = "🥇 DOBLE OPORTUNIDAD"
            color = "#FFD700"
        elif score < 50:
            recomendacion = "❌ NO HAY VALOR AQUÍ"
            color = "#FF4444" 
            score = max(score, 20)

        return {
            "sport": self.sport,
            "matchup": f"{equipo_local} vs {equipo_visitante}",
            "pick": recomendacion,
            "score": score,
            "reasons": reasons,
            "recommendation": recomendacion,
            "color": color
        }
