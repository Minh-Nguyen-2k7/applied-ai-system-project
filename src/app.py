import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from recommender import load_songs, recommend_songs

DATA_PATH = Path(__file__).parent.parent / "data" / "songs.json"

GENRES = sorted([
    "Acoustic Pop", "Afrobeats", "Alternative", "Ambient", "Beatbox",
    "Blues", "Bossa Nova", "Celtic", "Chillhop", "City Pop",
    "Classical", "Country", "Dark Ambient", "Drill", "Drum And Bass",
    "EDM", "Electronic", "Emo", "Folk", "Future Bass",
    "Gospel", "Hip-Hop", "Indie Pop", "Indie Rock", "J-Pop",
    "Jazz", "K-Pop", "Latin", "Lofi", "Metal",
    "Minecraft Lofi", "New Age", "Nightcore", "OST", "Phonk",
    "Pop", "Post-Rock", "R&B", "Reggae", "Rock",
    "Soul", "Study", "Synthwave", "Trance", "Trap",
    "V-Pop", "Vocaloid",
])

MOODS = sorted([
    "Aggressive", "Chill", "Confident", "Contemplative", "Euphoric",
    "Focused", "Happy", "Intense", "Melancholic", "Moody",
    "Nostalgic", "Peaceful", "Relaxed", "Sensual",
])


@st.cache_data
def get_songs():
    return load_songs(str(DATA_PATH))


st.set_page_config(page_title="Mood Constructor", page_icon="🎵", layout="wide")

st.title("🎵 Mood Constructor")
st.caption(
    "Hybrid music recommendations powered by semantic text similarity "
    "and LLM-generated dynamic weights."
)

st.sidebar.header("Your Preferences")
genre = st.sidebar.selectbox("Favorite Genre", GENRES, index=GENRES.index("Pop"))
mood = st.sidebar.selectbox("Mood", MOODS, index=MOODS.index("Happy"))
energy = st.sidebar.slider(
    "Target Energy", 0.0, 1.0, 0.7, step=0.05,
    help="0 = very calm and mellow · 1 = very high-energy and intense",
)
k = st.sidebar.slider("Number of Recommendations", 1, 10, 5)
run = st.sidebar.button("Get Recommendations", type="primary", use_container_width=True)

songs = get_songs()

if run:
    user_prefs = {"genre": genre.lower(), "mood": mood.lower(), "energy": energy, "tempo_bpm": 110.0}

    with st.spinner("Scoring songs against your preferences..."):
        results = recommend_songs(user_prefs, songs, k=k)

    st.subheader(f"Top {len(results)} picks for: {mood} · {genre} · energy {energy:.2f}")

    for rank, (song, score, reasons) in enumerate(results, start=1):
        with st.container(border=True):
            left, right = st.columns([4, 1])
            with left:
                st.markdown(f"**#{rank} — {song['title']}** &nbsp; *by {song['artist']}*")
                st.caption(
                    f"{song['genre'].title()} · {song['mood'].title()} · "
                    f"Energy {song['energy']:.2f} · {song['tempo_bpm']:.0f} BPM"
                )
                st.write(song["vibe_description"])
            with right:
                st.metric("Match Score", f"{score:.3f}")

            with st.expander("Score breakdown"):
                for part in reasons.split(", "):
                    st.text(f"  {part}")
else:
    st.info("Set your preferences in the sidebar and click **Get Recommendations** to begin.")

    with st.expander("Browse all songs in the catalog"):
        for song in songs:
            st.write(
                f"**{song['title']}** by {song['artist']} "
                f"— {song['genre']} · {song['mood']} · energy {song['energy']:.2f}"
            )
