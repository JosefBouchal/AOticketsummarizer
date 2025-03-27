import os
import base64
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

API_URL = "https://api.aliteo.com/AddTask"

API_KEY = os.environ.get("ALITEO_JBO_API_KEY")
COMPANY = os.environ.get("ALITEO_JBO_COMPANY")
PROJECT = os.environ.get("ALITEO_JBO_PROJECT")
EMAIL = "josef-bouchal@seznam.cz"
CREATOR_EMAIL = "josef-bouchal@seznam.cz"

#REPORT_MONTH = datetime.now().replace(day=1).strftime("%Y-%m")

# ====== Automatický výpočet předchozího měsíce ======
today = datetime.today()
first_day_this_month = datetime(today.year, today.month, 1)
last_month = first_day_this_month - timedelta(days=1)
REPORT_MONTH = last_month.strftime("%Y-%m")
#REPORT_MONTH = "2025-02"
HTML_PATH = os.path.join("reports", REPORT_MONTH, "monthly_summary.html")

MONTH_NAMES = {
    "01": ("leden", "január"),
    "02": ("únor", "február"),
    "03": ("březen", "marec"),
    "04": ("duben", "apríl"),
    "05": ("květen", "máj"),
    "06": ("červen", "jún"),
    "07": ("červenec", "júl"),
    "08": ("srpen", "august"),
    "09": ("září", "september"),
    "10": ("říjen", "október"),
    "11": ("listopad", "november"),
    "12": ("prosinec", "december"),
}

report_month_number = REPORT_MONTH.split("-")[1]
cz_month, sk_month = MONTH_NAMES.get(report_month_number, ("neznámý", "neznámy"))


# Počet analyzovaných ticketů
def count_tickets():
    summary_dir = os.path.join("summaries", REPORT_MONTH)
    if not os.path.exists(summary_dir):
        return 0
    return len([d for d in os.listdir(summary_dir) if os.path.isdir(os.path.join(summary_dir, d))])

number_of_tickets = count_tickets()

# Načtení HTML a převod do base64
with open(HTML_PATH, "rb") as f:
    encoded_html = base64.b64encode(f.read()).decode("utf-8")

headers = {
    "Content-Type": "application/json",
    "apikey": API_KEY
}

# HTML description
description = f"""
<div>
<span>V příloze se nachází souhrn reportů v supportu za měsíc <b>{cz_month} ({sk_month})</b>.</span>
</div>
<div>V tomto období bylo analyzováno celkem <b>{number_of_tickets} ticketů</b>.</div>
<div><i>Toto je automaticky generovaný úkol za pomocí AO Ticker Summarizer</i></div>
""".strip()

comment = f"""
<div><span class=\"user xcid\" data-id=\"a01t6ckg80gqpt\" contenteditable=\"false\">@ Josef Bouchal (josef-bouchal@seznam.cz)</span> V příloze se nachází souhrn reportů v supportu za měsíc <b>{cz_month} ({sk_month})</b>.</div>
<div><i>Tento komentář je automaticky generovaný pomocí AO Ticker Summarizer</i></div>
""".strip()

payload = {
    "company": COMPANY,
    "email": EMAIL,
    "project": PROJECT,
    "name": f"Měsíční shrnutí supportu ({REPORT_MONTH})",
    "description": description,
    "comments": [
        {
            "comment": comment,
            "emailcreator": EMAIL
        }
    ],
    "attachments": [
        {
            "filename": f"monthly_summary_{REPORT_MONTH}.html",
            "contenttype": "Base64",
            "content": encoded_html,
            "emailcreator": EMAIL
        }
    ]
}

print("📤 ODESÍLANÝ REQUEST:")
print(json.dumps(payload, indent=2, ensure_ascii=False))

response = requests.post(API_URL, headers=headers, json=payload)

print("📥 ODPOVĚĎ API:")
print(f"Status code: {response.status_code}")
try:
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception:
    print(response.text)

if response.ok:
    print("✅ Úkol byl úspěšně vytvořen v Aliteo.")
else:
    print("❌ Chyba při vytváření úkolu.")