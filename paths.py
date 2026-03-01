# ========================================
# Centralized Project Paths
# ========================================

from pathlib import Path

# Root directory of the backend project
BASE_DIR = Path(__file__).resolve().parent

# Core folders
LABS_DIR = BASE_DIR / "labs"
LOGS_DIR = BASE_DIR / "logs"

# Ensure required folders exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LABS_DIR.mkdir(parents=True, exist_ok=True)