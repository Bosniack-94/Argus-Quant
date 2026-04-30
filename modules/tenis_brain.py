class TenisBrain:
    def __init__(self):
        self.name = "TENIS BRAIN v2.1"
        self.sport = "Tennis"

    def analizar_partido(self,
                         jugador_A: str, ranking_A: int,
                         jugador_B: str, ranking_B: int,
                         cuota_A_americana: int, cuota_B_americana: int, # Dummy
                         h2h_diff: int,
                         racha_A: int,
                         racha_B: int,
                         superficie_favorita: bool = True 
                         ):
        """
        Analiza Tenis con lógica 'BANKER' y 'Dangerous Underdog'.
        """
        
        score = 0
        reasons = []
        is_banker = False

        # --- 0. DETECCIÓN DE BANKER (MOMIO PESADO) ---
        if cuota_A_americana <= -300:
            score += 40 
            is_banker = True
            reasons.append(f"🚀 BANKER DETECTADO (Cuota {cuota_A_americana}): +40 pts")
        elif -150 <= cuota_A_americana <= 120:
             score += 10
             reasons.append("Cuota de Valor: +10 pts")

        # --- RANKING & DANGEROUS UNDERDOG ---
        rank_diff = ranking_B - ranking_A
        
        # Si el rival es bueno (Top 50) y el favorito es Top 20, cuidado.
        # Dangerous Underdog: Rival Top 50, H2H negativo o parejo
        cardiaco = False
        if ranking_B <= 50 and h2h_diff <= 0:
            score -= 15
            cardiaco = True
            reasons.append(f"⚠️ RIVAL PELIGROSO (Top 50 + H2H): -15 pts")
        
        if rank_diff > 100:
            score += 15
            reasons.append("Abismo en Ranking (>100): +15 pts")
        elif rank_diff > 50:
            score += 10

        # --- SUPERFICIE ---
        if superficie_favorita:
            score += 15
            reasons.append("Especialista en Superficie: +15 pts")

        # --- RACHA ---
        if racha_A >= 4: score += 10
        if racha_B <= 1: score += 5

        # --- RECOMENDACIÓN & STAKE ---
        recomendacion = "NO BET"
        color = "#FAFAFA"
        stake = "0%"

        if is_banker and score >= 80:
            recomendacion = "🚀 BANKER (BASE DE PARLAY)"
            color = "#00FFFF" # Cyan Eléctrico
            stake = "5-10% (High Confidence)"
            score = min(score, 99)
        elif score >= 85: 
             recomendacion = "💎 DIAMANTE (GANA DIRECTO)"
             color = "#39FF14"
             stake = "3-5%"
        elif score >= 60:
             recomendacion = "🥇 ORO"
             color = "#FFD700"
             stake = "2%"
        elif score < 50:
             recomendacion = "❌ NO HAY VALOR"
             color = "#FF4444"
             stake = "0%"

        # Si es peligroso, bajar stake
        if cardiaco and stake != "0%":
            stake = "1% (Risk)"
            recomendacion += " (CON CUIDADO)"

        return {
            "sport": self.sport,
            "matchup": f"{jugador_A} vs {jugador_B}",
            "pick": recomendacion,
            "score": score,
            "reasons": reasons,
            "recommendation": recomendacion,
            "color": color,
            "stake_suggestion": stake
        }
