from pathlib import Path

from split_settings.tools import include

BASE_DIR = Path(__file__).resolve().parents[2]

include(
    'components/base.py',
    'components/database.py',
    scope=globals(),
)
