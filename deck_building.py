import streamlit as st
import random
from PIL import Image
import base64
import io

# --- Setup ---
st.set_page_config(page_title="Ghibli Deck Battle", page_icon="🎴", layout="wide")

# --- Card Definitions ---
CARD_LIBRARY = {
    "Strike": {"type": "attack", "damage": 5, "description": "Deal 5 damage."},
    "Heal": {"type": "heal", "heal": 3, "description": "Restore 3 HP."},
    "Big Strike": {"type": "attack", "damage": 8, "description": "Deal 8 damage."}
}

# --- Game State Init ---
if "player_hp" not in st.session_state:
    st.session_state.player_hp = 20
    st.session_state.player_max_hp = 20
    st.session_state.enemy_hp = 20
    st.session_state.enemy_max_hp = 20
    st.session_state.deck = ["Strike", "Strike", "Strike", "Heal", "Big Strike"]
    st.session_state.hand = []
    st.session_state.discard = []
    st.session_state.turn = 1
    st.session_state.battle_over = False
    st.session_state.message = "Battle Start! Draw cards and play."

# --- Helper Functions ---

def draw_cards(n=3):
    deck = st.session_state.deck
    random.shuffle(deck)
    for _ in range(n):
        if not deck:
            if not st.session_state.discard:
                break
            deck.extend(st.session_state.discard)
            st.session_state.discard = []
            random.shuffle(deck)
        st.session_state.hand.append(deck.pop())

def play_card(card):
    card_data = CARD_LIBRARY[card]
    if card_data["type"] == "attack":
        st.session_state.enemy_hp -= card_data["damage"]
        st.session_state.message = f"You played {card}! Enemy took {card_data['damage']} damage."
    elif card_data["type"] == "heal":
        st.session_state.player_hp = min(
            st.session_state.player_max_hp, st.session_state.player_hp + card_data["heal"]
        )
        st.session_state.message = f"You played {card}! Healed {card_data['heal']} HP."
    st.session_state.hand.remove(card)
    st.session_state.discard.append(card)

def enemy_turn():
    dmg = random.randint(2, 5)
    st.session_state.player_hp -= dmg
    st.session_state.message += f" Enemy attacks for {dmg} damage."

def check_battle_end():
    if st.session_state.enemy_hp <= 0:
        st.session_state.battle_over = True
        st.session_state.message = "🎉 You defeated the enemy!"
    elif st.session_state.player_hp <= 0:
        st.session_state.battle_over = True
        st.session_state.message = "💀 You have been defeated..."

def next_turn():
    if st.session_state.battle_over:
        return
    st.session_state.turn += 1
    draw_cards(3)
    enemy_turn()
    check_battle_end()

def reset_game():
    st.session_state.player_hp = 20
    st.session_state.enemy_hp = 20
    st.session_state.deck = ["Strike", "Strike", "Strike", "Heal", "Big Strike"]
    st.session_state.hand = []
    st.session_state.discard = []
    st.session_state.turn = 1
    st.session_state.battle_over = False
    st.session_state.message = "Battle Start! Draw cards and play."

# --- UI Layout ---
st.title("🎴 Ghibli Deck Battle")
col1, col2 = st.columns(2)

# Ghibli-style Placeholder
with col1:
    st.subheader("🌸 Your Hero")
    st.image("https://i.imgur.com/NLxH0gM.png", width=200)
    st.progress(st.session_state.player_hp / st.session_state.player_max_hp)
    st.write(f"HP: {st.session_state.player_hp}/{st.session_state.player_max_hp}")

with col2:
    st.subheader("👹 Enemy")
    st.image("https://i.imgur.com/IgWjHHt.png", width=200)
    st.progress(st.session_state.enemy_hp / st.session_state.enemy_max_hp)
    st.write(f"HP: {st.session_state.enemy_hp}/{st.session_state.enemy_max_hp}")

st.markdown("---")

# --- Card Hand ---
st.subheader(f"🧠 Turn {st.session_state.turn}")
st.write(st.session_state.message)

if not st.session_state.hand and not st.session_state.battle_over:
    draw_cards(3)

st.markdown("### 🃏 Your Hand")
card_cols = st.columns(len(st.session_state.hand) if st.session_state.hand else 1)

for i, card in enumerate(st.session_state.hand):
    with card_cols[i]:
        st.markdown(f"**{card}**")
        st.caption(CARD_LIBRARY[card]["description"])
        if st.button(f"Play {card}", key=f"play_{i}"):
            play_card(card)
            check_battle_end()

if st.button("🔁 End Turn"):
    next_turn()

if st.session_state.battle_over:
    st.success(st.session_state.message)
    if st.session_state.enemy_hp <= 0:
        st.markdown("### 💡 Choose a Reward Card")
        reward_cards = random.sample(list(CARD_LIBRARY.keys()), 2)
        rcols = st.columns(2)
        for i, card in enumerate(reward_cards):
            with rcols[i]:
                st.markdown(f"**{card}**")
                st.caption(CARD_LIBRARY[card]["description"])
                if st.button(f"Add {card}", key=f"reward_{i}"):
                    st.session_state.deck.append(card)
                    reset_game()
    else:
        if st.button("Try Again"):
            reset_game()
