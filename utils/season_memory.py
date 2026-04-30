import json
import os
import datetime
import streamlit as st

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seasonal_archive.json")

def ensure_db(initial_cap=10000):
    """Asegura que el archivo JSON exista y esté sembrado con datos para la demo."""
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))
    if not os.path.exists(DB_PATH):
        # Sembramos datos iniciales directamente para evitar que el ledger aparezca vacío
        mock_data = generate_mock_history("Mensual", initial_cap)
        with open(DB_PATH, 'w') as f:
            json.dump({"weeks": mock_data}, f, indent=4)

def archive_week(week_data):
    """
    Guarda el resumen de una semana.
    """
    ensure_db()
    with open(DB_PATH, 'r') as f:
        data = json.load(f)
    
    # Evitar duplicados
    data["weeks"] = [w for w in data["weeks"] if w["week_id"] != week_data["week_id"]]
    data["weeks"].append(week_data)
    
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=4)
    # Limpiar caché al actualizar


def get_historical_report(period="Mensual", initial_cap=10000):
    """
    Retorna datos agregados. Se priorizan los datos reales del JSON si existen.
    """
    ensure_db(initial_cap)
    with open(DB_PATH, 'r') as f:
        data = json.load(f)
        weeks = data.get("weeks", [])
        if weeks:
            # Auto-rotación semanal (comprobar si la última semana coincide con la real)
            current_year, current_wk, _ = datetime.datetime.now().isocalendar()
            current_week_str = f"{current_year}-W{current_wk:02d}"
            
            # Para evitar conflictos con los mocks que llegaban al W18, 
            # forzamos una semana nueva sólo si es string real esperado
            last_week_id = weeks[-1].get("week_id", "")
            if last_week_id != current_week_str:
                # Archivar la anterior y empezar una limpia real
                start_new_forensic_week(initial_cap, force_week_id=current_week_str)
                # Recargar después de rotar
                with open(DB_PATH, 'r') as f2:
                    data = json.load(f2)
                    weeks = data.get("weeks", [])
            
            # Filtrar según el periodo
            if period == "Semanal": return [weeks[-1]]
            if period == "Mensual": return weeks[-4:]
            if period == "Semestral": return weeks[-26:]
            return weeks
    
    # Fallback a mock si algo falla o está vacío
    return generate_mock_history(period, initial_cap)

def append_live_match_to_ledger(match_data, tier="BOTH"):
    """
    Agrega picks analizados en vivo al reporte histórico.
    Si tier="BOTH", agrega ambos picks como registros separados para auditoría granular.
    """
    ensure_db()
    try:
        with open(DB_PATH, 'r') as f:
            db_data = json.load(f)
        
        if not db_data.get("weeks"): return False
        last_week = db_data["weeks"][-1]
        if "matches" not in last_week: last_week["matches"] = []

        tiers_to_add = ["💵 Standard", "💎 Elite VIP"] if tier == "BOTH" else [tier]
        
        added_any = False
        for current_tier in tiers_to_add:
            is_std = "Standard" in current_tier
            pick_text = match_data.get("std_pick" if is_std else "elite_pick", "TBD")
            
            new_entry = {
                "teams": match_data["matchup"],
                "sport": match_data["sport"],
                "tier": current_tier, # Nueva llave para separación absoluta
                "pick": pick_text,
                "status": "PENDIENTE",
                "why": "Sincronizado desde Live Analysis"
            }
            
            # Evitar duplicados por matchup + tier
            if not any(m.get("teams") == new_entry["teams"] and m.get("tier") == new_entry["tier"] for m in last_week["matches"]):
                last_week["matches"].append(new_entry)
                added_any = True
            
        if added_any:
            with open(DB_PATH, 'w') as f:
                json.dump(db_data, f, indent=4)

        return True
    except Exception as e:
        print(f"Error appending to ledger: {e}")
        return False

