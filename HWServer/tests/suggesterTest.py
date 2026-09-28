import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from HWServer.utils import suggester as sug


if __name__ == "__main__":
    s = sug.Suggester()
    print(s.get_device_advice("electric_heating", 500))