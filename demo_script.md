# KSP Crime Intelligence Platform — Demo Script
### "The Raju Kumar Story" — 5 minute live demo

---

## Before you start
- Have the app running and already loaded (dedup takes ~1 second now, so no awkward wait).
- Open the Dashboard (`/`) as your starting tab. Don't click anything yet.
- One person talks, one person drives the mouse/keyboard. Rehearse the handoff so it's not clunky.
- Know your numbers cold: **5,010 FIRs, 106 identity clusters, 121 alias matches, 32 anomalies, 15 districts risk-scored.**

---

## 0:00–0:30 — The Hook

> "Imagine a repeat offender gets arrested five times across five different districts in Karnataka. Each time, he gives a slightly different name — Raju Gowda in Tumakuru, Rajesh K in Mysuru, Raju Kumar in Bengaluru. To five different police stations, these look like five different people with clean records. To us, this is one man who's never been caught."

*(Pause. Don't click anything yet — let the problem land.)*

---

## 0:30–1:00 — The Problem, Fast

> "Karnataka Police handle FIRs district by district. There's no single system that connects identities across districts, flags unusual crime spikes, or predicts where the next spike is coming. We built one — in Python, deployable today, running on real synthetic data modeled on actual Karnataka crime patterns."

Click to **Dashboard**. Let the live FIR ticker run for 2 seconds without narrating — it looks alive on its own.

> "5,010 FIRs. Nine intelligence tools. One connected system."

---

## 1:00–2:15 — The Reveal: Identity Deduplication

Navigate to **Identity Dedup** (`/dedup`).

> "This is the core of the platform. We run every accused name through Soundex phonetic matching, then score similarity on name, age, phone number, and district — including neighboring districts, since offenders often move to adjacent areas, not random ones."

Search or scroll to find **Cluster CLUSTER_0287**.

> "Here he is. Raju Gowda. Rajesh K. Raju Kumar. Raju Naik. Raj Kumar. Five names, five FIRs, five districts — Tumakuru, Mysuru, Bengaluru Urban, Shivamogga, Hubballi-Dharwad. Same phone number pattern, same age bracket, same crime type: Chain Snatching, every time. Our engine links them at **61.7% confidence** — flagged, not buried."

Click into the cluster → **Suspect Profile** page.

> "One click, and an officer sees the entire criminal history as a single dossier, not five disconnected police reports."

---

## 2:15–2:45 — Making It Actionable: PDF Export

On the Suspect Profile page, click **Export Case as PDF**.

> "And because this needs to leave the screen and go into a case file, it exports as an official dossier — aliases, full FIR history, confidence score — ready to hand to an investigating officer or attach to a court filing."

Briefly show the PDF that downloads.

---

## 2:45–3:15 — Seeing the Web: Network Graph

Navigate to **Network Graph** (`/network`).

> "Zooming out — this is what identity fraud looks like at scale across Karnataka. Every connection here is a suspect linked across district lines. This isn't five isolated problems. It's a pattern."

---

## 3:15–4:00 — From Reactive to Predictive: Risk Score + Anomaly Alerts

Navigate to **Risk Score** (`/risk`).

> "Everything so far has been about catching what already happened. This is where we get ahead of it. Every district gets a 0–100 predictive risk score, built from four transparent signals: recent crime trend, crime severity mix, anomaly history, and unresolved case backlog. Not a black box — an officer can see exactly why a district is flagged."

Point to the top-ranked district.

> "Right now, Tumakuru — the same district Raju Gowda was operating in — is flagged high-risk. That's not a coincidence we told the model. That's the model independently surfacing the same threat."

Navigate to **Anomaly Alerts** (`/alerts`).

> "And when something breaks pattern in real time — like Hubballi-Dharwad in October 2018, where robbery cases jumped 136% above that district's own historical average — we catch it with statistical confidence, not guesswork. Z-score of 3.43. That's a genuine outlier, not noise."

---

## 4:00–4:30 — The Close

Return to **Dashboard**.

> "One offender, five names, five districts, zero connections — until now. This platform doesn't just visualize crime data. It thinks the way an investigator thinks: detect the alias, confirm the pattern, predict where it happens next, and hand over a case file that's ready to act on."

> "Nine connected tools. One pipeline. Built in Python, ready to deploy today."

*(Stop talking. Let it sit for a second before Q&A.)*

---

## Anticipated Judge Questions — Have Answers Ready

**"Is this real data?"**
> "Synthetic data, generated to statistically mirror real Karnataka crime patterns — district distributions, crime type frequency, seasonal patterns. The pipeline is built to run on real KSP data with zero code changes, just a different CSV."

**"How accurate is the identity matching?**
> "We use a weighted confidence score — 35% phone number, 30% name similarity, 20% age, 15% district — and only flag matches above threshold. We deliberately show the confidence percentage rather than a binary yes/no, because an investigator should verify before acting, not blindly trust the system."

**"Can this scale to the whole state?"**
> "Yes — the identity matching is blocked using Soundex, so it doesn't compare every record to every other record. We optimized it to run 5,010 records in about a second; the same approach scales to hundreds of thousands."

**"What would it take to actually deploy this for KSP?"**
> "Swap the synthetic CSV for a live FIR database connection, add authentication for officer logins, and it's production-ready. The architecture doesn't change."

---

## Rehearsal Checklist
- [ ] Run through it twice out loud, with a timer, before the real thing
- [ ] Practice the mouse handoff between speaker and driver
- [ ] Have a backup screen recording in case live wifi/demo fails
- [ ] Know the exact cluster ID (CLUSTER_0287) and don't rely on search working live — bookmark the URL directly: `/suspect/CLUSTER_0287`
- [ ] Assign one teammate to watch the clock and give a silent 30-seconds-left signal
