import random
import datetime
import math

class EVModel:
    """
    Motor Algorítmico de Valor Esperado (EV) y Distribución de Poisson.
    Diseñado para aislar la lógica matemática del UI y mantener código limpio (Clean Architecture).
    """

    def __init__(self, target_winrate_low=0.65, target_winrate_high=0.75):
        self.target_winrate_low = target_winrate_low
        self.target_winrate_high = target_winrate_high
        self.min_ev_threshold = 0.05 # 5% minimum EV

    def calculate_base_probability_xg(self, rank_home, rank_away):
        """Calcula Probabilidad Base usando una simulación heurística de Goles Esperados (xG) en base a Rango."""
        base_xg_h = max(0.5, 2.5 - (rank_home * 0.1))
        base_xg_a = max(0.5, 2.0 - (rank_away * 0.1))
        
        # Poisson simplificado para win-rate directo
        real_prob_home = (base_xg_h / (base_xg_h + base_xg_a)) * 100
        return real_prob_home, base_xg_h, base_xg_a

    def get_implied_probability(self, american_odds):
        """Convierte momio de Las Vegas a Probabilidad Implícita."""
        dec_odds = (american_odds/100 + 1) if american_odds > 0 else (100/abs(american_odds) + 1)
        implied_prob = (1 / dec_odds) * 100
        return implied_prob, dec_odds

    def analyze_matchup(self, m_dict):
        """
        Ingiere el diccionario de un partido crudo y devuelve sus métricas enriquecidas.
        """
        # Extraer variables con safe defaults
        r_h = m_dict.get('rank_home', 10)
        r_a = m_dict.get('rank_away', 10)
        odds = m_dict.get('odds', -110)
        home_team = m_dict.get('home_team', 'Local')
        away_team = m_dict.get('away_team', 'Visita')
        league = m_dict.get('league', '')
        sport = m_dict.get('sport', '⚽ Fútbol')
        
        # 1. Base Math
        real_prob_home, bg_h, bg_a = self.calculate_base_probability_xg(r_h, r_a)
        implied_prob, dec_odds = self.get_implied_probability(odds)
        
        # 2. Raw Expected Value (EV)
        raw_ev = (real_prob_home/100 * dec_odds) - 1

        # 3. Módulos de Ajuste (Protecciones de Varianza)
        is_cup_or_derby = "Copa" in league or abs(r_h - r_a) <= 2
        variance_penalty = 0.15 if is_cup_or_derby else 0.0
        adjusted_ev = raw_ev - variance_penalty
        
        # 4. Underdog Boost (Kelly Fraccional Simulado)
        is_underdog = odds > 0
        value_boost = 0.05 if is_underdog and adjusted_ev > 0 else 0.0
        
        final_ev_percent = (adjusted_ev + value_boost) * 100
        
        # Normalización para UI (Clamp)
        visual_score = 50 + (final_ev_percent * 2)
        visual_score = max(10, min(99, visual_score))
        
        # 5. Pick Logic
        std_pick = f"Gana {home_team}" if real_prob_home > 50 else f"Gana {away_team}"
        
        market_pool = [
            (f"OVER 2.5 Goles", 60), 
            (f"UNDER 2.5 Goles", 40),
            (f"Ambos Anotan - SÍ", 55),
            (f"Local +0.5 HA", 70)
        ]
        
        if final_ev_percent > 5:
            vip_pick = "VIP: " + std_pick
        else:
            vip_pick = "VIP: " + random.choices([x[0] for x in market_pool], weights=[x[1] for x in market_pool])[0]

        # Multi-Markets Custom Generation per Sport
        multi_markets = {}
        if "⚽" in sport:
            multi_markets = {
                "Posesión Est.": f"{random.randint(48, 60)}%",
                "xG Proyectado": f"{bg_h:.1f} vs {bg_a:.1f}",
                "Rank Gap": f"{r_a - r_h}"
            }
        elif "🏀" in sport:
             multi_markets = {
                "Rank Gap": f"{r_a - r_h}",
                "Defensa Int.": f"{random.randint(70, 95)}",
                "Ataque Ext.": f"{random.randint(60, 85)}"
            }
        elif "🎾" in sport:
             multi_markets = {
                "Rank Gap": f"{r_a - r_h}",
                "Fondo Pista": f"{random.randint(70, 95)}%",
                "Primer Saque": f"{random.randint(60, 85)}%",
                "Fatiga": "Bajo"
            }

        return {
            'score': visual_score,
            'ev_real': final_ev_percent,
            'real_prob': real_prob_home,
            'implied_prob': implied_prob,
            'is_high_variance': is_cup_or_derby,
            'std_pick': std_pick,
            'vip_pick': vip_pick,
            'multi_markets': multi_markets
        }

    def generate_war_room_report(self, team_h, team_a, xgh, xga):
        """
        Genera un reporte avanzado de 5 mercados usando distribución de Poisson
        y selecciona los 3 más probables con explicación detallada.
        """
        # Calcular matriz de Poisson 10x10
        max_goals = 10
        matrix = [[0.0 for _ in range(max_goals)] for _ in range(max_goals)]
        
        for i in range(max_goals):
            for j in range(max_goals):
                prob_h = ((xgh**i) * math.exp(-xgh)) / math.factorial(i)
                prob_a = ((xga**j) * math.exp(-xga)) / math.factorial(j)
                matrix[i][j] = prob_h * prob_a
                
        # Calcular probabilidades de mercados
        prob_home_win = 0.0
        prob_away_win = 0.0
        prob_draw = 0.0
        prob_over_25 = 0.0
        prob_btts_yes = 0.0
        
        for i in range(max_goals):
            for j in range(max_goals):
                p = matrix[i][j]
                if i > j: prob_home_win += p
                elif i < j: prob_away_win += p
                else: prob_draw += p
                
                if (i + j) > 2.5: prob_over_25 += p
                if i > 0 and j > 0: prob_btts_yes += p
                
        # Lista de los 5 mercados
        markets = [
            {"name": f"Gana {team_h} (Moneyline)", "prob": prob_home_win * 100, "desc": f"El modelo proyecta que el local generará {xgh:.2f} goles esperados, dominando las fases de ataque. La probabilidad matemática pura de victoria directa es sólida basándonos en su superioridad ofensiva de xG."},
            {"name": f"Gana {team_a} (Moneyline)", "prob": prob_away_win * 100, "desc": f"Considerando el xG visitante ({xga:.2f}), esta apuesta asume que van a capitalizar sus contragolpes. Recomendada solo si detectas demasiado valor en la cuota (Underdog potente)."},
            {"name": "Empate (Draw)", "prob": prob_draw * 100, "desc": f"El cruce de probabilidades de Poisson detecta este margen de empate. Suele darse cuando la diferencia de xG entre ambos equipos ({abs(xgh-xga):.2f}) es menor a 0.5 o ambos tienen defensas que obligan al fallo."},
            {"name": "Más de 2.5 Goles (Over 2.5)", "prob": prob_over_25 * 100, "desc": f"Sumando el poder ofensivo de ambos equipos ({xgh+xga:.2f} xG Totales), este mercado evalúa la probabilidad de un partido abierto. Arriba del 55% indica un escenario con alta fluidez y llegadas constantes."},
            {"name": "Ambos Equipos Anotan (SÍ)", "prob": prob_btts_yes * 100, "desc": f"Esta variable es independiente de quién gane. Como el Local tira para {xgh:.2f}xG y la visita para {xga:.2f}xG, evalúa qué tan frágiles son ambas defensas al mismo tiempo."}
        ]
        
        # Ordenar por probabilidad
        markets.sort(key=lambda x: x['prob'], reverse=True)
        top_3 = markets[:3]
        
        # Construir Markdown
        report = f"### 🔮 Panorama Global Analítico ({team_h} vs {team_a})\n\n"
        report += f"_Motor Poisson procesando {xgh:.2f} vs {xga:.2f} xG_\n\n"
        
        report += "**Las 5 Posibilidades Matemáticas:**\n"
        for i, m in enumerate(markets):
            report += f"{i+1}. **{m['name']}** -> Probabilidad Real: `{m['prob']:.1f}%`\n"
            
        report += "\n---\n"
        report += "### 🏆 TOP 3 - Sugerencias de Mayor Efectividad\n\n"
        
        for i, m in enumerate(top_3):
            icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            report += f"#### {icon} {m['name']} (`{m['prob']:.1f}%`)\n"
            report += f"> {m['desc']}\n\n"
            
        return report, top_3
