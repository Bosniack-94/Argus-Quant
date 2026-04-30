import re

def interpretar_texto_pegado(texto: str):
    """
    Analiza texto crudo para intentar extraer:
    1. Matchup (Equipo A vs Equipo B)
    2. Momios (Americanos o Decimales)
    
    Retorna un diccionario con lo encontrado.
    """
    resultado = {
        "equipo_a": None,
        "equipo_b": None,
        "momio_a": None,
        "momio_b": None,
        "texto_detectado": False
    }

    if not texto:
        return resultado

    # 1. BUSCAR MOMIOS (Americanos primero, luego Decimales)
    # Patrón Americano: +150, -200, +1200
    regex_americano = r'([+-]\d{3,})'
    momios_americanos = re.findall(regex_americano, texto)

    # Patrón Decimal: 1.90, 2.50, 1.25 (Evitar confundir con fechas o horas, basic check)
    regex_decimal = r'(\d+\.\d{2})' 
    momios_decimales = re.findall(regex_decimal, texto)

    last_odd = None

    if momios_americanos:
        # Asumimos que el primer momio es del local/favorito si hay varios
        resultado["momio_a"] = int(momios_americanos[0])
        last_odd = resultado["momio_a"]
        if len(momios_americanos) > 1:
            resultado["momio_b"] = int(momios_americanos[1])
    
    elif momios_decimales:
        # Convertir decimal a americano para el sistema interno
        try:
            dec = float(momios_decimales[0])
            from .conversor_momios import decimal_to_american
            # La funcion retorna string "+100", convertir a int
            resultado["momio_a"] = int(decimal_to_american(dec))
            last_odd = resultado["momio_a"]
        except:
            pass

    # 2. BUSCAR EQUIPOS (Separadores comunes: vs, VS, - )
    # Limpiamos los momios del texto para no confundir
    texto_limpio = texto
    if last_odd:
         texto_limpio = texto.replace(str(last_odd), "")

    # Regex para encontrar "Algo vs Algo"
    # Grupo 1: Equipo A, Grupo 2: Separador, Grupo 3: Equipo B
    regex_vs = r'([a-zA-Z0-9\s]+)\s+(vs\.?|VS|Vs|-)\s+([a-zA-Z0-9\s]+)'
    match_vs = re.search(regex_vs, texto_limpio)

    if match_vs:
        resultado["equipo_a"] = match_vs.group(1).strip()
        resultado["equipo_b"] = match_vs.group(3).strip()
        resultado["texto_detectado"] = True

    return resultado
