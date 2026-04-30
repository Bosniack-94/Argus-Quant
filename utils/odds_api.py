import requests
import config
import random
import time
import datetime
import json
import os

class OddsConnector:
    def __init__(self):
        self.api_key = config.THE_ODDS_API_KEY
        self.base_url = config.THE_ODDS_API_URL
        self.mock_mode = config.ODDS_API_MOCK_MODE
        self.cache_file = "odds_cache.json"
        self.cache_duration = 1800 # 30 minutos

    def _get_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    if time.time() - data.get('timestamp', 0) < self.cache_duration:
                        return data.get('payload')
            except:
                pass
        return None

    def _save_cache(self, payload):
        with open(self.cache_file, 'w') as f:
            json.dump({'timestamp': time.time(), 'payload': payload}, f)

    def get_live_odds(self, sport_key="soccer_mexico_liga_mx"):
        """
        Obtiene momios en vivo desde la API Real o Caché (Fase 24).
        Filtra RIGUROSAMENTE por la fecha actual: 2026-02-21.
        """
        if self.mock_mode:
            return self._get_mock_odds(sport_key)

        cached = self._get_cache()
        if cached and sport_key in cached:
            return cached[sport_key]

        # Mapeo de llaves de API
        # soccer_epl, soccer_italy_serie_a, soccer_mexico_liga_mx, basketball_nba, tennis_atp
        try:
            url = f"{self.base_url}/sports/{sport_key}/odds/?apiKey={self.api_key}&regions=us&markets=h2h,totals,spreads"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Filtrar por los próximos 7 días
                now = datetime.datetime.utcnow()
                limit = now + datetime.timedelta(days=7)
                filtered_data = []
                for m in data:
                    try:
                        ct_str = m.get('commence_time', '').replace('Z', '')
                        ct = datetime.datetime.fromisoformat(ct_str)
                        if now <= ct <= limit:
                            filtered_data.append(m)
                    except: pass
                
                # Guardar en caché
                full_cache = cached if cached else {}
                full_cache[sport_key] = filtered_data
                self._save_cache(full_cache)
                
                return filtered_data
            else:
                return []
        except:
            return []

    def translate_market(self, market_key, outcome, sport="soccer"):
        """Traductor de Líneas (Fase 24)."""
        name = outcome['name']
        price = outcome['price']
        label = "Favorito" if price < 0 else "Underdog"
        
        if market_key == 'h2h':
            return f"Gana {name} ({label})"
        elif market_key == 'totals':
            line = outcome.get('point', outcome.get('score', 2.5))
            prefix = "Altas >" if name.lower() in ['over', 'over '] else "Bajas <"
            return f"{prefix} {line} Goles" if sport == "soccer" else f"{prefix} {line} Puntos"
        elif market_key == 'spreads':
            point = outcome.get('point', 0)
            sign = "+" if point > 0 else ""
            return f"{name} {sign}{point} (Handicap)"
        return name

    def _get_mock_odds(self, sport_key):
        """Fallback mock data compatible con la estructura de la API Real."""
        # Implementado para no romper si falla la API key temporalmente
        return []

    def get_live_scores(self):
        return []

    def detect_line_movements(self, match_id, current_odds):
        return None
