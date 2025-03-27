import os
import json
import markdown
from datetime import datetime, timedelta
from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot
from openai import OpenAI
from dotenv import load_dotenv
from dateutil import parser

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ====== Automatický výpočet předchozího měsíce ======
today = datetime.today()
first_day_this_month = datetime(today.year, today.month, 1)
last_month = first_day_this_month - timedelta(days=1)
REPORT_MONTH = last_month.strftime("%Y-%m")
#REPORT_MONTH = "2025-02"
SUMMARIES_DIR = os.path.join("summaries", REPORT_MONTH)
REPORT_DIR = os.path.join("reports", REPORT_MONTH)
os.makedirs(REPORT_DIR, exist_ok=True)

SATISFACTION_TRANSLATION = {
    "Lowest": "Nejnižší",
    "Low": "Nízká",
    "Normal": "Normální",
    "High": "Vysoká",
    "Highest": "Nejvyšší",
    "Unknown": "Nevyplněno",
    "": "Nevyplněno",
    None: "Nevyplněno"
}


def format_datetime(date_str):
    try:
        dt = parser.isoparse(date_str)
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return date_str or "Neznámé"

def generate_chatgpt_summary(tickets):
    summaries = []
    stats = compute_quick_stats(tickets)
    for t in tickets:
        summaries.append(f"- {t['summary_html']}")

    summaries_text = "\n".join(summaries)

    prompt = f"""
Jsi seniorní analytik podpory. Máš před sebou výstupy ze {stats['total']} support ticketů za měsíc {REPORT_MONTH}. Potřebujeme od tebe přehledné a hluboké shrnutí pro produktového vlastníka a další zúčastněné týmy.

Tvůj výstup bude strukturovaný a bude obsahovat:

1. **Klíčová témata a nejčastější typy problémů.**
   - Identifikuj oblasti systému, kde se problémy nejvíce hromadí.
   - Zaměř se na opakující se chyby, požadavky nebo nedorozumění.

2. **Statistika typů úkolů a oblastí.**
   - Napiš, jaké typy ticketů převažují (např. Chyby, Požadavky, Otázky).
   - V jakých částech systému se tyto tikety nejčastěji vyskytují?

3. **Spokojenost uživatelů.**
   - Odhadni celkovou spokojenost na základě hodnocení i formulací ve shrnutích.
   - Uveď konkrétní pozitivní nebo negativní reakce.

4. **Doporučení pro vývoj, UX nebo support.**
   - Navrhni zlepšení na základě trendů ve feedbacku.
   - Pokud je něco častý problém, doporuč změnu v systému nebo procesu.

5. **Další poznatky (volitelné).**
   - Například přístup supportu, opakující se nedorozumění, nebo návrhy na zlepšení dokumentace.

Zde jsou shrnutí jednotlivých ticketů:
{summaries_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Jsi analytik podpory. Tvoříš měsíční shrnutí pro vedení společnosti."},
            {"role": "user", "content": prompt}
        ]
    )
    return markdown.markdown(response.choices[0].message.content)

# ====== Načtení dat ======
def load_tickets(base_path):
    tickets = []
    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if not os.path.isdir(folder_path):
            continue

        aliteo_path = os.path.join(folder_path, "aliteo.json")
        summary_path = os.path.join(folder_path, "summary.md")

        if os.path.exists(aliteo_path) and os.path.exists(summary_path):
            with open(aliteo_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            with open(summary_path, "r", encoding="utf-8") as f:
                summary_raw = f.read()

                # 🔧 Oprava: rozbij nadpis a seznam do samostatných odstavců
                lines = summary_raw.splitlines()
                fixed_lines = []
                for i, line in enumerate(lines):
                    # Pokud je to číslovaný bod s tučným názvem
                    if line.strip().startswith(("1.", "2.", "3.", "4.", "5.")) and "**" in line:
                        fixed_lines.append(line)  # nech řádek
                        fixed_lines.append("")    # přidej prázdný řádek – nový odstavec
                    else:
                        fixed_lines.append(line)

                summary_fixed = "\n".join(fixed_lines)

                # Markdown na HTML s podporou seznamů
                summary_html = markdown.markdown(
                    summary_fixed,
                    extensions=["extra", "sane_lists"],
                    output_format="html5"
                )

            data["summary_html"] = summary_html
            tickets.append(data)
    return tickets


# ====== Statistika ======
def group_and_count(tickets, key):
    return Counter(t.get(key) or "Neznámé" for t in tickets)

def count_comment_authors(tickets):
    authors = Counter()
    for t in tickets:
        for c in t.get("comments", []):
            authors[c["creator"]] += 1
    return authors

def count_task_owners(tickets):
    owners = Counter()
    for t in tickets:
        owner = t.get("owner", "Neznámý")
        owners[owner] += 1
    return owners


# ====== Vykreslení grafů ======
def generate_plotly_graphs(tickets):
    durations = [t["duration_minutes"] / 1440 for t in tickets if t.get("duration_minutes")]
    comments = [t["comment_stats"]["total"] for t in tickets if "comment_stats" in t]
    priorities = group_and_count(tickets, "priority")
    types = group_and_count(tickets, "type")
    areas = group_and_count(tickets, "area")
    contributors = count_comment_authors(tickets)
    owners = count_task_owners(tickets)

    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=[
            "Doba řešení (dny)", "Počet komentářů",
            "Tickety podle priority", "Tickety podle typu",
            "Tickety podle oblasti", "Top komentující",
            "Top autoři úkolů", ""
        ],
        vertical_spacing=0.15
    )

    fig.add_trace(go.Histogram(x=durations, nbinsx=15, name='', marker=dict(line=dict(color='black', width=1.2))), row=1, col=1)
    fig.add_trace(go.Histogram(x=comments, nbinsx=10, name='', marker=dict(line=dict(color='black', width=1.2))), row=1, col=2)
    fig.add_trace(go.Bar(x=list(priorities.keys()), y=list(priorities.values()), name='', marker=dict(line=dict(color='black', width=1.2))), row=1, col=3)
    fig.add_trace(go.Bar(x=list(types.keys()), y=list(types.values()), name='', marker=dict(line=dict(color='black', width=1.2))), row=2, col=1)
    fig.add_trace(go.Bar(x=list(areas.keys()), y=list(areas.values()), name='', marker=dict(line=dict(color='black', width=1.2))), row=2, col=2)

    top_contributors = contributors.most_common(10)
    fig.add_trace(go.Bar(
        x=[c[0] for c in top_contributors],
        y=[c[1] for c in top_contributors],
        name='',
        marker=dict(line=dict(color='black', width=1.2))
    ), row=2, col=3)

    top_owners = owners.most_common(10)
    fig.add_trace(go.Bar(
        x=[o[0] for o in top_owners],
        y=[o[1] for o in top_owners],
        name='',
        marker=dict(line=dict(color='black', width=1.2))
    ), row=3, col=1)

    fig.update_layout(
        height=1000,
        title_text=f"Statistiky support ticketů za {REPORT_MONTH}",
        showlegend=False
    )

    return plot(fig, include_plotlyjs='cdn', output_type='div')

# ====== Hledání extrémů (nejrychlejší a nejpomalejší) ======
def find_extremes(tickets):
    fastest = min((t for t in tickets if t.get("duration_minutes")), key=lambda t: t["duration_minutes"], default=None)
    slowest = max((t for t in tickets if t.get("duration_minutes")), key=lambda t: t["duration_minutes"], default=None)

    fr_fastest = min((t for t in tickets if t.get("first_response_minutes") is not None), key=lambda t: t["first_response_minutes"], default=None)
    fr_slowest = max((t for t in tickets if t.get("first_response_minutes") is not None), key=lambda t: t["first_response_minutes"], default=None)

    return {
        "fastest": fastest,
        "slowest": slowest,
        "first_response_fastest": fr_fastest,
        "first_response_slowest": fr_slowest
    }

def format_duration(minutes):
    if minutes >= 2880:
        return f"{round(minutes / 1440, 1)} dnů"
    elif minutes >= 120:
        return f"{round(minutes / 60, 1)} h"
    else:
        return f"{int(minutes)} min"

def compute_quick_stats(tickets):
    total = len(tickets)
    avg_duration = sum(t["duration_minutes"] for t in tickets if t.get("duration_minutes")) / total if total else 0
    avg_comments = sum(t["comment_stats"]["total"] for t in tickets if "comment_stats" in t) / total if total else 0
    satisfaction_known = sum(1 for t in tickets if t.get("surveyquality") not in [None, "", "Unknown"])
    satisfaction_unknown = total - satisfaction_known
    return {
        "total": total,
        "avg_duration": avg_duration,
        "avg_comments": round(avg_comments, 1),
        "satisfaction_known": satisfaction_known,
        "satisfaction_unknown": satisfaction_unknown
    }

# ====== Vygenerování HTML reportu ======
def generate_html_report(tickets, graph_html):
    stats = compute_quick_stats(tickets)
    extremes = find_extremes(tickets)
    # Seřazení ticketů podle data uzavření
    tickets.sort(key=lambda t: t.get("closed") or "", reverse=False)
    
    def ticket_link(t):
        return f'<a href="https://app.aliteo.com/task/{t["id"]}" target="_blank">{t["name"]}</a>'

    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Měsíční souhrn ticketů - {REPORT_MONTH}</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f9;
                padding: 20px;
            }}
            h1 {{
                text-align: center;
                margin-bottom: 30px;
                color: #0056b3;
            }}
            .ticket-summary {{
                margin-bottom: 40px;
                padding: 20px;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .quick-stats {{
                margin-bottom: 30px;
                padding: 20px;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
            }}
            .quick-stats .stat {{
                font-size: 1.1rem;
                margin-bottom: 10px;
            }}
            summary {{
                cursor: pointer;
                font-size: 1.1rem;
                font-weight: bold;
            }}
            details {{
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 10px;
                background-color: #fff;
            }}
            footer {{
                margin-top: 60px;
                font-size: 0.9rem;
                color: #888;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <h1>📊 Měsíční souhrn ticketů – {REPORT_MONTH}</h1>

        <details class="alert alert-info" role="alert">
            <summary>
                <span class="alert-heading">📌 Shrnutí měsíce od ChatGPT</h4>
            </summary>
            <div class="mt-2">
                {monthly_summary_html}
            </div>
        </details>


        <div class="quick-stats row text-center">
            <div class="col-md-3 stat"><strong>🎟️ Celkem ticketů</strong><br>{stats['total']}</div>
            <div class="col-md-3 stat"><strong>⏱️ Průměrná doba řešení</strong><br>{format_duration(stats['avg_duration'])}</div>
            <div class="col-md-3 stat"><strong>💬 Průměrný počet komentářů</strong><br>{stats['avg_comments']}</div>
            <div class="col-md-3 stat"><strong>📊 Hodnoceno / Nehodnoceno</strong><br>{stats['satisfaction_known']} / {stats['satisfaction_unknown']}</div>
        </div>

        <div class="quick-stats row text-center">
            <div class="col-md-6 stat"><strong>⚡ Nejrychleji vyřešeno:</strong><br>{ticket_link(extremes['fastest'])} – {format_duration(extremes['fastest']['duration_minutes'])}</div>
            <div class="col-md-6 stat"><strong>🐢 Nejpomaleji vyřešeno:</strong><br>{ticket_link(extremes['slowest'])} – {format_duration(extremes['slowest']['duration_minutes'])}</div>
            <div class="col-md-6 stat mt-3"><strong>🚀 Nejrychlejší reakce:</strong><br>{ticket_link(extremes['first_response_fastest'])} – {format_duration(extremes['first_response_fastest']['first_response_minutes'])}</div>
            <div class="col-md-6 stat mt-3"><strong>⏳ Nejpomalejší reakce:</strong><br>{ticket_link(extremes['first_response_slowest'])} – {format_duration(extremes['first_response_slowest']['first_response_minutes'])}</div>
        </div>

        {graph_html}

        <h2 class="mt-5">📝 Shrnutí jednotlivých ticketů</h2>
    """

    for t in tickets:
        s1 = SATISFACTION_TRANSLATION.get(t.get('surveyquality'), 'Nevyplněno')
        s2 = SATISFACTION_TRANSLATION.get(t.get('surveyterm'), 'Nevyplněno')

        html_content += f"""
        <div class="ticket-summary">
            <details>
                <summary>
                    <span>{t['name']}</span><br>
                    <small class="text-muted">Priorita: {t['priority']} | Typ: {t.get('type', 'Neznámé')} | Uzavřeno: {format_datetime(t['closed'])}</small>
                </summary>
                <div class="mt-3">
                    <p><strong>🔗 Úkol v Aliteo:</strong> <a href="https://app.aliteo.com/task/{t['id']}" target="_blank">ODKAZ</a></p>
                    <p><strong>👤 Vlastník:</strong> {t['owner']}</p>
                    <p><strong>📊 Spokojenost:</strong> {s1}, {s2}</p>
                    <hr>
                    <div>{t['summary_html']}</div>
                </div>
            </details>
        </div>
        """

    html_content += """
        <footer class="mt-5 text-center text-muted">
            <p>Generováno automaticky – AO ticket Summarizer - {REPORT_MONTH}</p>
        </footer>
    </body>
    </html>
    """

    output_path = os.path.join(REPORT_DIR, "monthly_summary.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Report uložen do {output_path}")


# ====== Main ======
if __name__ == "__main__":
    tickets = load_tickets(SUMMARIES_DIR)
    graph_html = generate_plotly_graphs(tickets)
    monthly_summary_html = generate_chatgpt_summary(tickets)
    generate_html_report(tickets, graph_html)
