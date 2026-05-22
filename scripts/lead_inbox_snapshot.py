import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.database import init_db
from core.lead_service import list_inbox_leads, print_json


def main():
    init_db()
    print_json(list_inbox_leads())


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(str(exc))
