import os
from datetime import datetime

reports_root = "reports"
output_file = "index.html"

MONTH_NAMES = {
    "01": ("Leden", "Január"),
    "02": ("Únor", "Február"),
    "03": ("Březen", "Marec"),
    "04": ("Duben", "Apríl"),
    "05": ("Květen", "Máj"),
    "06": ("Červen", "Jún"),
    "07": ("Červenec", "Júl"),
    "08": ("Srpen", "August"),
    "09": ("Září", "September"),
    "10": ("Říjen", "Október"),
    "11": ("Listopad", "November"),
    "12": ("Prosinec", "December"),
}

report_folders = sorted([
    d for d in os.listdir(reports_root)
    if os.path.isdir(os.path.join(reports_root, d)) and os.path.exists(os.path.join(reports_root, d, "monthly_summary.html"))
], reverse=True)

html = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>📁 Přehled měsíčních reportů</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f8f9fa;
            padding: 30px;
        }
        h1 {
            text-align: center;
            margin-bottom: 40px;
            color: #343a40;
        }
        .month-link {
            padding: 20px;
            margin-bottom: 15px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.3s ease-in-out;
            text-decoration: none;
            color: #212529;
            font-size: 1.2rem;
        }
        .month-link:hover {
            background-color: #e9ecef;
            transform: scale(1.02);
        }
    </style>
</head>
<body>
    <h1>📊 Měsíční reporty support ticketů</h1>
    <div class="container">
"""

for folder in report_folders:
    try:
        year, month = folder.split("-")
        cz, sk = MONTH_NAMES.get(month, ("neznámý", "neznámy"))
        label = f"{cz} ({sk}) {year}"
    except Exception:
        label = folder

    html += f"""
        <a class="month-link d-block" href="reports/{folder}/monthly_summary.html">
            📅 {label}
        </a>
    """

html += """
    </div>
    <footer class="text-center mt-5 text-muted">
        <p>Generováno automaticky – <a href="https://github.com/JosefBouchal/AOticketsummarizer" target="_blank">AO ticket summarizer</a></p>
    </footer>
</body>
</html>
"""

with open(output_file, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Vytvořen index: {output_file}")