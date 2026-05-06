"""測試共用設定。"""

import sys
from pathlib import Path


def _append_project_root_to_path() -> None:
    """將專案根目錄加入 Python 匯入路徑。"""
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


_append_project_root_to_path()
