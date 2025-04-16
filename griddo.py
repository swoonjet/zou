import streamlit as st
import string
import random
from PIL import Image, ImageDraw, ImageFont
import os

# === CONFIG ===
GRID_SIZE = 25
CELL_SIZE = 50  # More space
FONT_SIZE = 36  # Bigger characters
HIDDEN_WORD = "NAMMU"
CHARACTERS = string.ascii_letters + string.digits
DIRECTIONS = [
    (0, 1),   # →
    (1, 0),   # ↓
    (1, 1),   # ↘
    (1, -1),  # ↙
]

# === FONT SETUP ===
# Try to load a monospace font
def load_mono_font(size):
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/Library/Fonts/Courier New.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "C:/Windows/Fonts/consola.ttf"
    ]
    for path in font_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

font = load_mono_font(FONT_SIZE)

# === CHAR GENERATOR ===
def generate_char(seed, i, j):
    random.seed(seed + i * GRID_SIZE + j)
    return random.choice(CHARACTERS)

# === PLACEMENT HELPER ===
def can_place_word(row, col, dx, dy, word_len):
    end_row = row + dx * (word_len - 1)
    end_col = col + dy * (word_len - 1)
    return 0 <= end_row < GRID_SIZE and 0 <= end_col < GRID_SIZE

# === DRAW GRID ===
def draw_whisper_grid(slider_val):
    img_size = (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)
    img = Image.new("RGB", img_size, color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    hidden_positions = {}
    random.seed(slider_val)
    num_words = random.randint(5, 8)
    placed = 0
    attempts = 0

    while placed < num_words and attempts < 100:
        dx, dy = random.choice(DIRECTIONS)
        row = random.randint(0, GRID_SIZE - 1)
        col = random.randint(0, GRID_SIZE - 1)

        if can_place_word(row, col, dx, dy, len(HIDDEN_WORD)):
            overlap = False
            temp_positions = {}
            for i, char in enumerate(HIDDEN_WORD):
                r = row + dx * i
                c = col + dy * i
                if (r, c) in hidden_positions:
                    overlap = True
                    break
                temp_positions[(r, c)] = char
            if not overlap:
                hidden_positions.update(temp_positions)
                placed += 1
        attempts += 1

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if (i, j) in hidden_positions:
                char = hidden_positions[(i, j)]
            else:
                char = generate_char(slider_val, i, j)

            x = j * CELL_SIZE + CELL_SIZE // 5
            y = i * CELL_SIZE + CELL_SIZE // 10
            draw.text((x, y), char, font=font, fill=(0, 255, 170))

    return img

# === STREAMLIT UI ===
st.set_page_config(page_title="Whisper Grid", layout="centered", page_icon="🌿")
st.markdown("<h1 style='text-align: center; color: #00FFAA;'>Whisper Grid</h1>", unsafe_allow_html=True)
st.caption("Slider regenerates secret grid with hidden words...")

slider_val = st.slider("Change the seed", 0, 100, 50, key="slider", label_visibility="collapsed")

image = draw_whisper_grid(slider_val)
st.image(image)
