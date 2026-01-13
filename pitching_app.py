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
st.set_page_config(page_title="Pitching WAR Draft", layout="wide")

# ----------------------------
# Rules dialog state
# ----------------------------
if "show_rules_p" not in st.session_state:
    st.session_state.show_rules_p = False


def open_rules():
    st.session_state.show_rules_p = True


@st.dialog("How to Play")
def rules_dialog():
    st.markdown(
        """
Two teams draft pitchers from the randomly selected team above. Snake draft order.

The goal is to draft a pitcher with the highest SINGLE SEASON WAR from that team.

Pitchers who played for multiple teams can be drafted multiple times across the game if the team changes.
Example: Nationals Max Scherzer is different from Tigers Max Scherzer.

No utility slot.
Each team drafts 7 pitchers.
        """
    )

    if st.button("Close", key="rules_close_btn_p"):
        st.session_state.show_rules_p = False
        st.rerun()


# ----------------------------
# GLOBAL CSS (same look)
# ----------------------------
st.markdown(
    dedent(
        """
        <style>
        html, body, [data-testid="stApp"],
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        .block-container {
          background-color: #525252 !important;
        }

        .block-container { padding-top: 2.6rem; padding-bottom: 1.2rem; }
        div[data-testid="stVerticalBlock"] { gap: 0.35rem; }

        label { margin-bottom: 0.05rem !important; }
        div[data-testid="stMarkdownContainer"] p { margin-bottom: 0.15rem !important; }

        div[data-testid="stWidget"] { margin-bottom: 0.15rem !important; }

        div[data-baseweb="select"] > div { min-height: 42px; }

        div[data-testid="stAlert"] { padding-top: 0.35rem; padding-bottom: 0.35rem; }

        h3 { margin-bottom: 0.4rem !important; }

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
        </style>
        """
    ),
    unsafe_allow_html=True,
)

# ----------------------------
# Title + Rules button
# ----------------------------
st.markdown('<h1 style="margin-bottom: 0.25rem;">MLB Pitching WAR Draft Faceoff</h1>', unsafe_allow_html=True)

st.button("Rules", on_click=open_rules, key="rules_open_btn_p", use_container_width=False)
if st.session_state.show_rules_p:
    rules_dialog()

# ----------------------------
# Data
# ----------------------------
df = pd.read_csv("pitch_game_pool.csv")

required_cols = {"team", "player", "war"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"pitch_game_pool.csv is missing columns: {missing}")
    st.stop()

df["team"] = df["team"].astype(str).str.strip().str.lower()
df["player"] = df["player"].astype(str).str.strip()
df["war"] = pd.to_numeric(df["war"], errors="coerce")
df = df.dropna(subset=["team", "player", "war"])

teams_all = sorted(df["team"].unique().tolist())

PITCH_SLOTS = ["p1", "p2", "p3", "p4", "p5", "p6", "p7"]

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


def roster_total(roster: dict) -> float:
    total = 0.0
    for v in roster.values():
        if v is not None:
            total += float(v["war"])
    return total


def init_game_state():
    st.session_state.roster_a = {slot: None for slot in PITCH_SLOTS}
    st.session_state.roster_b = {slot: None for slot in PITCH_SLOTS}

    st.session_state.used_teams = set()
    st.session_state.round_index = 0
    st.session_state.pick_in_round = 0

    st.session_state.round_team = random.choice(teams_all)
    st.session_state.used_teams.add(st.session_state.round_team)

    # block drafting the same pitcher from the same team within the round
    st.session_state.round_used_players = set()

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
        st.session_state.round_used_players = set()

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
    return df[df["team"] == team].copy()


def roster_taken_keys(roster: dict) -> set:
    return {(v["player"], v.get("team")) for v in roster.values() if v is not None}


def options_for_slot(team_df: pd.DataFrame, roster: dict) -> pd.DataFrame:
    taken_keys = roster_taken_keys(roster)

    pool = team_df.copy()

    # remove already drafted (player, team) from this roster
    if taken_keys:
        pool = pool[~pool.apply(lambda r: (r["player"], r["team"]) in taken_keys, axis=1)]

    # remove players already taken this round by either team
    if st.session_state.round_used_players:
        pool = pool[~pool["player"].isin(st.session_state.round_used_players)]

    # one row per player, best WAR already in your CSV, but we max again just in case
    best = pool.groupby("player", as_index=False)["war"].max()
    return best.sort_values("war", ascending=False)


def apply_pick(team_letter: str, ui_slot: str, player_name: str):
    roster_key = "roster_a" if team_letter == "A" else "roster_b"
    roster = st.session_state[roster_key]

    if roster[ui_slot] is not None:
        return

    team_df = round_team_df()
    rows = team_df[team_df["player"] == player_name].copy()
    if rows.empty:
        st.session_state.message = f"No data found for {player_name}."
        return

    chosen_war = float(rows["war"].max())

    roster[ui_slot] = {
        "player": player_name,
        "war": chosen_war,
        "team": st.session_state.round_team,
    }
    st.session_state[roster_key] = roster

    st.session_state.round_used_players.add(player_name)

    st.session_state.message = f"Team {team_letter} drafted {player_name} for {chosen_war:.1f} WAR."
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


def slot_label(slot: str) -> str:
    return slot.upper()


def render_team(letter: str, roster_key: str):
    roster = st.session_state[roster_key]
    total = roster_total(roster)
    st.subheader(f"TEAM {letter}  •  Total WAR: {total:.1f}")

    is_active = (letter == on_clock) and (st.session_state.round_team is not None)

    for ui_slot in PITCH_SLOTS:
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
                    opts = options_for_slot(team_df, roster)
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

done_a = all(st.session_state.roster_a[s] is not None for s in PITCH_SLOTS)
done_b = all(st.session_state.roster_b[s] is not None for s in PITCH_SLOTS)

if done_a and done_b:
    st.divider()
    total_a = roster_total(st.session_state.roster_a)
    total_b = roster_total(st.session_state.roster_b)
    winner = "TEAM A" if total_a > total_b else ("TEAM B" if total_b > total_a else "TIE")
    st.header(f"Winner: {winner}")
    st.subheader(f"Team A total WAR: {total_a:.1f}")
    st.subheader(f"Team B total WAR: {total_b:.1f}")
