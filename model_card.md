# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

MoodConstructor v1.2.3.4
---

## 2. Intended Use  

- This recommender will create a list of suggested songs that should fit to the user's need based on their personal song interest.
- Specifically, the recommender is based on the user's preferred genre, mood, energy and tempo
- This is just a sample, classroom exploration of how a typical song recommender would work.
---

## 3. How the Model Works  

- The recommender looks at four features of each song: genre, mood, energy level, and tempo. The user tells the system what genre and mood they prefer, how energetic they want the music to feel (on a scale of 0 to 1), and optionally a target tempo. For each song in the catalog, the system checks how well it matches those preferences and produces a single score between 0 and 1. Genre and mood are treated as yes-or-no matches — either the song fits or it does not. Energy is compared as a distance — the closer the song's energy is to what the user wants, the higher it scores. Tempo is normalized across the catalog before comparing, so a slow song and a fast song are judged fairly. The four scores are then combined using weights — genre counts the most (40%), followed by mood (30%), energy (20%), and tempo (10%). Songs are ranked from highest to lowest score, and the top five are returned as recommendations.

---

## 4. Data  
  
- The catalog contains 18 songs loaded from a CSV file. Genres represented include pop, lofi, rock, classical, hip-hop, blues, acoustic, and synth.
- Moods include happy, chill, intense, sad, and romantic. No songs were added or removed from the original dataset. Musical styles that are missing or underrepresented include R&B, jazz, country, and Latin — meaning users who prefer those genres will rarely get a genre match and receive weaker recommendations overall.

---

## 5. Strengths  

- The system works best for users whose preferences clearly match a well-represented genre in the catalog — particularly pop, lofi, and rock. For those profiles, the top results scored above 0.95 and felt intuitive. The scoring also captures energy level well: a user who wants high-energy music consistently receives songs with energy values close to their target. The explanation output for each recommendation is a strength too — every result shows exactly which features matched and how much each contributed to the score, making the system fully transparent.
---

## 6. Limitations and Bias 

- The genre weight (0.4) creates a filter bubble. Because genre is the single heaviest factor in the score, the system almost always returns songs from the same genre the user already prefers — even when a song from a different genre matches their energy and mood far better. The system cannot reward a song for being "close" in genre (like indie-pop vs pop); it only sees a match or a complete miss. This design makes the users with cross-genre tastes have problems finding their best song recommendations, and this also force a user to stick to what they are used to rather than helping them discover new genre they never tried.

---

## 7. Evaluation  

- I tested five user profiles to evaluate how the recommender behaved across different situations. Three were realistic profiles — High-Energy Pop, Chill Lofi, and Deep Intense Rock — and two were edge cases designed to stress-test the scoring logic. 
- For the realistic profiles, the top results matched my expectations for the design: the correct genre and mood songs ranked highest, with scores above 0.95 in most cases. The most surprising result came from the "Conflicting: Lofi + High Energy" profile, where the system returned lofi songs in the top 3 even though none of them matched the requested energy level, which shows how genre dominates the score. 
- I also ran a weight experiment where I halved the genre weight (0.4 → 0.2) and doubled the energy level (0.2 → 0.4), which caused cross-genre songs with strong energy matches to surface higher in the rankings. 
- This makes me confirmed that the weights directly control how "open" or "narrow" the recommendations feel, and that no single weight setting is objectively correct — it depends on what the user values most.

---

## 8. Future Work  

- Allowing adjacent genres to receive a small score instead of zero.
- Use the unused `likes_acoustic` field in the scoring so acoustic preference actually influences results.
- Add a diversity rule so the same artist cannot appear more than once in the top 5.
- Expand the catalog, since 18 songs are too small for meaningful recommendations across many profiles.

---

## 9. Personal Reflection  

- Building this recommender makes me realize how hard it is for a recommender to truly capture the next recommender song for new user. The scoring systems are actually way harder than complex than I expected. Also users can have very weird preferences, such as a high-energy lofi song. Perhaps real apps like Spotify also have certain tradeoffs when they use many weighted scores, and they reflect the people's idea who built the system - not some objective truth about what music is good.

---
## THIS IS AFTER THE NEW IMPROVEMENT ON THE ORIGINAL MUSIC RECOMMENDER

## 10. Limitations and Biases

