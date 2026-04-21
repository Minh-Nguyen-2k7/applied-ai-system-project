import csv
import json
import os

# Load existing vibe descriptions so they are not wiped on re-run
existing_vibes = {}
json_path = 'data/songs.json'
if os.path.exists(json_path):
    with open(json_path, encoding='utf-8') as f:
        for song in json.load(f):
            vibe = song.get('vibe_description', '')
            if vibe:
                existing_vibes[song['id']] = vibe

# Load songs from CSV
songs = []
with open('data/songs.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        song_id = int(row['id'])
        song = {
            'id': song_id,
            'title': row['title'],
            'artist': row['artist'],
            'genre': row['genre'],
            'mood': row['mood'],
            'energy': float(row['energy']),
            'tempo_bpm': float(row['tempo_bpm']),
            'valence': float(row['valence']),
            'danceability': float(row['danceability']),
            'acousticness': float(row['acousticness']),
            'vibe_description': existing_vibes.get(song_id, ''),
        }
        songs.append(song)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(songs, f, indent=2, ensure_ascii=False)

print(f"Converted {len(songs)} songs from songs.csv to songs.json.")
