import random
import base64
from pathlib import Path
from textwrap import dedent

import pandas as pd
import streamlit as st

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = Path(__file__).parent
LOGO_DIR = BASE_DIR / "logos"

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="WAR Draft", layout="wide")

# ----------------------------
# Rules modal state (FIXED)
# ----------------------------
if "show_rules" not in st.session_state:
    st.session_state.show_rules = False

def open_rules():
    st.session_state.show_rules = True

def close_rules():
    st.session_state.show_rules = False

# ----------------------------
# GLOBAL CSS (background + spacing + widgets)
# ----------------------------
st.markdown(
    dedent(
        """
        <style>
        /* Entire page background (FORCED, keep same gray) */
        html, body, [data-testid="stApp"],
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        .block-container {
          background-color: #525252 !important;
        }

        /* Reduce overall vertical whitespace */
        .block-container { padding-top: 2.6rem; padding-bottom: 1.2rem; }
        div[data-testid="stVerticalBlock"] { gap: 0.35rem; }

        /* Make labels and widgets tighter */
        label { margin-bottom: 0.05rem !important; }
        div[data-testid="stMarkdownContainer"] p { margin-bottom: 0.15rem !important; }

        /* Reduce spacing above/below widgets */
        div[data-testid="stWidget"] { margin-bottom: 0.15rem !important; }

        /* Make selectboxes a bit shorter */
        div[data-baseweb="select"] > div { min-height: 42px; }

        /* Compact success/info boxes */
        div[data-testid="stAlert"] { padding-top: 0.35rem; padding-bottom: 0.35rem; }

        /* Subheaders tighter */
        h3 { margin-bottom: 0.4rem !important; }

        /* Picked player pill */
        .picked-pill{
          display:block;
          margin: 0 0 8px 0;
          width: 100%;
          padding: 0.60rem 0.95rem;
          border-radius: 0.55rem;
          font-weight: 700;
          color: white;
          line-height: 1.2;
          border: 1px solid rgba(255,255,255,0.12);
          box-shadow: inset 0 0 0 1px rgba(0,0,0,0.15);
        }
        .picked-pill small{
          font-weight: 600;
          opacity: 0.95;
        }

        /* Make the Rules button look like a big link */
        div[data-testid="stButton"] button.rules-link{
          background: none !important;
          border: none !important;
          padding: 0 !important;
          color: #2b6cb0 !important;
          text-decoration: underline !important;
          font-size: 28px !important;
          font-weight: 700 !important;
          box-shadow: none !important;
        }
        div[data-testid="stButton"] button.rules-link:hover{
          opacity: 0.85;
        }

        /* Modal overlay + panel */
        .rules-overlay{
          position: fixed;
          top: 0; left: 0;
          width: 100vw; height: 100vh;
          background: rgba(0,0,0,0.55);
          z-index: 999999;
          display: flex;
          align-items: flex-start;
          justify-content: center;
          padding-top: 5vh;
        }
        .rules-panel{
          background: #0b1a3a;
          color: white;
          width: min(1100px, 92vw);
          border-radius: 22px;
          padding: 42px 48px 34px 48px;
          box-shadow: 0 18px 60px rgba(0,0,0,0.35);
        }
        .rules-title{
          font-size: 56px;
          font-weight: 800;
          margin: 0 0 18px 0;
        }
        .rules-text{
          font-size: 28px;
          line-height: 1.55;
          margin: 0 0 16px 0;
        }
        </style>
        """
    ),
    unsafe_allow_html=True,
)

# ----------------------------
# Title + Rules link (under title)
# ----------------------------
st.markdown('<h1 style="margin-bottom: 0.25rem;">MLB WAR Draft Faceoff</h1>', unsafe_allow_html=True)