def settle_match_result(match_teams, tier, result):
    """
    Liquida un pick específico (match + tier).
    tier: '💵 Standard' o '💎 Elite VIP'
    result: 'WIN', 'LOSS', 'PENDIENTE'
    """
    ensure_db()
    with open(DB_PATH, 'r') as f:
        db_data = json.load(f)
    
    if not db_data.get("weeks"): return False
    
    last_week = db_data["weeks"][-1]
    match_found = False
    for m in last_week.get("matches", []):
        if m.get("teams") == match_teams and m.get("tier") == tier:
            m["status"] = result
            match_found = True
            break
            
    if match_found:
        # Calcular PnL Real-Time
        wins = len([m for m in last_week.get("matches", []) if m.get("status") == "WIN"])
        losses = len([m for m in last_week.get("matches", []) if m.get("status") == "LOSS"])
        
        last_week["verdazos"] = wins
        last_week["erradas"] = losses
        
        unit_size = last_week.get("initial_balance", 10000) * 0.05
        profit_aprox = (wins * (unit_size * 0.90)) - (losses * unit_size)
        
        last_week["profit"] = profit_aprox
        last_week["ending_balance"] = last_week.get("initial_balance", 10000) + profit_aprox
        last_week["roi"] = (profit_aprox / last_week.get("initial_balance", 10000)) * 100 if last_week.get("initial_balance", 10000) > 0 else 0

        with open(DB_PATH, 'w') as f:
            json.dump(db_data, f, indent=4)
            
    return match_found

def update_match_pick(match_teams, tier, new_pick):
    """
    Actualiza el pronóstico (pick) de un partido pendiente.
    """
    ensure_db()
    with open(DB_PATH, 'r') as f:
        db_data = json.load(f)
    
    if not db_data.get("weeks"): return False
    
    last_week = db_data["weeks"][-1]
    match_found = False
    for m in last_week.get("matches", []):
        if m.get("teams") == match_teams and m.get("tier") == tier:
            m["pick"] = new_pick
            match_found = True
            break
            
    if match_found:
        with open(DB_PATH, 'w') as f:
            json.dump(db_data, f, indent=4)
            
    return match_found

def delete_match_from_ledger(match_teams, tier=None):
    """
    Elimina registros del ledger. Si tier es None, borra todos los picks de ese match.
    Si tier está presente, borra solo esa elección específica.
    """
    ensure_db()
    with open(DB_PATH, 'r') as f:
        db_data = json.load(f)
    
    if not db_data.get("weeks"): return False
    last_week = db_data["weeks"][-1]
    original_count = len(last_week.get("matches", []))
    
    if tier:
        last_week["matches"] = [m for m in last_week.get("matches", []) if not (m.get("teams") == match_teams and m.get("tier") == tier)]
    else:
        last_week["matches"] = [m for m in last_week.get("matches", []) if m.get("teams") != match_teams]
    
def clear_current_audit():
    """Limpia todos los partidos de la semana de auditoría actual."""
    ensure_db()
    with open(DB_PATH, 'r') as f:
        db_data = json.load(f)
    if not db_data.get("weeks"): return False
    
    db_data["weeks"][-1]["matches"] = []
    db_data["weeks"][-1]["verdazos"] = 0
    db_data["weeks"][-1]["erradas"] = 0
    db_data["weeks"][-1]["roi"] = 0.0
    db_data["weeks"][-1]["profit"] = 0.0
    
    with open(DB_PATH, 'w') as f:
        json.dump(db_data, f, indent=4)

    return True

