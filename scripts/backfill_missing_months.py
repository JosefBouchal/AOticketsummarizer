import subprocess
import sys
from datetime import datetime
from pathlib import Path


def validate_month(value):
    return datetime.strptime(value, "%Y-%m")


def run_step(command):
    print(f"Running: {' '.join(command)}")
    subprocess.run(command, check=True)


def month_range(from_month, to_month):
    current = validate_month(from_month)
    end = validate_month(to_month)
    months = []

    while current <= end:
        months.append(current.strftime("%Y-%m"))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    return months


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/backfill_missing_months.py YYYY-MM YYYY-MM")
        raise SystemExit(1)

    from_month = sys.argv[1]
    to_month = sys.argv[2]
    from_date = validate_month(from_month)
    to_date = validate_month(to_month)

    if from_date > to_date:
        print("from_month must be earlier than or equal to to_month")
        raise SystemExit(1)

    target_months = month_range(from_month, to_month)
    print(f"Target months: {', '.join(target_months)}")

    run_step(["python", "scripts/aliteo_summary.py"])
    run_step(["python", "scripts/generate_summaries.py"])
    run_step(["python", "scripts/generate_monthly_report.py"])
    run_step(["python", "scripts/generate_index_page.py"])

    print("\nResult check:")
    for month in target_months:
        summaries_exists = Path("summaries", month).exists()
        report_exists = Path("reports", month, "monthly_summary.html").exists()
        print(f"- {month}: summaries={summaries_exists}, report={report_exists}")
