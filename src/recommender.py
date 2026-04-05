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
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of song dicts with typed fields."""
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
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
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    # TODO: Implement scoring logic using your Algorithm Recipe from Phase 2.
    # Expected return format: (score, reasons)
    return []

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song against user_prefs using weighted genre/mood/energy/tempo and return the top k."""
    # Weights
    W_GENRE  = 0.4
    W_MOOD   = 0.3
    W_ENERGY = 0.2
    W_TEMPO  = 0.1

    # Min-Max tempo bounds derived from the catalog
    TEMPO_MIN = 60.0
    TEMPO_MAX = 160.0

    # Normalize the user's target tempo (if provided) to 0-1
    u_tempo_norm = (user_prefs.get("tempo_bpm", 110.0) - TEMPO_MIN) / (TEMPO_MAX - TEMPO_MIN)

    scored = []
    for song in songs:
        reasons = []

        # Genre match (categorical: 0 or 1)
        genre_match = 1.0 if song["genre"] == user_prefs.get("genre", "") else 0.0
        if genre_match:
            reasons.append(f"genre match (+{W_GENRE:.1f})")
        else:
            reasons.append(f"genre mismatch (+0.0)")

        # Mood match (categorical: 0 or 1)
        mood_match = 1.0 if song["mood"] == user_prefs.get("mood", "") else 0.0
        if mood_match:
            reasons.append(f"mood match (+{W_MOOD:.1f})")
        else:
            reasons.append(f"mood mismatch (+0.0)")

        # Energy similarity (1 - abs difference, so closer = higher)
        energy_sim = 1.0 - abs(song["energy"] - user_prefs.get("energy", 0.5))
        reasons.append(f"energy similarity {energy_sim:.2f} (+{W_ENERGY * energy_sim:.2f})")

        # Tempo similarity: normalize song tempo then compare
        tempo_norm = (song["tempo_bpm"] - TEMPO_MIN) / (TEMPO_MAX - TEMPO_MIN)
        tempo_sim = 1.0 - abs(tempo_norm - u_tempo_norm)
        reasons.append(f"tempo similarity {tempo_sim:.2f} (+{W_TEMPO * tempo_sim:.2f})")

        # Weighted final score
        score = (W_GENRE  * genre_match
               + W_MOOD   * mood_match
               + W_ENERGY * energy_sim
               + W_TEMPO  * tempo_sim)

        explanation = ", ".join(reasons)
        scored.append((song, score, explanation))

    # Sort highest score first, return top k
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
