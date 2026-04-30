import sys
from utils import decimal_to_american
from modules import TenisBrain, FutbolBrain, NBABrain
import config

def main():
    print("🚀 Iniciando Argus Quant - Sports Analysis System")
    print("====================================================")
    
    # Ejemplo de uso del conversor
    test_odd = 1.90
    american_odd = decimal_to_american(test_odd)
    print(f"[TEST] Conversión de Momio: {test_odd} (Decimal) -> {american_odd} (Americano)")
    
    # Inicializar cerebros
    tenis = TenisBrain()
    futbol = FutbolBrain()
    nba = NBABrain()
    
    print(f"\n[SYSTEM] Módulos cargados: {tenis.name}, {futbol.name}, {nba.name}")
    print(f"[CONFIG] Umbral Diamante: >{config.SCORE_DIAMOND} pts")
    
    print("\n✅ Estructura creada exitosamente. Esperando instrucciones...")

if __name__ == "__main__":
    main()