st.button("Rules", on_click=open_rules, key="rules_open_btn", type="secondary", use_container_width=False)
# Apply the "link" styling class to the button via a tiny CSS hook:
st.markdown(
    """
    <script>
      const btn = window.parent.document.querySelector('button[kind="secondary"][data-testid="baseButton-secondary"]');
      if (btn && btn.innerText.trim() === "Rules") { btn.classList.add("rules-link"); }
    </script>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# Modal (FIXED: close button is inside Streamlit, always clickable)
# ----------------------------
if st.session_state.show_rules:
    st.markdown(
        """
        <div class="rules-overlay">
          <div class="rules-panel">
            <div class="rules-title">How to Play</div>
            <p class="rules-text">
            **REFRESH BROWSER TO CLOSE RULES BLOCK**
            </p>
            <p class="rules-text">
              -Two teams draft MLB players since 1980 from the randomly selected team above. Snake draft order.
            </p>
            <p class="rules-text">
              -The goal is to draft a player with the highest SINGLE-SEASON WAR from that team
            </p>
            <p class="rules-text">
              -Players only appear in the positional dropdown box if they played the most games at that position for that team in a single season.
            </p>
            <p class="rules-text">
              -Players that played a different position in a different season with the same team will have a different WAR at that position.
            </p>
            <p class="rules-text">
              -For example: if the team is the Phillies, putting Bryce Harper in an OF slot will produce a different WAR than the 1B slot.
            </p>
            <p class="rules-text">
              -This means there are 4 different Harpers. (Nats OF, Phillies OF, Phillies 1B, and Phillies DH)
            </p>
            <p class="rules-text">
              -If team A chooses Phillies OF Bryce Harper, Team B could still choose 1B/DH Harper.
            </p>
            <p class="rules-text">
              -Team A would still be allowed to take Nats OF Harper later in the game if the Nats are selected.
            </p>
            <p class="rules-text">
              -IMPORTANT: UTILITY SLOT
            </p>
            <p class="rules-text">
              -Any postiiton can be used in utility slot, but DH's are only eligible for the utility slot.
            </p>
            <p class="rules-text">
              -The utility slot automacailly chooses the highest WAR that player had in a season with that team, regardless of position.
            </p>
            <p class="rules-text">
              -If Team A chooses Phillies OF Bryce Harper (phillies Harper with highest WAR), team B can still put Phillies Harper in their utility slot but it will choose the highest non-OF WAR season.
            </p>
            <p class="rules-text">
              -HAVE FUN AND EXPAND YOUR BALL KNOWLEDGE
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # This renders ABOVE the page content in Streamlit's layout, so it's clickable.
    # Put it immediately after the modal HTML so it sits at the top of the page flow.
    st.button("Close rules", on_click=close_rules, key="rules_close_btn")

# ----------------------------
# Data
# ----------------------------
df = pd.read_csv("game_pool.csv")

required_cols = {"team", "slot", "player", "war"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"game_pool.csv is missing columns: {missing}")
    st.stop()

df["team"] = df["team"].astype(str).str.strip().str.lower()
df["slot"] = df["slot"].astype(str).str.strip().str.lower()
df["player"] = df["player"].astype(str).str.strip()

teams_all = sorted(df["team"].unique().tolist())

ROSTER_SLOTS = ["c", "1b", "2b", "3b", "ss", "of1", "of2", "of3", "util"]

TEAM_COLORS = {
    "nationals": "#0C2340",
    "astros": "#0C2340",
    "braves": "#CE1141",
    "padres": "#2F241D",
    "mariners": "#005C5C",
    "red_sox": "#0C2340",
    "yankees": "#0C2340",
    "mets": "#002D72",
    "phillies": "#E81828",
    "dodgers": "#005A9C",
    "giants": "#FD5A1E",
    "cubs": "#0E3386",
    "white_sox": "#27251F",
    "cardinals": "#C41E3A",
    "brewers": "#0A2351",
    "reds": "#C6011F",
    "pirates": "#FDB827",
    "guardians": "#0C2340",
    "tigers": "#0C2340",
    "royals": "#004687",
    "twins": "#002B5C",
    "rays": "#092C5C",
    "blue_jays": "#134A8E",
    "orioles": "#DF4601",
    "marlins": "#00A3E0",
    "angels": "#BA0021",
    "athletics": "#003831",
    "rangers": "#003278",
    "diamondbacks": "#A71930",
    "rockies": "#33006F",
}

def team_color(team_name: str) -> str:
    t = (team_name or "").strip().lower()
    return TEAM_COLORS.get(t, "#1F6F43")

def slot_label(slot: str) -> str:
    if slot in ["of1", "of2", "of3"]:
        return "OF"
    return slot.upper()

def ui_slot_to_data_slot(ui_slot: str) -> str:
    if ui_slot in ["of1", "of2", "of3"]:
        return "of"
    return ui_slot

def roster_total(roster: dict) -> float:
    total = 0.0
    for v in roster.values():
        if v is not None:
            total += float(v["war"])
    return total

def init_game_state():
    st.session_state.roster_a = {slot: None for slot in ROSTER_SLOTS}
    st.session_state.roster_b = {slot: None for slot in ROSTER_SLOTS}

    st.session_state.used_teams = set()
    st.session_state.round_index = 0
    st.session_state.pick_in_round = 0

    st.session_state.round_team = random.choice(teams_all)
    st.session_state.used_teams.add(st.session_state.round_team)

    st.session_state.round_used_player_slots = {}
    st.session_state.message = ""

def current_picker() -> str:
    round_index = st.session_state.round_index
    first = "A" if (round_index % 2 == 0) else "B"
    second = "B" if first == "A" else "A"
    return first if st.session_state.pick_in_round == 0 else second

def advance_pick():
    st.session_state.pick_in_round += 1
    if st.session_state.pick_in_round >= 2:
        st.session_state.pick_in_round = 0
        st.session_state.round_index += 1
        st.session_state.round_used_player_slots = {}

        remaining = [t for t in teams_all if t not in st.session_state.used_teams]
        if remaining:
            st.session_state.round_team = random.choice(remaining)
            st.session_state.used_teams.add(st.session_state.round_team)
        else:
            st.session_state.round_team = None

def round_team_df() -> pd.DataFrame:
    team = st.session_state.round_team
    if team is None:
        return df.iloc[0:0].copy()

    sub = df[df["team"] == team].copy()

    of_mask = sub["slot"].isin(["lf", "cf", "rf", "of"])
    if of_mask.any():
        sub.loc[of_mask, "slot"] = "of"

    sub = sub[sub["slot"] != "util"]

    sub["war"] = pd.to_numeric(sub["war"], errors="coerce")
    sub = sub.dropna(subset=["war", "player", "slot"])
    return sub

def player_slots_used_in_round(player: str) -> set:
    used = st.session_state.round_used_player_slots.get(player, set())
    return set(used)

def mark_used(player: str, data_slot: str):
    if player not in st.session_state.round_used_player_slots:
        st.session_state.round_used_player_slots[player] = set()
    st.session_state.round_used_player_slots[player].add(data_slot)

def roster_taken_players(roster: dict) -> set:
    return {v["player"] for v in roster.values() if v is not None}

def options_for_slot(team_df: pd.DataFrame, ui_slot: str, roster: dict) -> pd.DataFrame:
    data_slot = ui_slot_to_data_slot(ui_slot)
    taken_this_roster = roster_taken_players(roster)

    if ui_slot == "util":
        allowed = team_df.copy()
        if taken_this_roster:
            allowed = allowed[~allowed["player"].isin(taken_this_roster)]

        def best_remaining_for_player(g: pd.DataFrame) -> float:
            used_slots = player_slots_used_in_round(g.name)
            g2 = g[~g["slot"].isin(used_slots)]
            if g2.empty:
                return float("nan")
            return float(g2["war"].max())

        util = allowed.groupby("player", as_index=True).apply(best_remaining_for_player)
        util = util.dropna().sort_values(ascending=False)
        out = util.reset_index()
        out.columns = ["player", "war"]
        out["slot"] = "util"
        return out

    pool = team_df[team_df["slot"] == data_slot].copy()
    if taken_this_roster:
        pool = pool[~pool["player"].isin(taken_this_roster)]

    used_block = []
    for p, used_slots in st.session_state.round_used_player_slots.items():
        if data_slot in used_slots:
            used_block.append(p)
    if used_block:
        pool = pool[~pool["player"].isin(used_block)]

    pool["war"] = pd.to_numeric(pool["war"], errors="coerce")
    pool = pool.dropna(subset=["war"])
    best = pool.groupby("player", as_index=False)["war"].max()
    best["slot"] = data_slot
    return best.sort_values("war", ascending=False)

def apply_pick(team_letter: str, ui_slot: str, player_name: str):
    roster_key = "roster_a" if team_letter == "A" else "roster_b"
    roster = st.session_state[roster_key]

    if roster[ui_slot] is not None:
        return

    team_df = round_team_df()

    if ui_slot == "util":
        used_slots = player_slots_used_in_round(player_name)
        rows = team_df[team_df["player"] == player_name].copy()
        rows = rows[~rows["slot"].isin(used_slots)]
        if rows.empty:
            st.session_state.message = f"No remaining season available for {player_name} in UTIL."
            return

        best_row = rows.sort_values("war", ascending=False).iloc[0]
        chosen_war = float(best_row["war"])
        chosen_data_slot = str(best_row["slot"])

        roster[ui_slot] = {
            "player": player_name,
            "war": chosen_war,
            "source_slot": chosen_data_slot,
            "team": st.session_state.round_team,
        }
        st.session_state[roster_key] = roster

        mark_used(player_name, chosen_data_slot)
        st.session_state.message = f"Team {team_letter} drafted {player_name} in UTIL for {chosen_war:.1f} WAR."
        advance_pick()
        st.rerun()

    else:
        data_slot = ui_slot_to_data_slot(ui_slot)
        used_slots = player_slots_used_in_round(player_name)
        if data_slot in used_slots:
            st.session_state.message = f"{player_name} at {data_slot.upper()} is already taken this round."
            return

        rows = team_df[(team_df["slot"] == data_slot) & (team_df["player"] == player_name)].copy()
        if rows.empty:
            st.session_state.message = f"No data found for {player_name} at {data_slot.upper()}."
            return

        chosen_war = float(pd.to_numeric(rows["war"], errors="coerce").max())

        roster[ui_slot] = {
            "player": player_name,
            "war": chosen_war,
            "source_slot": data_slot,
            "team": st.session_state.round_team,
        }
        st.session_state[roster_key] = roster

        mark_used(player_name, data_slot)
        st.session_state.message = f"Team {team_letter} drafted {player_name} at {data_slot.upper()} for {chosen_war:.1f} WAR."
        advance_pick()
        st.rerun()

if "roster_a" not in st.session_state:
    init_game_state()

top_left, top_right = st.columns([3, 1], gap="small")

with top_left:
    team = st.session_state.round_team

    if team:
        logo_path = LOGO_DIR / f"{team}.png"
        if logo_path.exists():
            b64 = base64.b64encode(logo_path.read_bytes()).decode()
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:14px;">
                  <div style="font-size:32px; font-weight:700; white-space:nowrap;">
                    Selected team:
                  </div>
                  <img src="data:image/png;base64,{b64}" style="height:72px; width:auto; display:block;" />
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.subheader(f"Selected team: {team}")
    else:
        st.subheader("Selected team: none")

    st.caption(
        f"Round: {st.session_state.round_index + 1}   "
        f"Pick: {st.session_state.pick_in_round + 1} of 2   "
        f"On the clock: Team {current_picker()}"
    )

with top_right:
    if st.button("reset game"):
        init_game_state()
        st.rerun()

if st.session_state.message:
    st.info(st.session_state.message)

team_df = round_team_df()
on_clock = current_picker()

colA, colB = st.columns(2, gap="medium")

def render_team(letter: str, roster_key: str):
    roster = st.session_state[roster_key]
    total = roster_total(roster)
    st.subheader(f"TEAM {letter}  •  Total WAR: {total:.1f}")

    is_active = (letter == on_clock) and (st.session_state.round_team is not None)

    for ui_slot in ROSTER_SLOTS:
        left, right = st.columns([1, 9], gap="small")

        with left:
            st.markdown(f"**{slot_label(ui_slot)}**")

        current = roster[ui_slot]
        with right:
            if current is None:
                if not is_active:
                    st.selectbox(
                        "Pick",
                        options=["—"],
                        key=f"{roster_key}_{ui_slot}_inactive",
                        label_visibility="collapsed",
                        disabled=True,
                    )
                else:
                    opts = options_for_slot(team_df, ui_slot, roster)
                    if opts.empty:
                        st.caption("No options for this slot on this team.")
                    else:
                        names = opts["player"].tolist()
                        choice = st.selectbox(
                            "Pick",
                            options=["—"] + names,
                            key=f"{roster_key}_{ui_slot}_pick",
                            label_visibility="collapsed",
                        )
                        if choice != "—":
                            apply_pick(letter, ui_slot, choice)
            else:
                war_val = float(current["war"])
                picked_team = current.get("team", "")
                bg = team_color(picked_team)
                st.markdown(
                    f"""
                    <div class="picked-pill" style="background:{bg};">
                      {current["player"]} <small>• {war_val:.1f} WAR</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

with colA:
    render_team("A", "roster_a")
with colB:
    render_team("B", "roster_b")

done_a = all(st.session_state.roster_a[s] is not None for s in ROSTER_SLOTS)
done_b = all(st.session_state.roster_b[s] is not None for s in ROSTER_SLOTS)

if done_a and done_b:
    st.divider()
    total_a = roster_total(st.session_state.roster_a)
    total_b = roster_total(st.session_state.roster_b)
    winner = "TEAM A" if total_a > total_b else ("TEAM B" if total_b > total_a else "TIE")
    st.header(f"Winner: {winner}")
    st.subheader(f"Team A total WAR: {total_a:.1f}")
    st.subheader(f"Team B total WAR: {total_b:.1f}")


