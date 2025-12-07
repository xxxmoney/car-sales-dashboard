# Dataset path
DATA_SET_PATH: str = "data/autoscout24-germany-dataset.csv"

# Chart theme
THEME_TEMPLATE: str = "plotly_white"

# --- Modern Color Palette (Flat UI) ---
# Professional, high-contrast colors suitable for presentations
COLOR_PRIMARY = "#2C3E50"      # Dark Blue (Base/Text)
COLOR_SECONDARY = "#E67E22"    # Carrot Orange (Highlights/Buttons)
COLOR_ACCENT = "#18BC9C"       # Teal (Positive indicators)
COLOR_INFO = "#3498DB"         # Light Blue (Neutral info)
COLOR_DANGER = "#E74C3C"       # Red (Warnings/High price)

# Specific chart sequences
# A harmonized sequence for categories
COLOR_SEQUENCE = [
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_ACCENT,
    COLOR_INFO,
    "#F1C40F", # Yellow
    "#9B59B6"  # Purple
]