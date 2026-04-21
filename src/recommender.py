from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    vibe_description: str = ""

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score all songs against the user profile and return the top k Songs."""
        prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }
        scored = [(song, score_song(prefs, vars(song))[0]) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable string explaining why a song was recommended."""
        prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }
        score, reasons = score_song(prefs, vars(song))
        return f"Score {score:.2f} — " + ", ".join(reasons)

    def explain_top_k_reasoning(self, user: UserProfile, k: int = 5) -> str:
        """Return a detailed explanation of why the top K songs were selected.

        Shows comparative reasoning and score deltas between ranked songs.
        """
        prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }

        scored = []
        for song in self.songs:
            score, reasons = score_song(prefs, vars(song))
            scored.append((song, score, reasons))
        scored.sort(key=lambda x: x[1], reverse=True)
        top_k = scored[:k]

        explanation = f"\n{'=' * 70}\nREASONING FOR TOP {k} RECOMMENDATIONS\n{'=' * 70}\n"
        explanation += f"User Profile: {prefs['mood'].upper()} mood, {prefs['genre'].upper()} genre, energy {prefs['energy']:.1f}\n\n"

        for rank, (song, score, reasons) in enumerate(top_k, start=1):
            explanation += f"#{rank} — {song.title} by {song.artist}\n"
            explanation += f"   Score: {score:.3f}\n"
            explanation += f"   Why: {', '.join(reasons)}\n"

            if rank > 1:
                prev_song, prev_score, _ = top_k[rank - 2]
                delta = score - prev_score
                explanation += f"   Advantage over #{rank - 1}: +{delta:.3f} points\n"

            explanation += "\n"

        return explanation

_semantic_model = None


def get_semantic_model():
    """Load the sentence transformer model lazily for genre and mood similarity."""
    global _semantic_model
    if _semantic_model is not None:
        return _semantic_model
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None

    _semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _semantic_model


def semantic_text_similarity(a: str, b: str) -> float:
    """Return a cosine similarity score in [0, 1] for two text values."""
    if a == b:
        return 1.0

    model = get_semantic_model()
    if model is None:
        return 0.0

    import numpy as np
    embeddings = model.encode([a, b], normalize_embeddings=True)
    similarity = float(np.dot(embeddings[0], embeddings[1]))
    return max(0.0, min(1.0, similarity))


def get_default_weights() -> Dict[str, float]:
    return {
        "genre": 0.4,
        "mood": 0.3,
        "energy": 0.2,
        "tempo": 0.1,
    }


def get_openai_client():
    try:
        from dotenv import load_dotenv
        load_dotenv()  # Load .env file if it exists
    except ImportError:
        pass

    try:
        import openai
    except ImportError:
        return None

    import os
    if not getattr(openai, "api_key", None):
        openai.api_key = os.getenv("OPENAI_API_KEY", "")

    return openai if openai.api_key else None


def parse_weights_from_text(raw_text: str) -> Optional[Dict[str, float]]:
    import json
    import re

    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        return None

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None

    weights: Dict[str, float] = {}
    for key in ["genre", "mood", "energy", "tempo"]:
        if key not in data:
            return None
        try:
            weights[key] = float(data[key])
        except (TypeError, ValueError):
            return None

    total = sum(weights.values())
    if total <= 0:
        return None

    return {key: weights[key] / total for key in weights}


def get_dynamic_weights(user_prefs: Dict, song: Dict) -> Dict[str, float]:
    openai_client = get_openai_client()
    if openai_client is None:
        return get_default_weights()

    prompt = (
        f"User wants {user_prefs.get('mood', 'a neutral')} mood. "
        f"Song is described as {song.get('vibe_description', '').strip() or 'a song with no description'}. "
        "On a scale of 0.0 to 1.0, what should the weights for Genre, Mood, Energy, and Tempo be? "
        "Ensure they sum to 1.0. Output JSON only with keys genre, mood, energy, tempo."
    )

    try:
        response = openai_client.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a music recommendation weighting assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=120,
        )
        text = response["choices"][0]["message"]["content"]
        weights = parse_weights_from_text(text)
        if weights is not None:
            return weights
    except Exception:
        pass

    return get_default_weights()


def load_songs(json_path: str) -> List[Dict]:
    """Read songs.json and return a list of song dicts with typed fields."""
    import json

    songs = []
    with open(json_path, encoding="utf-8") as f:
        raw_songs = json.load(f)

    for row in raw_songs:
        songs.append({
            "id": int(row["id"]),
            "title": row["title"],
            "artist": row["artist"],
            "genre": row["genre"],
            "mood": row["mood"],
            "energy": float(row["energy"]),
            "tempo_bpm": float(row["tempo_bpm"]),
            "valence": float(row["valence"]),
            "danceability": float(row["danceability"]),
            "acousticness": float(row["acousticness"]),
            "vibe_description": row.get("vibe_description", ""),
        })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a single song against user_prefs and return (score, reasons).

    This uses LLM-generated dynamic weights and semantic similarity for genre/mood.
    """
    TEMPO_MIN = 60.0
    TEMPO_MAX = 160.0

    reasons = []

    weights = get_dynamic_weights(user_prefs, song)
    W_GENRE = weights["genre"]
    W_MOOD = weights["mood"]
    W_ENERGY = weights["energy"]
    W_TEMPO = weights["tempo"]
    reasons.append(
        f"dynamic weights genre={W_GENRE:.2f} mood={W_MOOD:.2f} "
        f"energy={W_ENERGY:.2f} tempo={W_TEMPO:.2f}"
    )

    genre_sim = semantic_text_similarity(song["genre"], user_prefs.get("genre", ""))
    reasons.append(f"genre similarity {genre_sim:.2f} (+{W_GENRE * genre_sim:.2f})")

    mood_sim = semantic_text_similarity(song["mood"], user_prefs.get("mood", ""))
    reasons.append(f"mood similarity {mood_sim:.2f} (+{W_MOOD * mood_sim:.2f})")

    energy_sim = 1.0 - abs(song["energy"] - user_prefs.get("energy", 0.5))
    reasons.append(f"energy similarity {energy_sim:.2f} (+{W_ENERGY * energy_sim:.2f})")

    u_tempo_norm = (user_prefs.get("tempo_bpm", 110.0) - TEMPO_MIN) / (TEMPO_MAX - TEMPO_MIN)
    tempo_norm = (song["tempo_bpm"] - TEMPO_MIN) / (TEMPO_MAX - TEMPO_MIN)
    tempo_sim = 1.0 - abs(tempo_norm - u_tempo_norm)
    reasons.append(f"tempo similarity {tempo_sim:.2f} (+{W_TEMPO * tempo_sim:.2f})")

    score = (W_GENRE * genre_sim + W_MOOD * mood_sim
           + W_ENERGY * energy_sim + W_TEMPO * tempo_sim)
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song against user_prefs using weighted genre/mood/energy/tempo and return the top k."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, ", ".join(reasons)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
