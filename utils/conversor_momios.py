def decimal_to_american(decimal_odd):
    """
    Convierte un momio decimal a formato americano.
    
    Reglas:
    - >= 2.00: (decimal - 1) * 100. Resultado positivo (ej. +200)
    - < 2.00: -100 / (decimal - 1). Resultado negativo (ej. -110)
    
    Args:
        decimal_odd (float): El momio en formato decimal (ej. 1.90)
        
    Returns:
        str: El momio en formato americano (ej. "-110", "+150")
    """
    if decimal_odd <= 1.0:
        return "N/A" # Momios <= 1.0 no son validos para apuestas estandar

    if decimal_odd >= 2.0:
        american = (decimal_odd - 1) * 100
        return f"+{int(round(american))}"
    else:
        american = -100 / (decimal_odd - 1)
        return f"{int(round(american))}"

if __name__ == "__main__":
    # Test cases rapidos
    test_odds = [1.909, 2.00, 2.50, 1.50, 1.10]
    print(f"{'Decimal':<10} | {'Americano':<10}")
    print("-" * 25)
    for odd in test_odds:
        print(f"{odd:<10} | {decimal_to_american(odd):<10}")
