import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.database import init_db
from core.lead_service import approve_lead, print_json, reject_lead


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python lead_inbox_action.py <approve|reject> <lead_id>")

    action, lead_id = sys.argv[1], sys.argv[2]
    if action not in {"approve", "reject"}:
        raise SystemExit("Action must be either 'approve' or 'reject'.")

    init_db()
    if action == "approve":
        print_json(approve_lead(lead_id))
        return

    print_json(reject_lead(lead_id))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(str(exc))
