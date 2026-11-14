# Pom — growth playbook (content + publishing algorithm)

Read this before writing any episode. The weekly analytics review updates the **"What works for Pom"** and **"Experiments"** sections; the rest changes only when platforms change.
_Last updated: 2026-11-14 (second weekly review: 9 episodes scoreable ≥ 72 h + 3 early; E2 & E3 concluded, E4 blocked, E6 started; "Pom's Loop" series opened; story_why capped at 25 s; slots unchanged)_

## 1. What the platforms reward (sources at the bottom)
| | Strongest signals | What it means for Pom |
|---|---|---|
| **YouTube Shorts** | Whether viewers *choose to view* vs swipe away, average view duration and **average % viewed**, likes, satisfaction. Only "engaged views" (watched past the first seconds) count for monetization. | First 1–2 s decide everything. Short and complete > long. End on the payoff. |
| **Instagram Reels** | **Watch time**, **likes per reach**, **sends per reach** (DM shares). Sends weigh most for reaching non-followers; likes weigh more for followers. Original content only (reposts get no recommendations). | Make it *sendable*: relatable situation + "send this to…" CTA. Trial Reels show a reel to non-followers first — use them for A/B tests (needs a minimum follower count — Pom is not there yet). |
| **TikTok** | Predicted likes, shares, comments, follows, profile visits, **finishing vs skipping**, watch time, sound taps, "not interested". Also post time, region, language, sound, length, hashtags. | Completion + comments. Ask a question people want to answer. English captions, US-friendly posting time. |
| **All (recommender design)** | Systems like ByteDance's Monolith (open-sourced on GitHub) train **online/in real time** from fresh interactions. | The first hours after posting shape distribution → post when the audience is awake; reply to early comments. |

