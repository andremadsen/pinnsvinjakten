import streamlit as st
import random

st.set_page_config(page_title="PinnsvinJakt 3.0", layout="centered")

# ------------------------------------------------------------
# GAME SETTINGS
# ------------------------------------------------------------
ROWS = 15
COLS = 15
NUM_MINES = 30        # antall skjulte pinnsvin
NEEDED_HITS = 5       # finn minst 5 pinnsvin
MAX_CLICKS = 10       # kun 10 klikk

# ------------------------------------------------------------
# START GAME LOGIC
# ------------------------------------------------------------
def new_game():
    mines = set()
    while len(mines) < NUM_MINES:
        r = random.randint(0, ROWS - 1)
        c = random.randint(0, COLS - 1)
        mines.add((r, c))

    st.session_state.mines = mines
    st.session_state.opened = set()
    st.session_state.hits = 0
    st.session_state.clicks = 0
    st.session_state.game_over = False
    st.session_state.win = False

# Init first time
if "mines" not in st.session_state:
    new_game()

# ------------------------------------------------------------
# MUSIC
# ------------------------------------------------------------
try:
    music = open("audio/theme.mp3", "rb").read()
    st.audio(music, format="audio/mp3", loop=True)
except:
    pass

# ------------------------------------------------------------
# COUNT ADJACENT MINES
# ------------------------------------------------------------
def count_adjacent(r, c):
    adj = 0
    for dr in (-1,0,1):
        for dc in (-1,0,1):
            if (dr,dc) != (0,0):
                nr, nc = r+dr, c+dc
                if (nr,nc) in st.session_state.mines:
                    adj += 1
    return adj

# ------------------------------------------------------------
# RIPPLE-OPEN SAFE CELLS
# ------------------------------------------------------------
def open_safe(r, c):
    """Open cell and ripple-open neighbors if safe."""
    if (r, c) in st.session_state.opened:
        return
    st.session_state.opened.add((r,c))

    if count_adjacent(r,c) == 0:
        # Open neighbors recursively
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                nr, nc = r+dr, c+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    if (nr,nc) not in st.session_state.opened and (nr,nc) not in st.session_state.mines:
                        open_safe(nr,nc)

# ------------------------------------------------------------
# CLICK HANDLING
# ------------------------------------------------------------
def handle_click(r, c):
    if st.session_state.game_over:
        return

    st.session_state.clicks += 1

    # Already opened?
    if (r,c) in st.session_state.opened:
        return

    # Hit a hedgehog
    if (r,c) in st.session_state.mines:
        st.session_state.hits += 1
        st.session_state.opened.add((r,c))

        # Win condition
        if st.session_state.hits >= NEEDED_HITS:
            st.session_state.win = True
            st.session_state.game_over = True
            return

    else:
        # Safe -> open + ripple
        open_safe(r, c)

    # Lose on max click usage
    if st.session_state.clicks >= MAX_CLICKS and not st.session_state.win:
        st.session_state.game_over = True

# ------------------------------------------------------------
# TITLE SCREEN LOGIC
# ------------------------------------------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "menu"

if st.session_state.mode == "menu":
    import os
    try:
        st.image("graphics/title_screen.png", use_column_width=True)
    except:
        st.title("PinnsvinJakt 3.0")

    st.write("Klikk for å starte!")
    if st.button("🎮 Start spillet"):
        st.session_state.mode = "game"
        st.rerun()
    st.stop()

# ------------------------------------------------------------
# GAME UI
# ------------------------------------------------------------
st.title("🦔 PinnsvinJakt – finn 5 pinnsvin på 10 klikk!")

colA, colB, colC = st.columns(3)
colA.metric("Treffede pinnsvin", st.session_state.hits)
colB.metric("Klikk igjen", MAX_CLICKS - st.session_state.clicks)
colC.metric("Pinnsvin som gjenstår", max(0, NEEDED_HITS - st.session_state.hits))

if st.button("🔄 Start nytt spill"):
    new_game()
    st.rerun()

# ------------------------------------------------------------
# GRID DISPLAY
# ------------------------------------------------------------
for r in range(ROWS):
    cols = st.columns(COLS)
    for c in range(COLS):

        key = f"{r}-{c}"

        # End of game → reveal everything
        if st.session_state.game_over:

            if (r,c) in st.session_state.mines:
                cols[c].button("🦔", key=key, disabled=True)
            elif (r,c) in st.session_state.opened:
                cols[c].button(str(count_adjacent(r,c)), key=key, disabled=True)
            else:
                cols[c].button("", key=key, disabled=True)

        else:
            # Active game
            if (r,c) in st.session_state.opened:
                # Hedgehog or safe number
                if (r,c) in st.session_state.mines:
                    cols[c].button("🦔", key=key, disabled=True)
                else:
                    cols[c].button(str(count_adjacent(r,c)), key=key, disabled=True)
            else:
                # Clickable cell
                if cols[c].button(" ", key=key):
                    handle_click(r,c)
                    st.rerun()

# ------------------------------------------------------------
# STATUS MESSAGE
# ------------------------------------------------------------
if st.session_state.game_over:
    if st.session_state.win:
        st.success("🎉 Du vant! Du fant 5 pinnsvin!")
    else:
        st.error("❌ Du brukte opp alle 10 klikk før du fant 5 pinnsvin!")