- **Small and subjective catalog.** With only 50 songs, the system cannot meaningfully serve users with niche tastes. Any genre with fewer than two or three entries will consistently produce weak recommendations, not because the scoring is broken but because there simply is not enough data to match against. The catalog also reflects one curator's taste — genres like Latin, Celtic, or Vocaloid are represented by a single song each, which creates an uneven playing field.
- **Filter bubble by design.** Genre carries a 40% weight by default, which means the system pushes users toward what they already know. Someone who listens to pop will almost always see pop songs at the top, even if a song from another genre matches their energy and mood better. This is the same filter bubble problem that real platforms like Spotify have been criticized for.
- **Vibe descriptions are hand-written opinions.** The natural language descriptions used by the LLM to reason about each song were written manually. They reflect one person's interpretation of what each song sounds like, not any objective musical analysis. If the description is misleading, the LLM will generate weights based on wrong context and the recommendation score for that song will be skewed.
- **Genre and mood labels are lossy.** A single word like "chill" or "ambient" cannot fully describe how a song feels. Two songs can share the same mood label and sound completely different, but the system treats them as identical in that dimension. This is a fundamental limit of the categorical approach.

---

## 11. Potential Misuse and Prevention

- **Misuse scenario.** While a 50-song classroom recommender is harmless on its own, the same architecture — weighted scoring, LLM-driven context, vibe descriptions — could be used at scale to deliberately push users toward certain artists, labels, or content. A bad vibe descriptions can artificially inflate scores for specific songs regardless of whether they actually match the user's preferences. The LLM trusts whatever description it receives without any fact-checking.
- **Prevention.** For a production system, vibe descriptions should be generated from objective audio features (tempo, key, spectral content) rather than freeform text, so they cannot be manually input with bad intentions. The scoring weights should also be audited regularly to check whether the system is systematically over-recommending any particular artist or genre — the same diversity check that streaming platforms use internally. For this project specifically, the catalog is too small and too controlled for this to be a real risk.

---

## 12. What Surprised Me While Testing Reliability

- **The system worked fine without the LLM.** The most surprising result from testing was that the recommendations were still reasonable even though the OpenAI API key was never actually active — every run used the fallback static weights (0.4 / 0.3 / 0.2 / 0.1). I expected the output to feel noticeably worse without the dynamic weights, but the semantic similarity component was doing enough work on its own that the results still felt meaningful. This made me realize the LLM feature is an enhancement, not a foundation.
- **A placeholder looked like a real key.** During interactive testing, the terminal printed `✓ API Key loaded: sk-key-here...` — which appeared to confirm the LLM was active. In reality, the `.env` file contained a placeholder string (`sk-key-here`) that the system accepted as a valid key because it was non-empty. The OpenAI call then silently failed and fell back to defaults. The system gave no error and behaved exactly as if everything was working. This was a reliability blind spot: the code had a guardrail for a missing key but not for a fake one.
- **Nonsense input produced silent results.** Before adding input validation, entering an unrecognized genre like "banana" or "asdfg" would cause the system to run without any warning. It would return songs with low but non-zero scores because the sentence-transformer still computed some similarity value. The output looked legitimate, which made the bad input invisible.

---

## 13. Collaboration with AI

- **How AI was used.** Throughout this project, an AI assistant (Claude) was used for implementation tasks: rewriting the Streamlit UI, expanding the song catalog from 18 to 50 songs with vibe descriptions, fixing bugs, updating the README, and suggesting the input validation guardrail in `interactive_test.py`.
- **One instance where AI was helpful.** When the `app.py` file from a different project (a number-guessing game) was brought in to serve as the Streamlit UI, the AI immediately identified that the file had nothing to do with music recommendations and needed to be fully rewritten rather than patched. It then built the correct UI from scratch by reading `recommender.py` to understand the actual data structures and function signatures. Without that catch, the app would have been broken from the start.
- **One instance where AI was incorrect.** When first asked how to run the app, the AI gave the command `cd applied-ai-system-project && streamlit run src/app.py`, but the terminal was already inside the `applied-ai-system-project` directory. Running that command caused a "not recognized" error because `streamlit` was not on the system PATH. The AI had assumed a different working directory and had not accounted for the PATH issue. The correct command turned out to be `python -m streamlit run src/app.py`. It's a small mistake but still shows that AI is not always correct. 
- **Takeaway.** AI assistance was most useful for mechanical, well-defined tasks like generating song data or fixing a known bug. It was less reliable for tasks that required knowing the specific state of the local environment, like the correct run command or whether a key was genuinely valid. Checking AI output before running it — especially for setup and environment commands — turned out to be important.