## 2. Episode recipe (default rules)
1. **Hook in frame 1** (no fade-in, no logo). Text readable in < 1.5 s: a number, a date, a "POV", or a relatable pain. Pom must be visible in the first frame. **Pom data (§6): the opener must describe the viewer's own moment right now ("It's 11 PM. Finally me time.", "Day 1 → Day 60", "It's dark at 5 PM") — not an offer/deal, a pop-culture reference or an off-niche fact. Don't add a second instruction line ("Pick A or B") in the first 2 s.**
2. **One idea, one turn.** Structure: hook → problem / A vs B → consequence / time skip → *the line that lands* (stop) → answer + CTA.
3. **Length: 15–20 s for montage/split; story_why max 25 s** (2026-11-14: every post ≤ 17.7 s held ~50% watched; 18.8–22 s ~32%; every post > 40 s got ≤ 131 IG views and ≤ 206 YT views). Every scene must earn its seconds; cut anything that repeats.
4. **Loop the ending.** Last frame should connect to the first (same pose / same question) so replays feel natural. No lingering after the payoff; CTA ≤ 2 s on screen.
5. **Make it sendable.** The situation must be about *someone you know* ("the friend who always says from Monday"). Instagram caption ends with "📩 Send this to…".
6. **Comment bait that's easy to answer:** one word or A/B ("Comment DAY 1", "A or B?"). Put it at the END only (on-screen + caption). In 12 posts Pom has 1 Instagram comment and 2 YouTube comments in total → Paul replying/pinning a first comment matters more than the wording.
7. **On-screen text ≤ ~30 chars per line, max 2 lines at once**, key line in orange.
8. **Consistent character = brand.** Always Pom (orange beanie + scarf). Grey = problem, warm = change.
9. **Captions per platform** (see README): YouTube searchable title (keyword first, ≤ 70 chars ideally), TikTok short question + 3–5 hashtags, Instagram longer + send/save CTA.
10. **Audio quality gate:** every render must be click-free (the 2026-11-03 fix in `pom_audio.py` fades every note's tail; never remove it). A bad-sounding video is worse than no video.

## 3. Publishing algorithm
- **Cadence:** one main video per day (episodes Sun/Mon/Wed/Fri, stories Tue/Thu/Sat), max 1 main video/day, same slots every time — consistency beats perfect timing. Plus TikTok-only "Pom quick" (see README budget).
- **Format rotation until the 2026-11-21 review (E6, §7):** **Sun + Wed = "Pom's Loop"** (proven montage, ≤ 20 s, "your moment right now" hook — see §6); **Mon + Fri = story_why compressed to 20–25 s** (4–5 spoken lines, 50–65 words: hook → what he did → WHY + name → fix → question). Tue/Thu/Sat as before. If ElevenLabs is unavailable, the story_why day falls back to a silent montage.
- **Slots (Europe/Bucharest) — from Metricool `getBestTimeToPostByNetwork`, re-checked 2026-11-14 for Nov 15–21 (same peaks, no change):** the same video goes out per network at
  - **YouTube: 16:00** (peak every day of the week, 15–17 strong)
  - **TikTok: 18:00** (evening peak every day; 10:00 is the other peak)
  - **Instagram: 18:00** (second peak after 10:00; 18:00 also reaches the UK evening / US midday for an English audience)
  - **TikTok-only "Pom quick": 10:00** the day after a main episode (TikTok's morning peak).
  A day is "taken" when it already has a main post (YouTube 16:00 / TikTok 18:00 / Instagram 18:00). Re-check best times monthly; Pom reaches 2 weeks of its own data on 2026-11-16, so from the 2026-11-21 review a slot may move (within ±2 h, between 17:00 and 23:00 for IG/TikTok) when the data clearly favours it; record it in "Experiments".
- **Order of priority when choosing a topic** (the episode task follows this):
  1. Dated/seasonal idea whose date is within 10 days.
  2. A topic/format from "What works for Pom" with the highest score.
  3. A competitor topic that over-performed in the last 30 days (Metricool competitors), done Pom's way.
  4. Fresh idea from this week's trends.
  Keep a 70/20/10 mix: 70% proven formats, 20% variations, 10% wild experiments.
- **Never repeat** a topic already in `episodes/`. A *format* can repeat; a topic cannot (sequels are fine if labelled "Part 2" and the first part scored top-25%).
- **First hour:** the delivery message reminds Paul to reply to the first comments (Metricool Inbox shows comments from all three networks in one place).

## 4. Episode tags (put in every spec as `"meta"`)
```json
"meta": {"topic": "money|habits|time|career|relationships|mindset|business",
         "format": "split|montage|counter|story|list|quick|story_why",
         "hook": "number|date|pov|question|pain|contrarian|story",
         "cta": "comment_word|ab_choice|send_to|save",
         "season": "none|<event name>",
         "series": "none|loop",
         "experiment": "<id from Experiments, or none>"}
```
The weekly review scores episodes and compares tags to learn what works.

## 5. Scoring (per episode, computed by `pom_score.py`)
Each metric is divided by Pom's **median** for that metric (so 1.0 = typical, 2.0 = twice as good), capped at 3, then weighted:
- **Instagram:** retention (avg % viewed) 0.30 · shares/reach 0.25 · saves/reach 0.10 · likes/reach 0.15 · comments/reach 0.10 · reel view rate (3 s) 0.10
- **TikTok:** full-video-watched rate 0.30 · avg watch time / duration 0.20 · shares/views 0.20 · comments/views 0.15 · likes/views 0.15
- **YouTube:** avg view duration / duration 0.40 · likes/views 0.20 · comments/views 0.15 · shares/views 0.15 · views 0.10
**Episode score** = average of the platform scores available. Only score episodes ≥ 72 h old. With < 5 scored episodes, treat results as hints, not rules. Entries with `"removed"` are skipped.
Notes: Metricool returns `null` for Instagram retention (IGRE27), so `performance.json` stores `retention` = avg watch time (IGRE24) / duration, marked `retention_source`. TikTok watch-time fields are `null` too, and likes/comments are ~0 → TikTok gets no score yet. **The score is a per-viewer quality ratio and ignores reach**: small posts can score well on YouTube from 1–2 extra likes (story001/002). Always read the score together with IG/YT views.

## 6. What works for Pom (updated by the weekly review)
_Review 2026-11-14. **9 episodes ≥ 72 h** (n ≥ 5 → rules, still young). ep010, ep011, ep013 (< 72 h) used as directional evidence only. YouTube for Nov 11–13 not synced yet; ep014/ep015 not out yet._

| Episode (length) | IG views | IG 3-s hold | IG % watched | IG likes/reach | YT views · AVD | Score |
|---|---|---|---|---|---|---|
| ep009 11 PM me time (19.5 s, habits, montage, pain) | 1,509 | 56% | 41% | 3.2% | 1,069 · 7 s | **1.60** |
| ep001 the loop (17 s, habits, montage, pain) | 2,066 | 61% | 57% | 4.5% | 1,172 · 8 s | **1.53** |
| ep003 dark at 5 PM (21.9 s, habits, split, pain) | 893 | 58% | 38% | 4.1% | 1,288 · 8 s | 1.34 |
| ep008 glow-up boring middle (17.7 s, habits, montage, contrarian) | 1,617 | 67% | 51% | 1.9% | 1,205 · 7 s | 1.20 |
| ep007 11.11 24-hour rule (17.5 s, money, montage) | 1,408 | 62% | 49% | 0.4% | 803 · 4 s | 0.98 |
| ep005 winter arc Monday (18.9 s, habits, split) | 1,197 | 50% | 32% | 0.7% | 801 · 5 s | 0.94 |
| story001 Voyager (52 s, science story) | 131 | 33% | 14% | 0.9% | 206 · 12 s | 0.94 |
| story002 Roanoke (59 s, history story) | 11 | 38% | 31% | 0% | 159 · 14 s | 0.82 |
| ep004 Black Friday (18.8 s, money, split) | 141 | 32% | 29% | 0.8% | 498 · 5 s | 0.62 |
| _early:_ ep010 smart people stuck (17.7 s, mindset, split) | 163 | 44% | 29% | 0.6% | – | (1.22) |
| _early:_ ep011 Mariah is back (21 s, habits, montage) | 154 | 26% | 20% | 0% | – | (0.83) |
| _early:_ ep013 can't say no (42.3 s, story_why narrated) | 124 | 52% | 14% | 0% | – | (0.36) |

Tag averages (≥ 72 h): format **montage 1.33** (n 4) vs split 0.97 (n 3) vs stories 0.88 (n 2) · hook **pain 1.35** (n 4) vs number 0.81 (n 3) · topic **habits 1.32** (n 5) vs money 0.80 (n 2) · season winter 1.47 (n 2) · CTA comment_word 1.22 vs ab_choice 0.72.

1. **Winning formula = 17–20 s montage of a habit loop, opened on "your moment right now".** The 4 montages average 1.33, the two top scores are both habit-loop montages with a pain hook (ep009 1.60, ep001 1.53 → §8 "> 1.5 twice" → series **"Pom's Loop"**). These 5 posts (ep001, 003, 007, 008, 009) reached 893–2,066 IG views and 803–1,288 YT views each.
2. **Instagram distribution is all-or-nothing: ~1,000+ views or ~150.** Every post above 800 IG views had a 3-s hold ≥ 50% *and* ≥ 32% watched; every post ≤ 163 views missed one of them — weak opener (ep004 32%, story001 33%, ep010 44%, ep011 26% hold) or too long to finish (ep013: good 52% hold but only 14% watched of 42 s). Openers that failed: a deal line ("Everything is 50% off"), a space fact, a pop-culture line ("Mariah is back") and a "you saved another video" line.
3. **Length: short wins on every platform.** % watched on IG: ≤ 17.7 s median 50% (ep001 57, ep007 49, ep008 51, ep010 29) vs 18.8–22 s median 32% vs > 40 s 14–31%. YouTube: all 7 episodes of 17–22 s got 498–1,288 views; the two 52–59 s stories got 159–206. The narrated story_why (ep013, 42 s) shows the same pattern early → story_why capped at 25 s from now on (E6).
4. **Money underperforms habits (E3 concluded):** money 0.80 avg (ep004 0.62, ep007 0.98) vs habits 1.32. ep007 got reach (hold 62%) but the lowest likes/reach (0.4%) and the lowest YouTube AVD (4 s = 23%). Money stays only as the 20% variation, opened on the viewer's pain.
5. **True/unsolved stories are off Pom.** story002 (Roanoke) got 11 IG views (reach 8) and 159 YT; story001 131 / 206. Keep them for "Mystery Frames".
6. **Engagement is still the weak spot:** 1 IG comment (ep007) and 2 YT comments across all posts; best sharer ep009 (4 IG shares). Likes/reach is highest on the "pain" hooks (ep001 4.5%, ep003 4.1%, ep009 3.2%).
7. **TikTok is not usable as a signal:** 11–22 views per short post, 42–59 on the long ones, 0 followers, watch-time fields empty in Metricool. That pattern (same ~17 views regardless of content) is an account/distribution problem, not content — Paul has to check it in the app (§ "Paul to do" in the review message).
8. Followers (Metricool, 2026-11-14): YouTube 11 (+4 this week, 7 → 11), Instagram 3 (4 → 3), TikTok 0.
- ep002 "60 days left" was deleted by Paul (audio bug + weak video) — not data. ep009b (E4 Trial Reel) never published (follower requirement) — not data.

## 7. Experiments (one variable at a time)
| id | Hypothesis | How | Status |
|---|---|---|---|
| E1 | Explicit "Pick A or B" in the first 2 s raises comments & completion | ep004 + ep005 opened with "Pick A or B." | **concluded 2026-11-07 — not supported.** Keep "A or B?" only at the end. |
| E2 | Under-20 s episodes get higher % viewed than 20–25 s | ep010 (17.7 s) vs ep011 (21.0 s) + all montage/split posts | **concluded 2026-11-14 — supported.** IG % watched: ≤ 17.7 s median 50% (n 4) vs 18.8–22 s median 32% (n 5); ep010 29% vs ep011 20%. Default 15–20 s (§2.3). |
| E3 | Money topics outperform habit topics | money ep004, ep007 vs habits ep001, 003, 005, 008, 009 | **concluded 2026-11-14 — not supported.** Money 0.80 vs habits 1.32 avg score; ep007 YT AVD 4 s (lowest). Money = 20% variation only, pain-first opener. |
| E4 | Instagram Trial Reel with an alternative hook finds a better opener | ep009b as `TRIAL_REEL` (opener "It's 1:40 AM. Again.") | **blocked 2026-11-11** — Metricool ERROR: account below Instagram's Trial Reel follower requirement. Retry when IG followers grow (re-check monthly). Don't schedule Trial Reels until then. |
| E_story | Story-first narrated episodes (30–40 s, WHY + name) beat the silent A/B format | ep013 (42.3 s), ep014 (39.0 s), ep015 (38.6 s) | **running — early warning.** ep013: 124 IG views, hold 52% (good), only 14% watched (5.9 s of 42 s). Conclude at the 2026-11-21 review with ep014/ep015. Long arm of E6. |
| E6 | story_why compressed to 20–25 s keeps the good story hook (≥ 50% hold) and gets ≥ 30% watched / ≥ 800 IG views, vs the 38–42 s versions | Mon + Fri episodes from 2026-11-16 as story_why 20–25 s (4–5 lines, 50–65 words); compare with ep013–ep015. Same narrator, same structure — only length changes. Sun + Wed stay "Pom's Loop" montages as the baseline. | **started 2026-11-14** — conclude 2026-11-28 (needs ≥ 3 short story_why ≥ 72 h). Metrics: IG views, 3-s hold, % watched, YT views. |
| E_quick | 8–14 s TikTok-only "Pom quick" clips add views/follows without hurting main episodes | 2/week at 10:00 | **paused** — TikTok gives every post ~11–22 views (ep006: 11). Resume when a main post passes 200 TikTok views. |
| E_slots | Per-network slots (YT 16:00, TT/IG 18:00) beat a single 19:00 slot | From 2026-11-03; compare first-24 h views once ≥ 2 weeks of data | running — best-time data (2026-11-14) unchanged; all posts used the same slots, so there is no comparison yet. Review 2026-11-21. |

## 8. When content should change (decision rules for the review)
- A format scores < 0.7 three times in a row → pause it.
- A topic/format scores > 1.5 twice → make it a series (done 2026-11-14: **"Pom's Loop"** = habit-loop montage, pain hook, ≤ 20 s; ep001 1.53 + ep009 1.60). Title pattern: "<the moment> — Pom's Loop #N" only in the IG/TikTok caption, not the first frame.
- Retention low but shares high → the idea is good, the pacing is slow → cut the middle.
- Retention high but shares/comments low → stronger CTA / more relatable framing.
- YouTube views low but IG/TikTok fine → the first frame/title is the problem (YouTube is the most search/title sensitive).
- **IG 3-s hold < 45% → the opener failed** (2026-11-14: all 4 such posts got ≤ 163 views). Rewrite the first scene for that topic before reusing it.
- **IG % watched < 25% with hold ≥ 50% → the video is too long for its idea** (ep013): cut to ≤ 25 s.
- A format family that stays ≤ 200 IG views on 3 posts → stop it on Pom (applied 2026-11-14 to true/unsolved stories: story001, story002 → Mystery Frames only).

## Sources
- TikTok official: [Introduction to the TikTok recommendation system](https://www.tiktok.com/transparency/en/recommendation-system)
- Instagram (Mosseri's guidance, summarized): [Kompozy](https://kompozy.io/news/instagram-mosseri-ranking-signals-guidance), [Buffer](https://buffer.com/resources/instagram-algorithms/)
- YouTube Shorts metrics (citing YouTube Help): [Shortimize – Shorts retention](https://www.shortimize.com/blog/youtube-shorts-retention-rate)
- Recommender design (Monolith, ByteDance, open-source): [MLOps newsletter](https://mlops.substack.com/p/tiktoks-recommendation-engine-explained)
- Hook types by content type: [Bytecap research](https://www.bytecap.io/research/best-hooks-for-youtube-shorts)
- Posting frequency: [Buffer – how often to post](https://buffer.com/library/how-often-post-social-media)
- Best times: Metricool `getBestTimeToPostByNetwork` (brand pomschoices, weeks of 2026-11-03, 2026-11-08 and 2026-11-15)
- Pom performance: Metricool analytics (brand pomschoices), pulled 2026-11-07 and 2026-11-14 → `analytics/performance.json`
- Competitors: Metricool YouTube competitor videos (Oct 15–Nov 14) → `ideas/COMPETITORS.md`, `ideas/IDEAS.md`
