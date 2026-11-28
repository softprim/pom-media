# Pom — growth playbook (content + publishing algorithm)

Read this before writing any episode. The weekly analytics review updates the **"What works for Pom"** and **"Experiments"** sections; the rest changes only when platforms change.
_Last updated: 2026-11-28 (fourth weekly review: 23 episodes scoreable ≥ 72 h + 3 early; **E7 concluded — not supported on Instagram** (7 viewer-moment story_why posts, all 116–160 IG views); E8 started (story_why ≤ 18 s); TikTok views corrected to 0 (earlier pulls read duration as views); slots unchanged; montage relaunch (E_loop) asked of Paul again)_

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
3. **Length: 15–20 s for montage/split; story_why max 18 s during E8** (was 25 s until 2026-11-28; E7 arm 20–25 s held a median 27% on IG) (2026-11-14: every post ≤ 17.7 s held ~50% watched; 18.8–22 s ~32%; every post > 40 s got ≤ 131 IG views and ≤ 206 YT views). Every scene must earn its seconds; cut anything that repeats.
4. **Loop the ending.** Last frame should connect to the first (same pose / same question) so replays feel natural. No lingering after the payoff; CTA ≤ 2 s on screen.
5. **Make it sendable.** The situation must be about *someone you know* ("the friend who always says from Monday"). Instagram caption ends with "📩 Send this to…".
6. **Comment bait that's easy to answer:** one word or A/B ("Comment DAY 1", "A or B?"). Put it at the END only (on-screen + caption). In 20 posts Pom has 1 Instagram comment and 2 YouTube comments in total (2026-11-21) → Paul replying/pinning a first comment matters more than the wording.
7. **On-screen text ≤ ~30 chars per line, max 2 lines at once**, key line in orange.
8. **Consistent character = brand.** Always Pom (orange beanie + scarf). Grey = problem, warm = change.
9. **Captions per platform** (see README): YouTube searchable title (keyword first, ≤ 70 chars ideally), TikTok short question + 3–5 hashtags, Instagram longer + send/save CTA.
10. **Audio quality gate:** every render must be click-free (the 2026-11-03 fix in `pom_audio.py` fades every note's tail; never remove it). A bad-sounding video is worse than no video.

## 3. Publishing algorithm
- **Cadence:** one main video per day (episodes Sun/Mon/Wed/Fri, stories Tue/Thu/Sat), max 1 main video/day, same slots every time — consistency beats perfect timing. Plus TikTok-only "Pom quick" (see README budget).
- **Format (from the 2026-11-28 review):** the daily episode task makes **story_why ≤ 18 s (E8, §7)**: 4–5 short spoken lines, **38–42 spoken words** (Kokoro am_michael 1.05 ≈ 170–180 wpm → ~14 s of voice), structure hook → Pom's moment → WHY + name → fix → one-word CTA; cut the "result" line if needed (the fix line can carry it: "Pom tried it. Out by 7:00."). Keep everything else as in E7: frame 1 = the viewer's own moment (a clock time or a number + the pain, second person: "It's 7:00 AM. Snooze #4."), Pom enters in line 2, one-word comment CTA on screen and in the caption ("Comment SNOOZE if this is you"; comment_word 1.21 vs ab_choice 0.88 over 23 episodes). Never a third-person "Pom told / Pom knows" first frame. Duration check for the task: 15–19 s. The Sun + Wed "Pom's Loop" montage never ran (the task prompt forces story_why); it comes back only if Paul approves changing the task (E_loop, §7).
- **Slots (Europe/Bucharest) — from Metricool `getBestTimeToPostByNetwork`, re-checked 2026-11-21 for Nov 22–28 (same peaks every day, no change; E_slots closed):** the same video goes out per network at
  - **YouTube: 16:00** (peak every day of the week, 15–17 strong)
  - **TikTok: 18:00** (evening peak every day; 10:00 is the other peak)
  - **Instagram: 18:00** (second peak after 10:00; 18:00 also reaches the UK evening / US midday for an English audience)
  - **TikTok-only "Pom quick": 10:00** the day after a main episode (TikTok's morning peak).
  A day is "taken" when it already has a main post (YouTube 16:00 / TikTok 18:00 / Instagram 18:00). Re-check best times at every weekly review; a slot moves only when the data clearly favours another hour between 17:00 and 23:00 for IG/TikTok (2026-11-28, data for Nov 29–Dec 5: 18:00 is still the evening peak on TikTok every day and on Instagram 6 of 7 days — Friday is flat 16–18 h; YouTube still peaks at 16:00 every day → no change).
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
Notes: Metricool returns `null` for Instagram retention (IGRE27), so `performance.json` stores `retention` = avg watch time (IGRE24) / duration, marked `retention_source`. TikTok watch-time fields are `null` too, and **TikTok views (TKPO07) are 0 on every post except ep001 (1)** — the "17–24 TikTok views" in reviews up to 2026-11-21 were TKPO06 *duration* misread as views (corrected in `performance.json` 2026-11-28) → TikTok gets no score. **The score is a per-viewer quality ratio and ignores reach**: small posts can score well on YouTube from 1–2 extra likes (story001/002). Always read the score together with IG/YT views.

## 6. What works for Pom (updated by the weekly review)
_Review 2026-11-28. **23 episodes scored ≥ 72 h** (ep001–ep024; ep006 TikTok-only, no score; ep002/ep009b/ep012 not data). ep025–ep027 used as directional evidence (< 72 h); ep028 has no data yet. Metricool pull 2026-11-28 (IG + TikTok up to Nov 27, YouTube up to Nov 25)._

| Episode (length, format) | IG views | IG 3-s hold | IG % watched | IG likes/reach | YT views · AVD | Score |
|---|---|---|---|---|---|---|
| ep009 11 PM me time (19.5 s, montage, pain) | 1,519 | 55% | 41% | 3.1% | 1,287 · 7 s | **1.61** |
| ep008 glow-up boring middle (17.7 s, montage) | 1,621 | 67% | 51% | 1.9% | 1,323 · 7 s | **1.59** |
| ep001 the loop (17 s, montage, pain) | 2,067 | 61% | 57% | 4.5% | 1,172 · 8 s | **1.58** |
| ep003 dark at 5 PM (21.9 s, split, pain) | 893 | 58% | 38% | 4.1% | 1,289 · 8 s | **1.51** |
| ep020 missed day (23.1 s, story_why) | 212 | 57% | 35% | 1.7% | 1,166 · 8 s | 1.28 |
| ep024 2 AM replay (22.0 s, story_why, E7) | 118 | 49% | 25% | 1.8% | 869 · 9 s | 1.22 |
| ep017 told everyone (24.9 s, story_why) | 129 | 63% | 39% | 0% | 1,242 · 10 s | 1.16 |
| ep005 winter arc Monday (18.9 s, split) | 1,198 | 50% | 32% | 0.7% | 802 · 5 s | 1.07 |
| ep007 11.11 24-h rule (17.5 s, montage, money) | 1,410 | 62% | 49% | 0.4% | 802 · 4 s | 1.04 |
| ep010 smart people stuck (17.7 s, split) | 163 | 44% | 29% | 0.6% | 1,003 · 5 s | 1.02 |
| ep015 screen-time report (38.6 s, story_why) | 512 | 55% | 25% | 1.8% | 12 · 13 s | 0.97 |
| ep019 gym bag (23.1 s, story_why) | 219 | 60% | 41% | 0% | 691 · 6 s | 0.94 |
| ep023 snooze (24.1 s, story_why, E7) | 150 | 51% | 33% | 0.8% | 888 · 7 s | 0.93 |
| ep022 one quick check (21.4 s, story_why, E7-style) | 129 | 55% | 27% | 0.9% | 477 · 6 s | 0.88 |
| ep004 Black Friday (18.8 s, split, money) | 141 | 32% | 29% | 0.8% | 498 · 5 s | 0.87 |
| ep014 weekend disappears (39 s, story_why) | 149 | 52% | 37% | 0.8% | 22 · 11 s | 0.85 |
| ep013 can't say no (42.3 s, story_why) | 128 | 53% | 14% | 0% | 905 · 11 s | 0.75 |
| ep018 big task (23.7 s, story_why) | 129 | 38% | 21% | 0% | 149 · 6 s | 0.68 |
| ep011 Mariah is back (21 s, montage) | 155 | 26% | 19% | 0% | 434 · 5 s | 0.66 |
| ep016 knowing-doing gap (24.9 s, story_why) | 129 | 45% | 18% | 0% | 659 · 6 s | 0.64 |
| ep021 unfinished task (22.5 s, story_why, E7-style) | 116 | 49% | 23% | 1.0% | **3** · 1 s | 0.52 |
| (stories) story001 1.02 · story002 1.01 — off Pom since 2026-11-14 (score inflated by YT likes on 159–206 views) | 131 / 11 | | | | 206 / 159 | |
| _early:_ ep025 27 tabs (22.8 s, E7) | 122 | 43% | 19% | 0.9% | 66 · 4 s (day 3) | – |
| _early:_ ep026 leave late (20.4 s, E7) | 160 | 60% | 39% | 0% | – | – |
| _early:_ ep027 timer (20.9 s, E7, money) | 142 | 53% | 32% | 0% | – | – |

Tag averages (≥ 72 h): format **montage 1.30** (n 5) · split 1.12 (n 4) · **story_why 0.90** (n 12) · hook pain 1.20 (n 8) vs story 0.87 (n 10) · topic habits 1.09 (n 13) vs mindset 1.01 (n 4) vs money 0.96 (n 2) · CTA **comment_word 1.21** (n 11) vs ab_choice 0.88 (n 12) · E7 1.08 (n 2: ep023, ep024).
Week totals (posts Nov 21–27, all story_why): **IG 937 views** (posts Nov 14–20: 1,479; Nov 8–13: 4,990) · **YouTube channel 2,390 views Nov 21–25** (Nov 14–20: 4,009) · **TikTok 0 views** on every post. Followers 2026-11-27: YouTube 11 (+0), Instagram 4 (+0), TikTok 0 (+0).

1. **E7 failed on Instagram: the viewer-moment opener did not unlock distribution.** All 7 story_why posts with a viewer-moment frame 1 (ep021–ep027) stayed at **116–160 IG views**, likes/reach 0–1.8% (median 0.9%), 0 comments, 0 shares. The opener *holds* (3-s hold 43–60%, median 51%) — the drop happens later: IG % watched 19–39% (median 27%) vs 38–57% for the four montage winners. → The bottleneck on IG is the narrated middle, not the first frame.
2. **Caution — the IG drop is not only a format effect.** Since Nov 11 no post of *any* format passed 220 IG views except ep015 (512): the split ep010 (163) and the montage ep011 (155) flopped too, with weak openers. All 4 IG winners were posted Nov 1–10. The only way to separate "montage beats story_why" from "the account lost its early boost" is to post montages again (E_loop) — that still needs Paul's OK to change the episode task.
3. **YouTube is where story_why works.** 8 of 12 story_why uploads got **477–1,242 YT views** (ep017 1,242, ep020 1,166, ep013 905, ep023 888, ep024 869) — the same range as the montages — with AVD 6–10 s (30–40%). But **4 uploads were barely shown: ep014 22, ep015 12, ep021 3, ep025 66 (day 3)** — content-independent (ep015 was the best IG story_why). Looks like a delivery/processing problem on those uploads → Paul to check them in YouTube Studio (restrictions, "made for kids", processing).
4. **Shorter holds better (directional):** among the 20–25 s story_why, the two shortest (ep026 20.4 s 39%, ep027 20.9 s 32%) had the best IG % watched of the E7 arm; montage/split ≤ 19.5 s held 41–57% when the opener worked (E2). → E8 tests story_why ≤ 18 s.
5. **Engagement is still almost zero:** 0 IG comments and 0 YouTube comments on all 7 E7 posts despite one-word CTAs; the 23-episode total is 1 IG comment and 2 YT comments. Likes on YouTube are the only engagement that moves (ep017 18, ep020 11, ep024 8). Paul replying/pinning a first comment remains the cheapest lever.
6. **TikTok: 0 views on all 27 posts** according to Metricool TKPO07 (ep001: 1). This is an account/connection problem, not content: earlier reviews' "17–24 views" were the video duration column. Paul must check in the TikTok app whether the posts are public and get views.
7. **Money and true stories stay down** (money 0.96, n 2; stories off Pom) — unchanged.
- ep002 "60 days left" deleted by Paul — not data. ep009b never published — not data. ep012 exists in `episodes/` but was never scheduled — not data.

## 7. Experiments (one variable at a time)
| id | Hypothesis | How | Status |
|---|---|---|---|
| E1 | Explicit "Pick A or B" in the first 2 s raises comments & completion | ep004 + ep005 opened with "Pick A or B." | **concluded 2026-11-07 — not supported.** Keep "A or B?" only at the end. |
| E2 | Under-20 s episodes get higher % viewed than 20–25 s | ep010 (17.7 s) vs ep011 (21.0 s) + all montage/split posts | **concluded 2026-11-14 — supported.** Default 15–20 s for montage/split (§2.3). |
| E3 | Money topics outperform habit topics | money ep004, ep007 vs habits | **concluded 2026-11-14 — not supported.** Money = 20% variation only, pain-first opener. |
| E4 | Instagram Trial Reel with an alternative hook finds a better opener | ep009b as `TRIAL_REEL` | **blocked 2026-11-11** — follower requirement (IG 4 followers on 2026-11-21). Re-check monthly; don't schedule Trial Reels. |
| E_story | Narrated story_why (30–40 s) beats the silent montage/split format | ep013, ep014, ep015 vs ep001–ep011 | **concluded 2026-11-21 — not supported.** Avg score 0.86 (0.69 / 0.79 / 1.11) vs montage 1.33; IG 128 / 149 / 508 views vs 893–2,067 for the montage winners. |
| E6 | story_why compressed to 20–25 s keeps the hook and gets ≥ 30% watched / ≥ 800 IG views | ep016–ep022 (20–25 s) vs ep013–ep015 | **concluded early 2026-11-21 — half supported.** % watched up (median 35% vs 24%; ep017 39%, ep019 41%), hold ≥ 50% on 3 of 5; but IG views 126–219, none near 800 (n 2 ≥ 72 h + 3 directional, all five in the same 126–219 band). Keep story_why ≤ 25 s; the bottleneck is likes, not length. |
| E_slots | Per-network slots (YT 16:00, TT/IG 18:00) beat a single 19:00 slot | from 2026-11-03 | **closed 2026-11-21 — keep slots.** Best-time data for Nov 22–28 still peaks at YT 16:00, IG/TT 18:00 every day; the reach drop after Nov 11 happened with identical slots, so it is not a timing effect. |
| E7 | A story_why that opens on **the viewer's own moment** ("It's 7:00 AM. Snooze #4.") gets ≥ 2% IG likes/reach and ≥ 400 IG views | Every story_why from ep021 on (ep021–ep029) | **concluded 2026-11-28 — not supported.** 4 posts ≥ 72 h (ep021–ep024) + 3 directional (ep025–ep027): IG views 116–160 (none near 400), likes/reach 0–1.8% (median 0.9%), 0 comments. Hold stayed fine (median 51%); % watched median 27%. Keep the viewer-moment opener (it costs nothing and holds), but it is not the lever. YouTube 477–888 views when delivered. |
| E_loop (proposed) | Relaunching "Pom's Loop" montages (≤ 20 s, silent text + music, viewer-moment hook) restores 800+ IG views now — and tells us whether the IG drop since Nov 11 is the format or the account | 2 per week (Sun + Wed) next to story_why | **needs Paul's OK (asked 2026-11-21 and again 2026-11-28)** — the daily episode task can only make narrated story_why (its prompt hard-codes `format: story_why`). This is now the most important open test. |
| E_quick | 8–14 s TikTok-only "Pom quick" clips add views/follows | 2/week at 10:00 | **paused** — TikTok shows 0 views on every post (Metricool TKPO07). Resume only after Paul confirms TikTok posts are public and get views. |
| **E8** | story_why cut to **≤ 18 s** (38–42 spoken words, 4–5 lines) gets **≥ 35% IG watched** and **≥ 250 IG views**, vs the 20–25 s E7 arm (median 27% watched, 116–160 views) | Every story_why from the next episode made after 2026-11-28 (first: the Mon Nov 30 / Tue Dec 1 slot). Everything else unchanged: viewer-moment frame 1, Pom in line 2, Kokoro voice, one-word CTA, same slots. | **started 2026-11-28.** Conclude 2026-12-05 if ≥ 3 E8 posts are ≥ 72 h, else 2026-12-12. Metrics: IG % watched, IG views, IG likes/reach, YT AVD %. If it fails too (≤ 200 IG views on 3 posts) → story_why leaves the Instagram main slot (§8). |

## 8. When content should change (decision rules for the review)
- A format scores < 0.7 three times in a row → pause it.
- A topic/format scores > 1.5 twice → make it a series (done 2026-11-14: **"Pom's Loop"** = habit-loop montage, pain hook, ≤ 20 s; ep001 1.53 + ep009 1.60). Title pattern: "<the moment> — Pom's Loop #N" only in the IG/TikTok caption, not the first frame.
- Retention low but shares high → the idea is good, the pacing is slow → cut the middle.
- Retention high but shares/comments low → stronger CTA / more relatable framing.
- YouTube views low but IG/TikTok fine → the first frame/title is the problem (YouTube is the most search/title sensitive).
- **IG 3-s hold < 45% → the opener failed** (2026-11-14: all 4 such posts got ≤ 163 views). Rewrite the first scene for that topic before reusing it.
- **IG % watched < 25% with hold ≥ 50% → the video is too long for its idea** (ep013): cut to ≤ 25 s.
- A format family that stays ≤ 200 IG views on 3 posts → stop it on Pom (applied 2026-11-14 to true/unsolved stories: story001, story002 → Mystery Frames only). **2026-11-21: story_why triggered this on Instagram (6 posts ≤ 200); 2026-11-28: E7 also stayed ≤ 160 on 7 posts.** Decision 2026-11-28: story_why stays on Instagram for one more test (E8, ≤ 18 s) because Instagram is the platform E8 measures and posting a low-reach reel has no known penalty; if E8 also stays ≤ 200 IG views on 3 posts, story_why leaves the Instagram main slot (YouTube + TikTok only) until Paul switches the task to Pom's Loop montages.
- **A platform shows 0 views on every post → check the account before judging content** (2026-11-28: TikTok 0 views on 27 posts).
- **YouTube views < 100 after 3 days while neighbours get 500+ → delivery problem, not content** (ep014, ep015, ep021, ep025): exclude from YouTube conclusions and ask Paul to check YouTube Studio.
- **IG hold ≥ 50% and % watched ≥ 35% but likes/reach < 1% → the video is watched but not felt** (ep017, ep019): make the first frame about the viewer, make the payoff a recognisable "that's me" moment, end with a one-word comment CTA.

## Sources
- TikTok official: [Introduction to the TikTok recommendation system](https://www.tiktok.com/transparency/en/recommendation-system)
- Instagram (Mosseri's guidance, summarized): [Kompozy](https://kompozy.io/news/instagram-mosseri-ranking-signals-guidance), [Buffer](https://buffer.com/resources/instagram-algorithms/)
- YouTube Shorts metrics (citing YouTube Help): [Shortimize – Shorts retention](https://www.shortimize.com/blog/youtube-shorts-retention-rate)
- Recommender design (Monolith, ByteDance, open-source): [MLOps newsletter](https://mlops.substack.com/p/tiktoks-recommendation-engine-explained)
- Hook types by content type: [Bytecap research](https://www.bytecap.io/research/best-hooks-for-youtube-shorts)
- Posting frequency: [Buffer – how often to post](https://buffer.com/library/how-often-post-social-media)
- Best times: Metricool `getBestTimeToPostByNetwork` (brand pomschoices, weeks of 2026-11-03, 2026-11-08, 2026-11-15, 2026-11-22 and 2026-11-29)
- Pom performance: Metricool analytics (brand pomschoices), pulled 2026-11-07, 2026-11-14, 2026-11-21 and 2026-11-28 → `analytics/performance.json`
- Competitors: Metricool YouTube competitor videos (Oct 15–Nov 14, Oct 22–Nov 21, Oct 29–Nov 28) → `ideas/COMPETITORS.md`, `ideas/IDEAS.md`
