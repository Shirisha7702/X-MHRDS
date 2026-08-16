# X-MHRDS — Live Demo Guide
## Exactly what to click, what to paste, what to say, and what to expect

> **Companion document, not a replacement:** `PROJECT_PLAYBOOK.md` is the reference — what everything is, why it was built that way, how the math works, and the full Q&A prep. **This document is the script** — the literal sequence of clicks and copy-paste inputs to run a live demo without fumbling for an example on the spot. Read the Playbook once beforehand; keep this one open in a second window *during* the demo.

---

## Table of Contents

1. [Before You Start — Pre-Flight Checklist](#1-before-you-start--pre-flight-checklist)
2. [Two Ready-Made Scripts](#2-two-ready-made-scripts)
3. [Stop 0 — Landing Page](#stop-0--landing-page)
4. [Stop 1 — Entering the Dashboard (Sidebar / Header / Theme)](#stop-1--entering-the-dashboard-sidebar--header--theme)
5. [Stop 2 — Diagnostic Assessment (Sandbox)](#stop-2--diagnostic-assessment-sandbox)
6. [Stop 3 — Multi-XAI Attribution Studio](#stop-3--multi-xai-attribution-studio)
7. [Stop 4 — Clinical Analytics](#stop-4--clinical-analytics)
8. [Stop 5 — Model Drift & PSI](#stop-5--model-drift--psi)
9. [Stop 6 — What-If Counterfactual Perturbation](#stop-6--what-if-counterfactual-perturbation)
10. [Stop 7 — Historical Retrieval (Case Search)](#stop-7--historical-retrieval-case-search)
11. [Stop 8 — Demographic Audit (Fairness)](#stop-8--demographic-audit-fairness)
12. [Stop 9 — Temporal Trajectory](#stop-9--temporal-trajectory)
13. [Stop 10 — Live Stream Monitor](#stop-10--live-stream-monitor)
14. [Stop 11 — Clinical Safety Copilot (all 4 sub-tabs)](#stop-11--clinical-safety-copilot-all-4-sub-tabs)
15. [Stop 12 — Command Palette (30-Second Flourish)](#stop-12--command-palette-30-second-flourish)
16. [Handling Live Q&A](#16-handling-live-qa)
17. [Troubleshooting Cheat Sheet](#17-troubleshooting-cheat-sheet)
18. [Timing Budget](#18-timing-budget)

---

## 1. Before You Start — Pre-Flight Checklist

Run through this **10 minutes before** your professor walks in, not while they're watching.

- [ ] **Backend is running and actually reachable.** `cd backend/src && uvicorn main:app --reload --port 8000`, then open `http://localhost:8000/` in a spare browser tab — you should see `{"status":"online",...}`. *(This exact failure happened during development this session: the frontend was up but the backend wasn't, and every tab showed red "Failed to fetch" toasts and `ERR_CONNECTION_REFUSED` in the console. It looks like a broken app but is just a not-yet-started server — see [Troubleshooting](#17-troubleshooting-cheat-sheet).)*
- [ ] **Frontend is running.** `cd frontend && npm run dev`, open `http://localhost:5173`. Or just run `run.bat` (Windows) / `run.sh` from the project root, which starts both.
- [ ] **Models are trained.** Confirm `models/logistic_regression.pkl`, `models/svm_classifier.pkl`, `models/bert_model/model.safetensors`, and `models/roberta-base/model.safetensors` all exist. If any is missing, that model's tab will 404 — see [Section 22 of the Playbook](PROJECT_PLAYBOOK.md#22-how-to-run--reproduce).
- [ ] **(Optional) Gemini narrative enabled.** If `.env` has a working `GOOGLE_API_KEY`, the Clinical Copilot's DSM-5 RAG tab will show an **"AI-generated"** badge on its narrative instead of **"Template"**. Neither is wrong to demo — see [Stop 11](#stop-11--clinical-safety-copilot-all-4-sub-tabs) — but decide in advance which one you're going to show and don't be surprised by the other.
- [ ] **Seed a little history before you start**, so the Drift and Fairness tabs don't show flat placeholder defaults: run 2–3 analyses in the Sandbox first (see [Stop 2](#stop-2--diagnostic-assessment-sandbox)), and let the Live Monitor run for ~30 seconds once at least once beforehand so `analyses` has both `manual` and `monitor` rows in it.
- [ ] **Browser window ~1440px wide or fullscreen**, light theme on (professors read dark-mode screenshares worse over a projector — toggle with the moon/sun icon in the header if it opens in dark mode). Close devtools/console unless you specifically want to show something there.
- [ ] **Have this file and the Playbook open in a second monitor/window** so you're never improvising an example input from memory.

---

## 2. Two Ready-Made Scripts

| | Lightning (~6–8 min) | Full Walkthrough (~18–22 min) |
|---|---|---|
| Use when | Time-boxed slot, or a first pass before deeper questions | You have the room's full attention and want to show governance depth |
| Stops | 0 → 2 (one high-risk example) → 3 → 8 (Fairness) → 11 (Copilot) | 0 → 1 → 2 (three examples) → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 |
| What it proves | The model works, it's explainable, it's audited, it has a clinical layer | All of that, plus robustness, drift, semantic retrieval, live streaming, and command-palette polish |

Both scripts are just subsets of the stop list below, run in order — nothing in the Lightning version needs setup the Full version doesn't also need.

---

## Stop 0 — Landing Page

**Purpose:** put every headline number on screen in one paged view before you've clicked anything — dataset size, four-model comparison table, fairness/construct-validity summary, authors, scope. This is your safety net if live inference has any hiccup later — the numbers already exist here, verified, static.

**Path:** the app opens here by default (`showLanding = true` in `App.jsx`). If you've already entered the dashboard, there's no button back to it — just refresh the page.

**What to point at, in order:**
1. Hero section — the animated waveform, the one-line problem statement.
2. **Dataset section** — 232,074 raw posts → 15,000 subsampled → 10,500/2,250/2,250 split.
3. **Evaluation table** — all four models' accuracy/precision/recall/F1 side by side.
4. **Construct validity section** — the negativity-confound residualization numbers.
5. **Fairness audit section** — the three linguistic-register cohorts and the recall gap.
6. **"Built beyond the original scope"** bullet list — cognitive distortion tagging, OOD detection, MC-Dropout, live monitor, clinical copilot.

**Say this:**
> "Before I open the live tool, here's the headline result: four models trained side by side — two transparent linear baselines, two fine-tuned transformers — all evaluated on the same held-out 2,250-post test split. The transformers get to about 97.7% F1, roughly six points above the linear baselines, and everything past this point in the demo is about answering *why* those numbers should be trusted, not just accepting them."

**Click "Enter Live Dashboard"** (nav bar or hero CTA) to proceed to Stop 1.

---

## Stop 1 — Entering the Dashboard (Sidebar / Header / Theme)

**Purpose:** orient the room to the app's layout in 20 seconds before diving into any one tab.

**What to point at:**
- The **left sidebar**, grouped into 5 categories (Core Assessment, Governance & Audits, Simulation & Search, Bias & Trajectory, Real-Time Monitoring) — mention this grouping is deliberate: it separates "run a prediction" from "audit the system" from "watch it live."
- The **model selector** at the bottom of the sidebar (or top of the header) — Logistic Regression / SVM (Calibrated) / BERT / RoBERTa. Every tab that depends on a model re-reads whichever is selected here.
- The **red "RESEARCH & CDS ONLY"** banner under the header — point out this is not cosmetic; it's the same safety framing carried through every clinical-facing feature (report disclaimers, copilot dispatch simulation, etc.).
- The **theme toggle** (sun/moon icon) — flip it once to show light/dark both work, then leave it on whichever you're presenting in.

**Say this:**
> "Everything here talks to a FastAPI backend over REST, plus one WebSocket for the live feed. Nine tabs, grouped by what kind of question they answer — I'll start with the core prediction, then work outward into how we know to trust it."

---

## Stop 2 — Diagnostic Assessment (Sandbox)

**Purpose:** the core feature — run a real prediction, show the tier escalation, the calibrated probability, and the word-level explanation, live.

**Path:** Sidebar → *Diagnostic Assessment*. Toggle input mode to **"Clinical Presets"** to use the dropdown instead of typing (faster, and guarantees a clean copy-paste-free run), or paste directly into the textarea in **"Direct Custom Text"** mode. Both are shown below — pick whichever suits your flow.

Run these **in this order** — the contrast between the first and third is the point.

### 2a. High-risk example

```text
I feel so completely hopeless. Every day is a struggle and I just want to end my life tonight.
```

- Click **Run Diagnostic Assessment** (or `Ctrl+Enter`).
- **Expect:** a high risk-probability %, a **Tier 3 (Severe Active Risk)** badge (red), and a word-attribution heatmap with `"end"`, `"life"`, `"tonight"`, `"hopeless"` lit up in red.
- **Say this:** "The tier isn't just thresholding the probability blindly — it also looks for an explicit method or timeline keyword like 'tonight' before escalating to Tier 3 rather than Tier 2. That logic lives in `multi_tier_classifier.py`."

### 2b. Low-risk / protective example

```text
Had a really tough week at work, but spending time with family and talking to my therapist helped me feel better.
```

- **Expect:** low probability, **Tier 0 or 1**, and — importantly — some words like `"tough"` or `"helped"` may light up faintly. If a *protective* word like `"helped"` or `"family"` shows a **green (protective)** highlight, call that out explicitly: it's the model down-weighting risk because of supportive context, not just an absence of red.
- **Say this:** "This is the contrast case — same interface, same model, and it correctly clears this as low risk despite mentioning a hard week. The heatmap is what lets you *verify* that, rather than trust it blindly."

### 2c. Long clinical narrative (Tier 3, multi-sentence)

```text
Over the last six months, everything in my life has collapsed. I lost my job, my relationship ended, and the constant unbearable weight in my chest never goes away even for a second. Every single morning I wake up wishing I hadn't. I have written letters to my family and cleared out my apartment. I bought a bottle of sleeping pills yesterday and I have made up my mind to end my life tonight when everyone is asleep. I cannot carry this exhausting agony anymore.
```

- **Expect:** Tier 3, high probability, and a much denser heatmap — good for showing the explanation scales to a realistic multi-sentence post, not just a one-liner.
- **This exact text is reused later** in the Multi-XAI Studio (Stop 3) and is the default preload of the Sandbox textarea — if you're short on time, you can skip 2a/2b and open straight on this one already sitting in the box.

### 2d. (Optional, if time allows) Multilingual example

```text
me siento solo y sin esperanza quiero morir
```

- **Expect:** the system detects Spanish, translates internally, runs the same pipeline on the translation, and shows **both** a native-language heatmap and the English translation underneath, with attribution scores projected back onto the original Spanish words.
- **Say this:** "The translation and language detection are heuristic — a small dictionary and a keyword-based detector, not a trained translation model — so I'll caveat that this is illustrative, not production-grade multilingual NLP." *(Being upfront about this is stronger than hoping it doesn't come up — see [Known Limitations](PROJECT_PLAYBOOK.md#24-known-limitations-say-these-before-your-professor-finds-them) #5 in the Playbook.)*

**After any run:** point out the **Report** and **Copilot** buttons that appear once a result exists — you'll use **Copilot** in Stop 11, so leave this last result (2c or 2d) on screen if you're about to jump there.

---

## Stop 3 — Multi-XAI Attribution Studio

**Purpose:** show that the model's explanation isn't the output of one cherry-picked method — four independent explainers agree.

**Path:** Sidebar → *Multi-XAI Studio*. It has its own preset dropdown; pick the first preset (the same six-month-collapse narrative from 2c) or paste it in directly.

```text
Over the last six months, everything in my life has collapsed. I lost my job, my relationship ended, and the constant unbearable weight in my chest never goes away even for a second. Every single morning I wake up wishing I hadn't. I have written letters to my family and cleared out my apartment. I bought a bottle of sleeping pills yesterday and I have made up my mind to end my life tonight when everyone is asleep. I cannot carry this exhausting agony anymore.
```

- Click **Run 4-Explainer Comparison**.
- **Expect:** an **Explainer Convergence Matrix** — pairwise Pearson correlations between SHAP, Integrated Gradients, LIME, and LOO, color-coded green (≥0.7) / amber (≥0.4) / red (<0.4) — followed by four stacked word-heatmaps, one per method, over the same text.
- **What to point at:** find one or two words (e.g. `"pills"`, `"tonight"`) that are highlighted consistently across **all four** panels, and one correlation cell that's green.
- **Say this:** "Each of these four methods derives attribution completely differently — one's exact linear algebra, one's game-theoretic, one's a gradient path integral, one's local perturbation sampling. When they converge on the same words, that's much stronger evidence those words are actually load-bearing than any single method's output alone." *(If asked what each method fundamentally is: [Playbook §26.7](PROJECT_PLAYBOOK.md#267-the-four-explainability-xai-methods).)*
- **Note:** this can take several seconds on CPU (SHAP is the slow one) — narrate through the wait rather than standing in silence: "SHAP is running a sampling-based approximation of an exponential computation, capped at 500 evaluations — this is the one method here that isn't instantaneous."

---

## Stop 4 — Clinical Analytics

**Purpose:** the model-comparison table and the robustness stress-test results, in one screen.

**Path:** Sidebar → *Clinical Analytics*. No input needed — loads automatically.

- **Left panel — Model Performance Comparison:** point at the four-row table (same numbers as the landing page — a good consistency callback: "these are the same figures I showed at the start, now sourced live from the running backend").
- **Right panel — Perturbation Robustness Metrics:** per model, three sub-rows — `original`, `typos`, `distracted`. Point at BERT's typo-injection F1 drop (~1.83 points) vs. its distracting-text drop (~0.31 points).
- **Say this:** "The typo test randomly swaps, drops, or doubles characters in 15% of words longer than three letters. The distraction test appends an unrelated, mildly positive sentence — 'anyway, I'm going to watch a comedy movie now' — to see if an irrelevant positive coda can drag a correct risk prediction down. The model is noticeably more sensitive to surface-level noise than to an irrelevant-but-grammatical addition, which is a defensible and explainable pattern."

---

## Stop 5 — Model Drift & PSI

**Purpose:** show the system has a mechanism to detect its own decay over time, not just a one-time evaluation number.

**Path:** Sidebar → *Model Drift & PSI*. Click **Refresh Drift Data** if you seeded history beforehand (Pre-Flight checklist) — otherwise it may show a small-sample placeholder.

- **What to point at:** the **PSI score** card (color-coded green/amber/red per the 0.10/0.20 thresholds), the **baseline vs. live-stream sample sizes**, and the **histogram** comparing the two probability distributions bucket by bucket.
- **Say this:** "PSI here is comparing the distribution of predictions from manual Sandbox use against the distribution coming out of the simulated Live Monitor feed — it's a stand-in for 'how the tool is actually being used' versus 'a reference distribution,' the same statistic used in production ML monitoring to catch silent model decay before accuracy metrics would show it."
- **If it shows small numbers / a flat default:** say so plainly — "with only a couple of predictions logged in this session, this is showing the small-sample fallback; it becomes meaningful once real usage accumulates" — this is more credible than pretending it's a fully-populated dashboard.

---

## Stop 6 — What-If Counterfactual Perturbation

**Purpose:** a very visual, intuitive demonstration of the model's sensitivity to specific word choices.

**Path:** Sidebar → *What-If Perturbation*. The fields preload with defaults — just click **Evaluate Wording Substitution**, or paste your own:

- **Text:** `I am feeling so hopeless and tired. I want to end my life tonight.`
- **Target Phrase to Swap:** `end my life`
- **Replacement Phrase:** `get help for my pain`

- **Expect:** two side-by-side probability cards (Original vs. Modified) and a "Risk De-escalated" badge with the probability delta.
- **Say this:** "This is a lightweight causal probe, not a full counterfactual-fairness framework — it's a single regex-safe word swap and a re-run of inference — but it's a fast, concrete way to show the model is actually responsive to specific lexical content, not just firing on vague negative sentiment." *(Ties directly back to the construct-validity audit in Stop 8/Playbook §13.2 — if this swap didn't move the needle much, that would itself be a red flag.)*

---

## Stop 7 — Historical Retrieval (Case Search)

**Purpose:** show the "find similar past cases" retrieval feature.

**Path:** Sidebar → *Historical Retrieval*.

```text
feeling sad and alone, nobody cares about me
```

- **Expect:** 1–3 results pulled from the small seeded case set in the database (past resolutions like "Operator contacted the user's university student counseling center...").
- **Say this, honestly:** "This is TF-IDF cosine similarity over a small seeded case table right now, not real embedding-based semantic search — I'd call it a working proof of concept for the retrieval *pattern* the Clinical Copilot is built around, and the natural next step is swapping in real sentence embeddings." *(This candor is explicitly recommended in the Playbook's Known Limitations #4 — better you say it than get caught overclaiming "semantic.")*

---

## Stop 8 — Demographic Audit (Fairness)

**Purpose:** the single best moment in the whole demo to show methodological maturity — this is the one to slow down on.

**Path:** Sidebar → *Demographic Audit*. Loads automatically for whichever model is currently selected — **switch the model selector to Logistic Regression first** if it isn't already, since that's the model the verified numbers below correspond to.

**What to point at, in this order:**
1. **The three cohort names** — Youth Slang / Formal Language / Literal-Direct. Say explicitly: *"This is not demographic data — there's no gender, age, or identity information anywhere in this dataset. This audits whether the model performs consistently across different ways of *phrasing* the same underlying crisis."*
2. **The Cohort Summary table** — Accuracy / Recall / Specificity per register, each with a 95% CI.
3. **Recall column specifically** — point out Youth Slang sits noticeably lower than Literal/Direct.
4. **The `n=X (under-powered)` amber warning** next to Recall — and explain *why* it's there: only 16 true-risk examples per cohort, below the audit's own 30-example significance floor.
5. **Accuracy**, by contrast, clears that floor (32 examples per cohort) and shows **no statistically significant cross-cohort gap**.

**Say this (the key line):**
> "There's a real, visible gap in the raw recall numbers — the model catches roughly 56% of true risk cases phrased in youth slang versus 87% phrased literally. But our own tool's statistical gate says that specific gap isn't certified significant yet, because each cohort only has 16 true-risk examples, below our 30-example minimum. I'd rather show you an honestly-uncertain result than round it up to a confident claim — and the fix is straightforward: write more scenarios per cohort, not change the methodology."

This single answer demonstrates: you understand statistical power, you built a tool that self-polices its own confidence, and you're not overselling your own results — which is exactly what a professor is listening for.

---

## Stop 9 — Temporal Trajectory

**Purpose:** short stop — a scripted demo timeline showing risk escalating over dated posts.

**Path:** Sidebar → *Temporal Trajectory*. Loads automatically — a fixed 4-post timeline (2026-07-01 → 2026-07-15) scored by the current model.

- **Expect:** a dated post list on the left, and a hand-built SVG line chart on the right showing the probability rising post-over-post.
- **Say this, proactively:** "I want to flag directly that this tab scores a fixed, illustrative 4-post timeline, not a real per-user history — the Live Monitor, next, is where trend detection is actually running against real logged data." *(Don't let this tab imply more than it does — the Playbook calls this out explicitly as a known limitation, and saying it yourself is much better than letting it surface as a gotcha.)*

---

## Stop 10 — Live Stream Monitor

**Purpose:** the most visually dynamic stop — a real-time feed with genuine trend/change-point detection computed on the fly.

**Path:** Sidebar → *Live Stream Monitor*. Click **Start Monitor** (with whichever model is currently selected).

- **What happens:** a synthetic post streams in roughly every 6 seconds, from one of 5 fictional users each following a scripted storyline (one escalating, one flat/benign, one flat/moderate, one de-escalating, one flat/high-risk).
- **Let it run for ~30–45 seconds** while you talk, then point at the **User Escalation Watch** table at the bottom — specifically a user's **trend label** (Escalating/Stable/De-escalating) and their little **sparkline**.
- **If a change-point marker appears** (a vertical line on a sparkline) — call it out specifically: "that vertical marker means our change-point detector — Binary Segmentation, from the `ruptures` library — found a sharp step-shift in this user's risk trajectory, not just a gradual trend. That's a different, more urgent signal than the slope alone would catch."
- **Click Stop Monitor** before moving on (or leave it running quietly in the background if you're moving to Copilot next, since the WebSocket doesn't block anything else).

---

## Stop 11 — Clinical Safety Copilot (all 4 sub-tabs)

**Purpose:** the clinical decision-support layer — DSM-5/C-SSRS grounding, the (new) AI-generated narrative, HIPAA-style audit tooling, and the explicitly-simulated action dispatcher.

**Path:** Click the **Copilot** button (header or sidebar) — it opens with whatever your **last Sandbox analysis** was, so run one first if you haven't (e.g. reuse the Stop 2c high-risk text). Four internal tabs:

1. **Safety Triage** — triage priority, recommended protocol, crisis hotline, action items. All deterministic, keyed off tier and probability.
2. **DSM-5 RAG Grounding** — the retrieved DSM-5 criteria matches, the C-SSRS protocol level, and the **Grounded Clinical Rationale** box.
   - Point at the small badge on that rationale: **"AI-generated"** (blue) or **"Template"** (gray).
   - **Say this:** "The DSM-5 keyword retrieval and the C-SSRS severity level above it are both deterministic Python — no model involved. What *can* optionally be AI-generated is just this one paragraph of clinician-facing narrative explaining that already-fixed result — and it's explicitly instructed never to override the tier above it, with the input PII-masked before it's sent anywhere, and a template fallback if the call fails for any reason." *(This is the single most defensible design choice to walk through if asked about LLM safety — see [Playbook §15](PROJECT_PLAYBOOK.md#15-the-gemini-backed-rag-narrative-new-this-session) and [§26.16](PROJECT_PLAYBOOK.md#2616-retrieval-augmented-generation-rag).)*
3. **HIPAA Compliance** — the tamper-evident compliance hash (SHA-256 over the text, tier, probability, and timestamp) and the PII-masking pass/fail indicator.
4. **Action Dispatcher** — click one of the three buttons (e.g. "Dispatch 988 Lifeline Safety Packet").
   - **Expect:** a green confirmation reading `[SIMULATED] Would trigger a 988 crisis line referral workflow in a production deployment. No real call was placed.`
   - **Say this, without being asked:** "This entire panel is simulated end to end — no integration with 988, a supervisor queue, or any real external system exists, and the response text says so explicitly. That's a deliberate safety boundary for a research prototype, not a missing feature."

---

## Stop 12 — Command Palette (30-Second Flourish)

**Purpose:** a quick, low-effort "polish" moment to close on.

**Path:** Press **Ctrl+K** (or **Cmd+K**) anywhere in the dashboard.

- Type a few letters of any tab name, model name, or "theme" — show the fuzzy filtering, hit Enter to jump.
- **Say this:** "Small thing, but worth showing — full keyboard-driven navigation across tabs, model switching, and theme toggling, in addition to the sidebar."
- **Don't claim it's complete:** it doesn't currently list the Multi-XAI Studio or Model Drift tabs — a minor, known gap, not worth bringing up unless asked.

---

## 16. Handling Live Q&A

- The full anticipated Q&A with prepared answers is in **[Playbook §27](PROJECT_PLAYBOOK.md#27-anticipated-qa)** — skim it once right before presenting.
- If you don't know the exact answer to something in the moment, it is always safe to say: *"That's covered in more depth in the written playbook — the short answer is [X], and I can show you the exact code if useful."* — then actually be ready to open the relevant file.
- **Proactively volunteer limitations before being asked one** — the [Known Limitations list](PROJECT_PLAYBOOK.md#24-known-limitations-say-these-before-your-professor-finds-them) (heuristic multilingual detection, TF-IDF "semantic" search, simulated dispatch, small fairness cohorts, orphaned frontend components) reads as far stronger engineering judgment coming from you first than as a concession dragged out of you.
- If a demo call genuinely errors (backend hiccup, model not loaded), don't panic-debug live — say "let me show you that from the landing page's pre-computed numbers instead" and pivot to Stop 0, then fix it after.

---

## 17. Troubleshooting Cheat Sheet

| Symptom | Likely cause | Fix |
|---|---|---|
| Every tab shows red "Failed to fetch" toasts; console shows `ERR_CONNECTION_REFUSED` on `localhost:8000` | Backend isn't running (or crashed) | Start it: `cd backend/src && uvicorn main:app --reload --port 8000`. Confirm `http://localhost:8000/` loads before touching the frontend again. |
| "No trained model metrics found" on Clinical Analytics | That model's `.pkl`/checkpoint doesn't exist under `models/` | Train it — see [Playbook §22](PROJECT_PLAYBOOK.md#22-how-to-run--reproduce). Or switch the model selector to one that *is* trained. |
| A specific model 404s in Sandbox ("Model weights not found") | Same as above, for that one model | Same fix, or pick a different model from the selector. |
| Drift / Fairness dashboards show flat, round placeholder numbers | Empty or near-empty database (`data/app.db`) — this is a designed fallback, not a bug | Run a few Sandbox analyses and/or the Live Monitor for ~30s before presenting (see Pre-Flight checklist). |
| RAG narrative always shows "Template," never "AI-generated" | No `GOOGLE_API_KEY` in `.env`, or the Gemini call failed silently (network/quota) | Check `.env` exists with a valid key; this is a safe fallback either way, not a broken demo — see [Playbook §15](PROJECT_PLAYBOOK.md#15-the-gemini-backed-rag-narrative-new-this-session). |
| SHAP explanation in Multi-XAI Studio takes a long time | Expected on CPU — SHAP is genuinely the slowest of the four methods | Narrate through it (see Stop 3) rather than waiting in silence; don't re-click while it's running. |
| Live Monitor table stays empty after clicking Start | The WebSocket only pushes events while the monitor is actually running, and the first tick takes up to 6 seconds | Wait one tick; if still empty, check the backend console for an error and confirm `ws://localhost:8000/api/ws/monitor` isn't blocked by a browser extension. |
| Multilingual example doesn't show a translation | `deep_translator` isn't installed, or the exact phrase isn't in the small hardcoded dictionary | Use the exact preset phrases in [Stop 2d](#2d-optional-if-time-allows-multilingual-example) — they're guaranteed to hit the dictionary path. |

---

## 18. Timing Budget

| Stop | Lightning | Full |
|---|---|---|
| 0. Landing page | 1 min | 1.5 min |
| 1. Dashboard tour | — | 1 min |
| 2. Sandbox (2–3 examples) | 2 min | 3.5 min |
| 3. Multi-XAI Studio | 1.5 min | 2.5 min |
| 4. Clinical Analytics | — | 1.5 min |
| 5. Drift & PSI | — | 1.5 min |
| 6. What-If | — | 1.5 min |
| 7. Case Search | — | 1 min |
| 8. Fairness Audit | 1.5 min | 3 min |
| 9. Temporal | — | 0.5 min |
| 10. Live Monitor | — | 1.5 min |
| 11. Copilot (4 sub-tabs) | 1.5 min | 3 min |
| 12. Command Palette | — | 0.5 min |
| **Total** | **~7.5 min** | **~22 min** |

Pad every number above by ~20% for actual live conditions (questions mid-flow, a slightly slow model load) — these are talking-time estimates, not stopwatch targets.

---
*Pair this with `PROJECT_PLAYBOOK.md` for the "why"/"how it works" depth behind every stop above. Good luck.*
