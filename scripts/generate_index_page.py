import os

reports_dir = "reports"
index_path = "index.html"

report_folders = sorted(os.listdir(reports_dir))
links = []

for folder in report_folders:
    summary_file = os.path.join(reports_dir, folder, "monthly_summary.html")
    if os.path.exists(summary_file):
        links.append(f'<li><a href="reports/{folder}/monthly_summary.html">{folder}</a></li>')

html = f"""<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8" />
  <title>Měsíční support reporty</title>
  <style>
    body {{ font-family: sans-serif; padding: 2em; background: #f7f7f7; }}
    h1 {{ color: #333; }}
    ul {{ list-style-type: none; padding: 0; }}
    li {{ margin-bottom: 10px; }}
    a {{ text-decoration: none; color: #0066cc; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>📊 Měsíční reporty supportu</h1>
  <ul>
    {''.join(links)}
  </ul>
</body>
</html>"""

with open(index_path, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Vygenerován index.html pro všechny reporty.")
