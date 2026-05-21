import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.database import init_db
from core.task_board_service import print_json, run_legal_review


def main():
    init_db()
    print_json(run_legal_review())


if __name__ == "__main__":
    main()
