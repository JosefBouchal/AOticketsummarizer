import os
import json
import markdown
from datetime import datetime
from dotenv import load_dotenv
from collections import Counter
from dateutil import parser
from pathlib import Path
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.offline import plot
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def generate_chatgpt_summary(tickets, batch_size=100):
    def generate_batch_summary(batch, batch_number):
        summaries = [f"- {t['summary_html']}" for t in batch]
        summaries_text = "\n".join(summaries)

        prompt = f"""
Jsi seniorní analytik podpory. Máš před sebou výstupy ze {len(batch)} support ticketů. Potřebujeme od tebe přehledné a hluboké shrnutí pro produktového vlastníka a další zúčastněné týmy.

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

Zde jsou shrnutí jednotlivých ticketů:
{summaries_text}
"""
        print(f"📝 Generuji dílčí souhrn pro batch {batch_number}...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Jsi analytik podpory. Tvoříš shrnutí pro vedení společnosti."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    # Rozdělení na bloky
    batch_summaries = []
    for i in range(0, len(tickets), batch_size):
        batch = tickets[i:i + batch_size]
        batch_summary = generate_batch_summary(batch, (i // batch_size) + 1)
        batch_summaries.append(batch_summary)

    # Finální souhrn ze všech dílčích shrnutí
    final_summaries_text = "\n".join(batch_summaries)
    final_prompt = f"""
Jsi seniorní analytik podpory. Zde jsou dílčí souhrny několika set support ticketů. Potřebujeme přehledné shrnutí všech uvedených dílčích souhrnů pro produktového vlastníka a další zúčastněné týmy.

Tvůj výstup bude strukturovaný a bude obsahovat:

1. **Shrnutí hlavních témat a problémů z jednotlivých dílčích souhrnů.**
2. **Celkové statistiky a trendy v podpoře.**
3. **Klíčová doporučení pro vývoj, UX nebo support.**
4. **Další poznatky a analýzy.**

Zde jsou dílčí souhrny:
{final_summaries_text}
"""
    print("📝 Generuji finální shrnutí ze všech dílčích souhrnů...")
    final_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Jsi analytik podpory. Tvoříš finální shrnutí pro vedení společnosti."},
            {"role": "user", "content": final_prompt}
        ]
    )
    return markdown.markdown(final_response.choices[0].message.content)


def format_duration(minutes):
    return f"{minutes / 60:.1f} h" if minutes else "N/A"

def load_tickets_from_range(from_month, to_month):
    tickets = []
    summaries_root = Path("summaries")

    from_date = datetime.strptime(from_month, "%Y-%m")
    to_date = datetime.strptime(to_month, "%Y-%m")

    for month_folder in sorted(summaries_root.iterdir()):
        if not month_folder.is_dir():
            continue

        try:
            month_date = datetime.strptime(month_folder.name, "%Y-%m")
        except ValueError:
            continue

        if from_date <= month_date <= to_date:
            for folder in month_folder.iterdir():
                if not folder.is_dir():
                    continue

                aliteo_path = folder / "aliteo.json"
                summary_path = folder / "summary.md"

                if aliteo_path.exists() and summary_path.exists():
                    with open(aliteo_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    with open(summary_path, "r", encoding="utf-8") as f:
                        summary_html = markdown.markdown(f.read(), extensions=["extra", "sane_lists"], output_format="html5")
                    data["summary_html"] = summary_html
                    tickets.append(data)

    return tickets

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
        title_text=f"Souhrnné statistiky",
        showlegend=False
    )

    return plot(fig, include_plotlyjs='cdn', output_type='div')

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

def format_datetime(date_str):
    try:
        dt = parser.isoparse(date_str)
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return date_str or "Neznámé"

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
def generate_html_report(tickets, graph_html, from_month, to_month):
    stats = compute_quick_stats(tickets)
    extremes = find_extremes(tickets)
    tickets.sort(key=lambda t: t.get("closed") or "", reverse=False)
    
    def ticket_link(t):
        return f'<a href="https://app.aliteo.com/task/{t["id"]}" target="_blank">{t["name"]}</a>'

    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Souhrn ticketů za období - {from_month} až {to_month}</title>
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
        <h1>📊 Souhrn ticketů za období - {from_month} až {to_month}</h1>

        <details class="alert alert-info" role="alert">
            <summary>
                <span class="alert-heading">📌 Shrnutí měsíce od ChatGPT</h4>
            </summary>
            <div class="mt-2">
                <div>{chatgpt_summary}</div>
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
            <p>Generováno automaticky – <a href="https://github.com/JosefBouchal/AOticketsummarizer.git">AO ticket Summarizer</a></p>
        </footer>
    </body>
    </html>
    """

    report_dir = f"reports/report_{from_month}_to_{to_month}"
    os.makedirs(report_dir, exist_ok=True)
    output_path = os.path.join(report_dir, "summary.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Souhrnný report vytvořen: {output_path}")

if __name__ == "__main__":
    import sys

    # Ověření, zda jsou zadány potřebné argumenty
    if len(sys.argv) < 3:
        print("❌ Chybí argumenty: from_month a to_month")
        print("Použití: python generate_custom_report.py YYYY-MM YYYY-MM")
        exit(1)

    from_month = sys.argv[1]
    to_month = sys.argv[2]

    tickets = load_tickets_from_range(from_month, to_month)
    if not tickets:
        print("⚠️  Nebyly nalezeny žádné tickety v zadaném období.")
        exit(1)

    graph_html = generate_plotly_graphs(tickets)
    chatgpt_summary = generate_chatgpt_summary(tickets)
    generate_html_report(tickets, graph_html, from_month, to_month)