def start_new_forensic_week(initial_cap=10000, force_week_id=None):
    """
    Archiva la semana actual y crea una nueva vacía para empezar auditoría limpia.
    """
    ensure_db(initial_cap)
    with open(DB_PATH, 'r') as f:
        db_data = json.load(f)
    
    # Liquidar la semana anterior calculando su PnL basado en las apuestas
    last_week = db_data["weeks"][-1]
    matches = last_week.get("matches", [])
    wins = len([m for m in matches if m.get("status") == "WIN"])
    losses = len([m for m in matches if m.get("status") == "LOSS"])
    
    last_week["verdazos"] = wins
    last_week["erradas"] = losses
    
    # Asumimos riesgo promedio de 5% de banca (1 unidad) para calcular PnL simple
    # Ganadas = +0.85 unidades (cuota -110), Perdidas = -1 unidad
    unit_size = last_week.get("initial_balance", initial_cap) * 0.05
    profit_aprox = (wins * (unit_size * 0.90)) - (losses * unit_size)
    last_week["profit"] = profit_aprox
    last_week["ending_balance"] = last_week["initial_balance"] + profit_aprox
    last_week["roi"] = (profit_aprox / last_week["initial_balance"]) * 100 if last_week["initial_balance"] > 0 else 0

    # Determinar el ID de la nueva semana
    if force_week_id:
        new_week_id = force_week_id
    else:
        last_week_id = last_week["week_id"]
        try:
            w_num = int(last_week_id.split("-W")[-1])
            new_week_id = f"2026-W{w_num + 1:02d}"
        except:
            current_year, current_week, _ = datetime.datetime.now().isocalendar()
            new_week_id = f"{current_year}-W{current_week:02d}"

    # El saldo inicial de la nueva semana es el saldo final de la anterior
    new_init_cap = last_week.get("ending_balance", initial_cap)
    
    new_week = {
        "week_id": new_week_id,
        "date_range": str(datetime.date.today()),
        "initial_balance": new_init_cap,
        "ending_balance": new_init_cap, # Empieza igual
        "verdazos": 0,
        "erradas": 0,
        "roi": 0.0,
        "profit": 0.0,
        "matches": [],
        "champion_sport": "Pendiente"
    }
    
    db_data["weeks"].append(new_week)
    with open(DB_PATH, 'w') as f:
        json.dump(db_data, f, indent=4)
        

        
    return new_week_id

