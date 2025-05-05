import streamlit as st
import random
from PIL import Image

# --- Streamlit setup ---
st.set_page_config(page_title="Ghibli Deck Battle", page_icon="🎴", layout="centered")

# --- Game Data ---
CARD_LIBRARY = {
    "Strike": {"type": "attack", "damage": 5, "description": "Deal 5 damage."},
    "Heal": {"type": "heal", "heal": 3, "description": "Restore 3 HP."},
    "Big Strike": {"type": "attack", "damage": 8, "description": "Deal 8 damage."}
}

ENEMIES = {
    "Battle 1": {"name": "Fuzzy Beast", "hp": 15, "img": "https://i.imgur.com/kJvBvgG.png"},
    "Battle 2": {"name": "Snail Slime", "hp": 20, "img": "https://i.imgur.com/MclAdVR.png"},
    "Battle 3": {"name": "Stone Golem", "hp": 25, "img": "https://i.imgur.com/DZ8UXLs.png"}
}

# --- Initialize session state ---
if "screen" not in st.session_state:
    st.session_state.screen = "map"
    st.session_state.player_hp = 20
    st.session_state.max_hp = 20
    st.session_state.deck = ["Strike", "Strike", "Strike", "Heal", "Big Strike"]
    st.session_state.hand = []
    st.session_state.discard = []
    st.session_state.enemy = None
    st.session_state.enemy_hp = 0
    st.session_state.enemy_max_hp = 0
    st.session_state.battle_message = ""
    st.session_state.victory = False

# --- Helper functions ---
def draw_cards(n=3):
    deck = st.session_state.deck
    random.shuffle(deck)
    for _ in range(n):
        if not deck:
            deck.extend(st.session_state.discard)
            st.session_state.discard.clear()
            random.shuffle(deck)
        if deck:
            st.session_state.hand.append(deck.pop())

def play_card(card):
    data = CARD_LIBRARY[card]
    if data["type"] == "attack":
        st.session_state.enemy_hp -= data["damage"]
        st.session_state.battle_message = f"You played {card}, dealt {data['damage']} damage!"
    elif data["type"] == "heal":
        st.session_state.player_hp = min(st.session_state.max_hp, st.session_state.player_hp + data["heal"])
        st.session_state.battle_message = f"You played {card}, healed {data['heal']} HP!"
    st.session_state.hand.remove(card)
    st.session_state.discard.append(card)

def enemy_turn():
    dmg = random.randint(2, 5)
    st.session_state.player_hp -= dmg
    st.session_state.battle_message += f" Enemy hits for {dmg} damage!"

def check_battle_end():
    if st.session_state.enemy_hp <= 0:
        st.session_state.victory = True
        st.session_state.battle_message = "🎉 You defeated the enemy!"
    elif st.session_state.player_hp <= 0:
        st.session_state.battle_message = "💀 You died!"
        st.session_state.screen = "map"  # Reset to map

def start_battle(name):
    enemy = ENEMIES[name]
    st.session_state.screen = "battle"
    st.session_state.enemy = enemy
    st.session_state.enemy_hp = enemy["hp"]
    st.session_state.enemy_max_hp = enemy["hp"]
    st.session_state.hand = []
    st.session_state.discard = []
    st.session_state.victory = False
    draw_cards(3)

def reset_to_map():
    st.session_state.screen = "map"
    st.session_state.enemy = None
    st.session_state.enemy_hp = 0
    st.session_state.hand = []
    st.session_state.discard = []
    st.session_state.battle_message = ""
    st.session_state.victory = False

# --- UI Screens ---

# 🎯 MAP SCREEN
if st.session_state.screen == "map":
    st.title("🎴 Ghibli Deck Battle")
    map_img = Image.open("map.png")
    st.image(map_img, use_column_width=True)
    st.subheader("🗺️ Choose a Battle")

    cols = st.columns(3)
    for i, (battle_name, data) in enumerate(ENEMIES.items()):
        with cols[i]:
            if st.button(battle_name):
                start_battle(battle_name)

# ⚔️ BATTLE SCREEN
elif st.session_state.screen == "battle":
    st.title("⚔️ Battle: " + st.session_state.enemy["name"])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🌸 You")
        st.progress(st.session_state.player_hp / st.session_state.max_hp)
        st.write(f"HP: {st.session_state.player_hp}/{st.session_state.max_hp}")

    with col2:
        st.subheader("👹 Enemy")
        st.image(st.session_state.enemy["img"], width=150)
        st.progress(st.session_state.enemy_hp / st.session_state.enemy_max_hp)
        st.write(f"HP: {st.session_state.enemy_hp}/{st.session_state.enemy_max_hp}")

    st.markdown("---")
    st.write(st.session_state.battle_message)

    if st.session_state.victory:
        st.success("🎉 You won! Choose a card to add:")
        reward_cards = random.sample(list(CARD_LIBRARY.keys()), 2)
        cols = st.columns(2)
        for i, card in enumerate(reward_cards):
            with cols[i]:
                st.markdown(f"**{card}**")
                st.caption(CARD_LIBRARY[card]["description"])
                if st.button(f"Add {card}", key=f"reward_{card}"):
                    st.session_state.deck.append(card)
                    reset_to_map()
    elif st.session_state.player_hp <= 0:
        st.error("💀 You lost! Back to map.")
        if st.button("Continue"):
            reset_to_map()
    else:
        # Hand
        st.markdown("### 🃏 Your Hand")
        hand_cols = st.columns(len(st.session_state.hand) or 1)
        for i, card in enumerate(st.session_state.hand):
            with hand_cols[i]:
                st.markdown(f"**{card}**")
                st.caption(CARD_LIBRARY[card]["description"])
                if st.button(f"Play {card}", key=f"play_{i}"):
                    play_card(card)
                    check_battle_end()
        if st.button("🔁 End Turn"):
            draw_cards(3)
            enemy_turn()
            check_battle_end()
