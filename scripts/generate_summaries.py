import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

summaries_path = "summaries"

for folder in os.listdir(summaries_path):
    folder_path = os.path.join(summaries_path, folder)
    aliteo_file = os.path.join(folder_path, "aliteo.json")
    summary_file = os.path.join(folder_path, "summary.md")  # nový výstup

    if not os.path.isfile(aliteo_file) or os.path.isfile(summary_file):
        continue  # přeskočí, pokud chybí vstup nebo už existuje výstup

    with open(aliteo_file, "r", encoding="utf-8") as f:
        task_data = json.load(f)

    prompt = f"""
Zpracuj následující data o support ticketu a vytvoř shrnutí obsahující:
1. Téma ticketu
2. Spokojenost (na základě `surveyquality`, `surveyterm`, případně odhad z komentářů)
3. Klíčové kroky provedené během řešení
4. Poznámky
5. Doporučení pro vývoj/support

Data:
{json.dumps(task_data, ensure_ascii=False, indent=2)}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Jsi support analytik, který vytváří přehledná shrnutí support ticketů."},
            {"role": "user", "content": prompt}
        ]
    )

    summary = response.choices[0].message.content

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)  # uloží jako čistý Markdown

    print(f"✅ Summary generated for {folder}")