def generate_mock_history(period, initial_seed_cap=10000):
    """Genera 12 semanas de historial forense con equipos reales y capital variable."""
    mock_data = []
    
    # Pool de equipos reales para mayor impacto visual
    teams_pool = [
        {"t": "América vs Chivas", "s": "⚽ Fútbol", "w": "Dominio absoluto en posesión y Rank Gap."},
        {"t": "Cruz Azul vs Pumas", "s": "⚽ Fútbol", "w": "Tendencia Under 2.5 confirmada por xG."},
        {"t": "Lakers vs Warriors", "s": "🏀 Basket", "w": "Ventaja en triples y ritmo de juego (Pace)."},
        {"t": "Alcaraz vs Djokovic", "s": "🎾 Tenis", "w": "Efectividad de primer servicio superior al 70%."},
        {"t": "Monterrey vs Tigres", "s": "⚽ Fútbol", "w": "Clásico regio con alta probabilidad de Empate/Local."},
        {"t": "Celtics vs 76ers", "s": "🏀 Basket", "w": "Defensa perimetral élite anula disparos externos."},
        {"t": "Nadal vs Sinner", "s": "🎾 Tenis", "w": "Resistencia física en sets largos favorece selección."},
        {"t": "Toluca vs Pachuca", "s": "⚽ Fútbol", "w": "Altitud de Toluca como factor determinante en Q2."},
        {"t": "Bucks vs Heat", "s": "🏀 Basket", "w": "Presencia en pintura (Giannis) rompe zona defensiva."},
        {"t": "Swiatek vs Sabalenka", "s": "🎾 Tenis", "w": "Consistencia desde fondo de pista."},
    ]
    
    for i in range(12):
        week_num = 7 + i 
        week_id = f"2026-W{week_num:02d}"
        
        # El capital inicial de esta semana es el capital final de la anterior
        cap_init = initial_seed_cap if i == 0 else mock_data[-1]["ending_balance"]
        
        # --- LÓGICA DE REALISMO ---
        # Si apostamos el 5% de stake, ganar un 10-15% semanal es una EXCELENTE racha (2-3 unidades netas).
        # Multiplicador compuesto: 1.12 promedio semanal -> aprox 3.8x en 12 semanas (más realista que 7x).
        profit_pct = 0.08 + (i % 4 * 0.02) # Entre 8% y 14% semanal
        profit = round(cap_init * profit_pct, 2)
        
        # Pool de partidos reales de Octavos de Final Champions League (DIVERSIFICADOS)
        champions_pairs = [
            {
                "t": "Atalanta vs Dortmund", "s": "⚽ Fútbol", 
                "std": "Over 2.5 Goles", "std_res": "WIN",
                "elite": "Mas de 9.5 Córners", "elite_res": "WIN",
                "w": "Atalanta promedia 6.2 córners por partido en casa."
            },
            {
                "t": "Juventus vs Galatasaray", "s": "⚽ Fútbol", 
                "std": "Gana Juventus", "std_res": "WIN",
                "elite": "Menos de 2.5 Goles", "elite_res": "WIN",
                "w": "Juventus bajo Allegri prioriza el orden defensivo en UCL."
            },
            {
                "t": "PSG vs Monaco", "s": "⚽ Fútbol", 
                "std": "Gana PSG", "std_res": "LOSS",
                "elite": "Más de 4.5 Tarjetas", "elite_res": "WIN",
                "w": "Derbi francés histórico con alta tensión y faltas tácticas."
            },
            {
                "t": "Real Madrid vs Benfica", "s": "⚽ Fútbol", 
                "std": "Gana Real Madrid", "std_res": "WIN",
                "elite": "Hándicap -1 (Madrid)", "elite_res": "WIN",
                "w": "Poder ofensivo del Madrid en el Bernabéu es incontrolable."
            },
        ]
        
        # Seleccionamos un partido de Champions y otros de Tenis/NBA
        idx = i % len(champions_pairs)
        matches = [
            {
                "teams": champions_pairs[idx]["t"],
                "sport": champions_pairs[idx]["s"],
                "market": "Dual: 💵/💎",
                "std_pick": champions_pairs[idx]["std"],
                "std_status": champions_pairs[idx]["std_res"],
                "elite_pick": champions_pairs[idx]["elite"],
                "elite_status": champions_pairs[idx]["elite_res"],
                "status": "DUAL_REPORT",
                "why": champions_pairs[idx]["w"]
            },
            {
                "teams": "Lakers vs Warriors",
                "sport": "🏀 Basket",
                "market": "Dual: 💵/💎",
                "std_pick": "Over 225.5", "std_status": "WIN",
                "elite_pick": "Hándicap -3.5 Lakers", "elite_status": "WIN",
                "status": "DUAL_REPORT",
                "why": "Dominio en la pintura de Anthony Davis."
            },
            {
                "teams": "Alcaraz vs Sinner",
                "sport": "🎾 Tenis",
                "market": "Dual: 💵/💎",
                "std_pick": "Sinner Ganador", "std_status": "WIN",
                "elite_pick": "Over 22.5 Games", "elite_status": "WIN",
                "status": "DUAL_REPORT",
                "why": "Partido largo a 3 sets garantizado."
            }
        ]
        
        mock_data.append({
            "week_id": week_id,
            "date_range": "Periodo Auditoría",
            "initial_balance": round(cap_init, 2),
            "ending_balance": round(cap_init + profit, 2),
            "verdazos": 82.5,
            "erradas": 17.5,
            "roi": round((profit / cap_init) * 100, 2),
            "profit": profit,
            "matches": matches,
            "champion_sport": "⚽ Fútbol Champions" if i % 2 == 0 else "🏀 NBA Elite"
        })
    
    if period == "Mensual": return mock_data[-4:]
    if period == "Semestral": return mock_data
    if period == "Anual": return mock_data
    return [mock_data[-1]]
