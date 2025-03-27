import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

summaries_path = "summaries"

skipped_log = []

# Projde jednotlivé měsíce
for month_folder in os.listdir(summaries_path):
    month_path = os.path.join(summaries_path, month_folder)
    if not os.path.isdir(month_path):
        continue

    # Projde jednotlivé tickety v daném měsíci
    for task_folder in os.listdir(month_path):
        task_path = os.path.join(month_path, task_folder)
        aliteo_file = os.path.join(task_path, "aliteo.json")
        summary_file = os.path.join(task_path, "summary.md")

        if not os.path.isfile(aliteo_file) or os.path.isfile(summary_file):
            continue  # přeskočí, pokud chybí vstup nebo už existuje výstup

        with open(aliteo_file, "r", encoding="utf-8") as f:
            task_data = json.load(f)

        prompt = f"""
Na základě následujících dat o support ticketu vytvoř shrnutí ve **striktně jednotné struktuře a formátu**, která bude obsahovat:

### Shrnutí support ticketu

1. **Téma ticketu:**
   - stručně, jednou větou shrň hlavní problém ticketu. Vyhni se opakování detailů, které se objeví v dalších bodech.

2. **Spokojenost:**
   - na základě `surveyquality`, `surveyterm`, případně i formulace posledních komentářů, zhodnoť míru spokojenosti uživatele. Pokud není hodnocení vyplněno, ale z komentářů lze usuzovat, že uživatel byl spokojený (např. poděkování, potvrzení funkčnosti), napiš to jako odhad (např. „Pravděpodobně spokojený – uživatel potvrdil funkčnost“). Pokud není dostupné nic, napiš „Nelze odhadnout – chybí hodnocení i zpětná vazba“.

3. **Klíčové kroky provedené během řešení:**
   - popiš hlavní kroky, které vedly k vyřešení (začínej malým písmenem a ukonči tečkou)
   - kroky piš věcně, může jich být libovolně podle obsahu ticketu
   - nepiš čísla, používej odrážky

4. **Poznámky:**
   - každá poznámka na nový řádek s odrážkou
   - může jít o délku řešení, počet komentářů, formu komunikace, úroveň spolupráce, vývojová omezení apod.
   - piš různorodě, vyhni se opakujícím se frázím

5. **Doporučení pro vývoj/support:**
   - stručná, praktická doporučení (každé na nový řádek s odrážkou)
   - není nutné mít přesně tři – přizpůsob počet obsahu
   - vždy začínej malým písmenem a ukonči tečkou

Zachovej přesně tento formát: nadpis, číslování hlavních bodů, tučné názvy sekcí, odrážky v bodech 3 a 5. Nevkládej nic mimo tuto strukturu. Styl piš přirozený a profesionální.

Data:
{json.dumps(task_data, ensure_ascii=False, indent=2)}
"""

        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        num_tokens = len(encoding.encode(prompt))
        if(num_tokens > 199999):
            print(f"⛔ Přeskočeno {month_folder}/{task_folder} – {num_tokens} tokenů (limit 199999)")
            skipped_log.append(f"{month_folder}/{task_folder} – {num_tokens} tokenů")
            continue

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Jsi analytik support dat. Vytváříš kvalitní, čitelné a variabilní shrnutí support ticketů."},
                {"role": "user", "content": prompt}
            ]
        )

        summary = response.choices[0].message.content

        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"✅ Summary generated for {month_folder}/{task_folder}")