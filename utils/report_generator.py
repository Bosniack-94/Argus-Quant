from fpdf import FPDF
import os
from .persistence import load_bankroll

REPORT_DIR = "reports"

class ArgusReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Argus Quant - Weekly Performance Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_weekly_report():
    """Genera un PDF con el estado actual."""
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)
        
    data = load_bankroll()
    bankroll = data['current_bankroll']
    streak = data['streak']
    history = data['history']
    
    pdf = ArgusReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # 1. Summary Section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. Financial Summary", 0, 1)
    pdf.set_font("Arial", size=12)
    
    pdf.cell(0, 10, f"Current Bankroll: ${bankroll:,.2f}", 0, 1)
    
    # Calculate simplistic profit (assuming 1000 start if not tracked explicitly in strict history)
    # For now showcase current state
    rating = "Stable"
    if bankroll > 1100: rating = "Excellent (Profit)"
    elif bankroll < 900: rating = "Risk (Drawdown)"
    
    pdf.cell(0, 10, f"Status: {rating}", 0, 1)
    pdf.ln(5)

    # 2. Streak Analysis
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. Recent Form (Last 5)", 0, 1)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Streak: {' - '.join(streak) if streak else 'No Data'}", 0, 1)
    pdf.ln(5)
    
    # 3. Pick History (Last 10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. Last 10 Recommendations", 0, 1)
    pdf.set_font("Arial", size=10)
    
    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(40, 10, "Date", 1, 0, 'C', 1)
    pdf.cell(80, 10, "Matchup", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Score", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Result", 1, 1, 'C', 1)
    
    # Table Rows
    pdf.set_font("Arial", size=9)
    recent_history = history[:10]
    for pick in recent_history:
        date = pick.get('timestamp', 'N/A')
        match = pick.get('matchup', 'N/A')[:35] # Truncate if too long
        score = str(pick.get('score', 0))
        rec = pick.get('recommendation', 'N/A')
        
        # Simple coloring logic for text not fill (FPDF simple)
        pdf.cell(40, 10, date, 1)
        pdf.cell(80, 10, match, 1)
        pdf.cell(30, 10, score, 1, 0, 'C')
        pdf.cell(40, 10, rec, 1, 1)
        
    filename = os.path.join(REPORT_DIR, "Argus_Weekly_Report.pdf")
    pdf.output(filename)
    return filename
