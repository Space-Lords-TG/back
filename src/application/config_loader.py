import toml
from pathlib import Path

# Абсолютный путь до config.toml, лежащего рядом
CONFIG_PATH = Path(__file__).parent / "config.toml"

# Читаем и загружаем конфиг
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = toml.load(f)
