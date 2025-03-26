import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from dotenv import load_dotenv
from dateutil import parser

load_dotenv()

# Config
FILTERED_TASKS_URL = "https://api.aliteo.com/FilteredTasks"
DETAIL_TASK_URL = "https://api.aliteo.com/DetailTask"
COMPONENT_INFO_URL = "https://api.aliteo.com/ComponentInfo"

API_KEY = os.environ.get("ALITEO_API_KEY")
EMAIL = os.environ.get("ALITEO_EMAIL")
COMPANY = os.environ.get("ALITEO_COMPANY")
FILTERID = os.environ.get("ALITEO_FILTERID")

HEADERS = {
    "Content-Type": "application/json",
    "apikey": API_KEY
}

user_cache = {}

priority_mapping = {
    "Lowest": "Nejnižší",
    "Low": "Nízká",
    "Normal": "Normální",
    "High": "Vyšší",
    "Highest": "Nejvyšší"
}

type_mapping = {
    "a04uaha6p00i8j": "Chyba",
    "a026bj3v005n4b": "Konzultace/dat. servis",
    "a04h0eolsg1j35": "Podnět",
    "a026bj3v001n4b": "Kritická chyba"
}

area_mapping = {
    "a04kg9katg0o4m": "API",
    None: "Bez",
    "a04kg9p9q00ujt": "ISK",
    "a026slkpk0h0e6": "Můj panel",
    "a026slkpk010e6": "Nastavení společnosti",
    "a04u4o00400i8j": "Nastavení uživatele",
    "a026slkpk050e6": "Projekty",
    "a03g6j8bsg0o7o": "Synchronizace",
    "a026slkpk0b0e6": "Výkazy práce",
    "a026slkpk0f0e6": "Úkoly"
}

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def fetch_user_name(user_id):
    if user_id in user_cache:
        return user_cache[user_id]

    response = requests.post(COMPONENT_INFO_URL, headers=HEADERS, json={
        "company": COMPANY,
        "componentid": user_id
    })
    name = response.json().get("name", user_id) if response.ok else user_id
    user_cache[user_id] = name
    return name

# Step 1: Get task IDs
payload_filtered = {
    "company": COMPANY,
    "email": EMAIL,
    "filterid": FILTERID
}

response = requests.post(FILTERED_TASKS_URL, headers=HEADERS, json=payload_filtered)
tasks_data = response.json()

if not tasks_data.get("tasks"):
    print("❌ Response data:", json.dumps(tasks_data, indent=2))
    raise Exception("No tasks found")

task_ids = [task["id"] for task in tasks_data["tasks"]]

# Step 2: Get task details
payload_detail = {
    "company": COMPANY,
    "ids": task_ids
}

detail_response = requests.post(DETAIL_TASK_URL, headers=HEADERS, json=payload_detail)
detail_data = detail_response.json()

# Step 3: Preprocess and save individually
os.makedirs("summaries", exist_ok=True)

for task in detail_data.get("data", []):
    created = task.get("created")
    closed = task.get("closedate")
    created_dt = parser.isoparse(created) if created else None
    closed_dt = parser.isoparse(closed) if closed else None
    duration = int((closed_dt - created_dt).total_seconds() / 60) if created_dt and closed_dt else None

    owner_id = task.get("owner")
    owner_name = fetch_user_name(owner_id) if owner_id else None

    comments = []
    unique_authors = set()
    from_owner = 0
    first_response_minutes = None

    for comment in task.get("comments", []):
        if comment.get("creator") != "a02820ivr014ba" and comment.get("comment"):
            creator_id = comment.get("creator")
            creator_name = fetch_user_name(creator_id)
            comment_time = parser.isoparse(comment["created"])

            if creator_id != owner_id:
                unique_authors.add(creator_id)
                if first_response_minutes is None and created_dt:
                    first_response_minutes = int((comment_time - created_dt).total_seconds() / 60)
            else:
                from_owner += 1

            comments.append({
                "creator": creator_name,
                "comment": clean_html(comment["comment"])
            })

    attr_type = None
    attr_area = None
    for attr in task.get("attributes", []):
        if attr["id"] == "a026bj0o8g1n4b":
            attr_type = type_mapping.get(attr.get("value"))
        elif attr["id"] == "a026slh55010e6":
            attr_area = area_mapping.get(attr.get("value"))

    preprocessed = {
        "id": task.get("id"),
        "created": created,
        "closed": closed,
        "duration_minutes": duration,
        "first_response_minutes": first_response_minutes,
        "name": task.get("name"),
        "description": clean_html(task.get("description", "")),
        "owner": owner_name,
        "priority": priority_mapping.get(task.get("priority"), task.get("priority")),
        "surveyquality": task.get("surveyquality"),
        "surveyterm": task.get("surveyterm"),
        "type": attr_type,
        "area": attr_area,
        "comment_stats": {
            "total": len(comments),
            "from_owner": from_owner,
            "from_others": len(comments) - from_owner,
            "unique_authors": len(unique_authors)
        },
        "comments": comments
    }

    if closed_dt:
        year_month = closed_dt.strftime("%Y-%m")
    else:
        year_month = "unknown"

    folder_name = f"{year_month}/{task.get('id')}"
    task_folder = os.path.join("summaries", folder_name)
    os.makedirs(task_folder, exist_ok=True)

    with open(os.path.join(task_folder, "aliteo.json"), "w", encoding="utf-8") as f:
        json.dump(preprocessed, f, ensure_ascii=False, indent=2)

print("✅ All preprocessed data saved per task in summaries/ folder.")
