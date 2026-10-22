---
title: How APS thinks
description: The model behind APS on one page - confidence, how senses combine, the seven states, why it lost you, awareness, attention, where the AI thinks you are, memory, threat, emotions and the perception tick.
---
<div class="kicker">Start here</div>

# How APS thinks

Read this once and the rest of APS explains itself. It is the model every page builds on.

<div class="meta"><span><b>10 minutes</b> to read</span><span>No setup</span><span>Formulas folded under <b>Go deeper</b></span></div>

::: fast
<ol class="flow">
<li><b>Senses</b><span>Each sense gives a 0 to 1 confidence for each target, on every perception tick.</span></li>
<li><b>Fusion</b><span>The strongest sense sets the level; every other sense that agrees adds a bonus.</span></li>
<li class="hi"><b>Belief</b><span>Smoothed into one belief per target: confidence, state, where it is, threat.</span></li>
<li><b>Events</b><span>Each change of state fires a Blueprint event.</span></li>
<li><b>Your Blueprint</b><span>Decides what to do. APS never moves your AI.</span></li>
</ol>

- **Confidence**, 0 to 100%, is how sure the AI is that a target is there. It climbs while a sense has you and fades when none does.
- It moves each target through **seven states**: Undetected, Suspected, Detected, Tracked, Lost, Remembered, Expired.
- When it loses you, it knows **why** and **where**, and it keeps a memory of you.
:::

## The system in one picture

<ol class="flow">
<li><b>Gather</b><span>Who could it perceive? Every Pawn in range, plus actors you registered.</span></li>
<li><b>Senses</b><span>Vision, hearing, smell, touch, vibration, damage, pain, echolocation.</span></li>
<li><b>Fusion</b><span>Best sense plus corroboration.</span></li>
<li class="hi"><b>Memory engine</b><span>Smoothing, decay and the seven states.</span></li>
<li><b>Belief record</b><span>One per target: everything it believes.</span></li>
<li><b>Brain</b><span>Where you are, threat, emotions, squad sharing.</span></li>
<li><b>Events and nodes</b><span>For your Blueprint or Behavior Tree.</span></li>
</ol>

The shape to remember: **senses produce numbers, the core turns numbers into belief, belief fires events, and your code decides what to do.** Everything is set on one asset per kind of AI, the **Perception Profile**.

## 1. Confidence

Every sense, on every perception tick, gives a number from **0 to 1** for every target it can perceive: how strongly that sense believes the target is there right now.

- Vision at 5 m in bright light, target fully in view: around 0.9.
- Vision at 30 m, only a shoulder showing past cover: around 0.15.
- Hearing a footstep two rooms away through a wall: around 0.2.
- Being shot: around 1.0.

Confidence is not distance and it is not visibility. It already accounts for distance, angle, light, cover, how fast the target moves and the sense's own quirks. The [Confidence](features/confidence.md) page shows each of these in the demo.

## 2. How senses combine

Senses don't average and they don't multiply. **The strongest active sense sets the level, and each other active sense adds a small flat bonus.**

<div class="bars">
<div class="bar"><span>Vision</span><i style="--v:80"></i><em>0.80: the strongest sense sets the level</em></div>
<div class="bar"><span>Hearing</span><i style="--v:30"></i><em>0.30: active, adds the 0.10 bonus</em></div>
<div class="bar"><span>Smell</span><i style="--v:20"></i><em>0.20: active, adds the 0.10 bonus</em></div>
<div class="bar off"><span>Touch</span><i style="--v:0"></i><em>0.00: silent, adds nothing</em></div>
<div class="bar total"><span>Fused</span><i style="--v:100"></i><em>0.80 + 2 &times; 0.10 = 1.00</em></div>
</div>

| Situation (`Corroboration Bonus` 0.1) | Fused |
|---|---|
| Vision 0.8, nothing else | **0.80** |
| Vision 0.8 + Hearing 0.3 | **0.90**: hearing backs up what it sees |
| Vision 0.8 + Hearing 0.3 + Smell 0.2 | **1.00** |
| Hearing 0.3 alone | **0.30** |
| Vision 0 (blocked) + Hearing 0.3 | **0.30**: a blind sense never drags the total down |

Two rules follow, and they matter:

- **A silent sense costs nothing.** Giving a guard smell can't make it worse at seeing. Senses only ever add.
- **Agreement is what makes multi-sense AI feel smart.** Something heard *and* half-seen is surer than either alone, as it is for people.

Each sense's weight is in the profile's `Sense Weights`: a guard dog might have Smell 1.5 and Vision 0.6.

### Rise, hold, decay

The fused value is smoothed into **Smoothed Confidence**, and that is the value everything else uses: the states, the events, your meter.

<figure class="fig">
<svg viewBox="0 0 680 290" role="img" aria-label="Smoothed confidence over time: it rises while a sense is active, holds, then decays once every sense is silent">
<g class="thr"><line x1="120" y1="118" x2="640" y2="118" stroke="#ff6b5e"/><line x1="120" y1="173" x2="640" y2="173" stroke="#ffb454"/><line x1="120" y1="217" x2="640" y2="217" stroke="#f4d27a"/></g>
<text x="112" y="122" text-anchor="end">Track 0.60</text><text x="112" y="177" text-anchor="end">Detect 0.35</text><text x="112" y="221" text-anchor="end">Suspect 0.15</text>
<line class="ln" x1="120" y1="30" x2="120" y2="250"/><line class="ln" x1="120" y1="250" x2="640" y2="250"/>
<text class="m" x="112" y="34" text-anchor="end">1.0</text><text class="m" x="112" y="254" text-anchor="end">0</text>
<line class="grid" x1="340" y1="30" x2="340" y2="250"/><line class="grid" x1="430" y1="30" x2="430" y2="250"/>
<text class="b" x="240" y="22" text-anchor="middle">RISE</text><text class="b" x="385" y="22" text-anchor="middle">HOLD</text><text class="b" x="535" y="22" text-anchor="middle">DECAY</text>
<path class="area" d="M140,250 C230,250 270,58 340,48 L430,48 C470,48 500,95 535,135 S610,228 640,239 L640,250 Z"/>
<path class="curve" d="M140,250 C230,250 270,58 340,48 L430,48 C470,48 500,95 535,135 S610,228 640,239"/>
<text class="m" x="285" y="276" text-anchor="middle">a sense is active: it rises or holds, never falls</text>
<text class="m" x="535" y="276" text-anchor="middle">every sense silent: it decays</text>
</svg>
<figcaption>While any sense is active, confidence never goes down: it rises or holds. It only fades once every sense is silent.</figcaption>
</figure>

The rule that surprises people: **while any sense is active, confidence never falls.** Ray sampling makes the raw value dip a few percent between ticks; holding stops that noise from making the AI flicker.

::: deep The smoothing formulas
**Rising** (fused above smoothed, a sense active):

```
Smoothed = Lerp(Smoothed, Fused, clamp(ConfidenceRiseRate × dt, 0, 1))
Smoothed += DwellRate × Fused × dt
DwellRate = Lerp(StandingDwellRate, MovingDwellRate, clamp(TargetSpeed / 600, 0, 1))
```

**Holding** (fused at or below smoothed, a sense still active): nothing changes.

**Decaying** (no sense active, or fused below 0.02):

```
no curve:    Smoothed ×= exp(−DefaultDecayExponent × SenseDecayMultiplier × dt)
with curve:  Smoothed = Lerp(Smoothed, LastActiveConfidence × DecayCurve(TimeSinceLastSensed),
                             clamp(SenseDecayMultiplier × dt, 0, 1))
```

SenseDecayMultiplier is the **Confidence Decay Multiplier** in the profile's Loss settings for the sense that was last dominant.
:::

::: warning Two Fusion settings do nothing in APS 3.0
`Confidence Decay Smoothing` and `Confidence Reduce Delay` are on the profile but no code reads them. Use `Confidence Rise Rate` and each sense's `Confidence Decay Multiplier` instead.
:::

## 3. The seven states

Each target sits in exactly one of seven states, and each change fires a Blueprint event. The [Confidence](features/confidence.md#seven-states-one-event-each) page plays them live.

| State | When | A typical reaction |
|---|---|---|
| **Undetected** | Below `Suspect Threshold` (0.15) | Nothing |
| **Suspected** | At or above 0.15 | Turn the head, "what was that?", walk over |
| **Detected** | At or above `Detect Threshold` (0.35) | Confirmed: alert, call it out, take cover |
| **Tracked** | At or above `Track Threshold` (0.60) for `Min Track Duration` (0.5 s) | Full engagement: chase, shoot, flank |
| **Lost** | Every sense went silent and the grace time ran out | Search. **Read the loss reason to know how.** |
| **Remembered** | Fading in memory | Patrol near where you were, stay alert |
| **Expired** | Below `Memory Expire Threshold` (0.05) | Forgotten: back to normal |

The event fires on **every** entry into a state, going up or down. When a Tracked target steps back to Detected, **On AI Detect** fires again; dropping back to Undetected fires **On AI Forget**. Keep a "first time" flag in your Blueprint if you only want the first one.

### Grace time and direct cut

When every sense goes quiet, the AI doesn't drop you at once. Each sense has a **grace time**, and says whether losing it may **cut straight to Lost**:

| Sense | Grace | Direct cut | Decay multiplier | Why |
|---|---|---|---|---|
| Vision | 0.3 s | Yes | 3.0 | You ducked behind a wall: gone, at once |
| Echolocation | 0.6 s | Yes | 2.0 | The pulse missed |
| Touch | 0.5 s | No | 2.0 | Contact ended, it fades |
| Hearing | 3.0 s | No | 1.0 | The sound still rings in its ears |
| Damage | 8.0 s | No | 0.5 | It remembers being shot for a while |
| Smell | 20.0 s | No | 0.3 | The scent lingers |
| Vibration | 0.0 s | No | 5.0 | You stopped moving: the signal is gone |

**Direct Cut** jumps straight to Lost. Without it, confidence steps down through Tracked, Detected and Suspected first, which reads as the AI slowly losing certainty. All of these are on the profile's **Loss** settings (`Vision Loss`, `Hearing Loss` and so on).

**Which sense's row applies:** the sense that had the target last, with one overlap. While Vision (or Echolocation) still perceives the target, its row applies even if another sense leads. When it loses the target but hearing still has it, vision's row is kept for vision's own grace time, so a moment's overlap doesn't turn ducking behind cover into a slow fade. After that, hearing's row applies: its 3 s grace and its gradual fade.

::: deep The exact transition rules
| From | To | When |
|---|---|---|
| Undetected | Suspected | `C ≥ Suspect Threshold`; also counts a detection |
| Suspected | Detected | `C ≥ Detect Threshold` |
| Suspected | Lost | No sense active and the grace time ran out, with or without direct cut |
| Suspected | Undetected | A sense is active but `C < Suspect Threshold × 0.5` |
| Detected | Tracked | A sense is active, `C ≥ Track Threshold`, and at least `Min Track Duration` in Detected |
| Detected | Lost | No sense active, grace ran out, and the sense allows a direct cut |
| Detected | Suspected | `C < Suspect Threshold − 0.04` |
| Tracked | Lost | No sense active, grace ran out, and the sense allows a direct cut |
| Tracked | Detected | Grace ran out without direct cut, or `C < Detect Threshold − 0.04` |
| Lost | Detected | A sense is active and `C ≥ Detect Threshold`; clears the loss reason |
| Lost | Remembered | `C < Suspect Threshold` and at least `Min Time in Lost` in Lost |
| Remembered | Detected | A sense is active and `C ≥ Detect Threshold` |
| Remembered | Expired | `C < Memory Expire Threshold` |
| Expired | Undetected | The target is perceived again: the belief starts over from nothing |

Two things follow:

- **A sense without direct cut never jumps from Detected or Tracked straight to Lost.** It always steps down first: that is the gradual fade.
- **Finding you again needs the Detect threshold, not Suspect.** A faint re-contact won't pull a target out of Lost.

Steps down from Detected and Tracked have a **0.04 margin**: confidence must fall that far below the threshold before the state drops (Tracked to Detected with Detect at 0.35 happens at 0.31). That stops the state flickering on a boundary. Suspected falls back to Undetected only below half the Suspect threshold.
:::

## 4. Why it lost you

When a target goes Lost, APS records **why**. Read it with **Get Loss Reason** and branch your search on it.

| Loss reason | What happened | What your AI should do |
|---|---|---|
| **Occluded** | Broke line of sight behind something | It knows where you hid: go to the last known position and search the cover there |
| **OutOfRange** | Out of range, or out of the side of the view cone | Head toward the last known position and widen the search; use **Get Loss Direction** |
| **SoundFaded** | The noise stopped | Check the sound's area; don't chase |
| **ScentLost** | The scent faded | Follow the loss direction like a trail |
| **SensorDropout** | The signal just stopped: too dark, cloaked, blinded by pain | A short look, then back to patrol |
| **TargetDestroyed** | The actor is gone | Drop the target |
| **Unknown** | No better answer | A general area search |

The reason comes from the **last sense that had the target**. If a guard could still hear your footsteps fading after you slipped out of sight, the loss is **SoundFaded**, not Occluded. Vision answers from what blocked its last look: a wall, too few visible points or too little exposure is Occluded; distance or the edge of the cone is OutOfRange; a target in view but too faint, cloaked or blotted out by pain is SensorDropout.

This one branch is the difference between an AI that runs to the corner you hid behind and one that wanders in a circle. The [Memory](features/memory.md) page shows it in the demo.

**Get Loss Direction** is recorded at every loss: the target's measured direction of travel at that moment. It is zero when the target wasn't moving, so check **Is Nearly Zero** before using it.

## 5. Awareness

The states are **per target**. Awareness is **per AI**: one level from its top target's confidence.

| Awareness | When the top target's confidence is |
|---|---|
| **Fully Aware** | At or above `Full Aware Threshold` (0.85) |
| **Alerted** | At or above `Track Threshold` (0.60) |
| **Suspicious** | At or above `Detect Threshold` (0.35) |
| **Peripheral** | At or above `Suspect Threshold` (0.15) |
| **Unaware** | Below that, or no targets |

Awareness reuses the state thresholds, so tune those and awareness follows. Use it for alert music, weapon-ready poses, a HUD meter: **Get Awareness Level**, **Get Awareness Level for Target**, and **On AI Awareness Changed**.

## 6. Attention: the target it commits to

An AI can hold beliefs about many targets at once (up to `Max Tracked Targets`, 16 by default). It can only chase one.

- **Get Top Target** is whoever scores highest *this update*. It can flicker when two are close.
- **Get Attention Target** is the one the AI **commits to**. It is sticky on purpose:
  - `Attention Stickiness Time` (2 s): the least time before it will even consider switching.
  - `Attention Switch Threshold` (0.2): how much better a rival must score to take its attention.

Once the stickiness time has passed, attention also moves to the top target when its own target is Lost, Remembered or Expired, however small the gap. You can force it at any time with **Force Attention Target** (when the player shoots this AI, say). **On Attention Changed** gives the old and new target so you can re-plan.

Only targets the AI has **noticed** (Suspected or more) take attention or count as the top target; one that falls back to Undetected lets attention go. A focus set with **Force Attention Target** on someone not noticed yet holds for the stickiness time.

::: warning Attention is not "sure"
The attention target can be someone the AI only **suspects**, or one of its own teammates once it has noticed them. So don't chase **Get Attention Target** as it is: take the target from **On AI Detect**, or check it first (**Get Awareness Level for Target** is Suspicious or more, and **Get Relationship** isn't Teammate or Friendly). Attention is for choosing **between** targets you know about.
:::

::: deep Which target is "top": the sort score
```
SortScore = Confidence × Sort Weight Confidence   (0.5)
          + Recency    × Sort Weight Recency      (0.3)
          + Proximity  × Sort Weight Proximity    (0.2)
```
Raise the proximity weight for melee enemies, the confidence weight for snipers. These are in the profile's **Performance** settings.
:::

## 7. Where it thinks you are

Even with every sense silent, APS keeps a model of where you are, and it grows less sure over time.

| Value | What it is |
|---|---|
| **Last Known Position** | Where the active sense with the **most precise position** placed you, not the strongest one: a faint but precise gunshot beats a strong but vague scent. |
| **Estimated Velocity** | Your velocity as the AI measured it, smoothed (`Velocity EMAWeight`). Measured between the AI's own samples over the real time between them; samples more than 1.5 s apart start it afresh. |
| **Estimated Acceleration** | How that velocity has been changing. |
| **Predicted Position** | While sensed: the same as last known. While lost, with `Enable Prediction` on: where your last run would have taken you, looking `Prediction Horizon` ahead. The acceleration part is capped so a noisy reading can't fling the guess past where a run could reach. Only when you were moving faster than about 10 cm/s. |
| **Uncertainty Radius** | While sensed: shrinks toward 0 as the position gets more precise. While lost: grows at `Uncertainty Growth Rate` (50 cm/s) up to `Max Uncertainty Radius` (500 cm). With `Velocity Scaled Uncertainty`, a target that was moving faster than 6 m/s makes it grow faster: twice as fast at 12 m/s, three times at 18 m/s and above. A normal run (Unreal's default top speed is 6 m/s) doesn't change it. |

The uncertainty radius is a ready-made **search radius**: feed it to an EQS query or **Get Random Reachable Point in Radius** and the search widens the longer you stay hidden.

Prediction is **off by default**, because for a slow patrolling guard it makes the AI feel psychic. Turn it on for pursuers. With it off, the predicted position always equals the last known one.

::: deep The prediction formula
```
Predicted = LastKnown + v·T + ½·a·T²,   T = clamp(Prediction Horizon, 0.1, Max Prediction Time)
```
The acceleration term is capped so that over that time it can change the speed by at most half.
:::

## 8. Memory

Two layers, plus a diary:

- **Short term:** the smoothed confidence fading after a loss (the slide from Lost to Remembered), shaped by `Decay Curve`, or `Default Decay Exponent` without one.
- **Long term:** `Long Term Memory Strength`, a second number on the belief (read it with **Get Belief Data**). It builds slowly while the AI senses you and fades far more slowly than confidence. APS itself doesn't act on it: read it to keep an AI twitchy for a minute after an encounter.
- **Episodes:** the last **5** encounters with each target, read with **Get Recent Episodes** or **Get Last Episode**: how it was lost, where, which way it was looking, which way you ran. One is written each time it loses you straight from Detected or Tracked (by default a Vision or Echolocation loss).

`Memory Refresh Bonus` gives a head start when it finds you again, and `Min Time in Lost` makes it search for at least that long before giving up. The [Memory](features/memory.md) page covers all of it, with the demo's Memory wing.

## 9. Threat and emotion

**Threat** is a score per target, from 0 to 1, mapped onto **None, Low, Medium, High, Critical**. It combines how sure the AI is, how much damage the target has done, how many senses agree, who it is, and whether it is in contact right now.

**Emotion** is five values on the AI itself, each 0 to 1: **fear, aggression, curiosity, alertness, panic**. Each rises and falls with what is happening; the strongest one above `Emotion Active Threshold` is the dominant emotion. Set every emotion's cap to 0 and a robot feels nothing, without touching code. The [Emotions & pain](features/emotions.md) page explains every rule.

::: deep The threat formula
```
ThreatScore = SmoothedConfidence          × Threat Weight Confidence       (0.35)
            + clamp(DamageReceived / 100) × Threat Weight Damage Received  (0.30)
            + (ActiveSenses / 8)          × Threat Weight Senses           (0.15)
            + RelationshipModifier        × Threat Weight Relationship     (0.10)
            + ApproachModifier            × Threat Weight Approach         (0.10)
```

- **100 damage fills the damage term.** Scale your damage, or reweight.
- **The senses term divides by 8**, the most sense slots an AI can have, not the senses this AI has: a two-sense guard adds at most 0.25 of that weight.
- **Relationship:** Feared 1.5, High Value 1.2, Enemy 1, Unknown 0.5, Neutral 0.3, Friendly and Teammate 0.
- **The approach factor is in effect a constant in APS 3.0:** 1 while the target is Detected or Tracked, 0 otherwise. With its default weight it is a flat bonus for being in contact, not a measure of closing speed.

Friendly and Teammate targets are always threat None, however sure the AI is or however much they hurt it; so are Expired ones. While a target is unsensed, its damage term fades at `Threat Damage Decay Rate` and drops to zero below 1 point. The level is the highest of `Threat Threshold Low` (0.15), `Medium` (0.35), `High` (0.60) and `Critical` (0.85) that the score reaches.
:::

## 10. The perception tick

APS doesn't run every frame. The component ticks, but perception only runs every `Base Update Interval` (0.1 s), multiplied by the AI's level of detail (below) and by any Quality Profile.

<ol class="flow">
<li><b>Gather</b><span>Candidate targets, at most 5 times a second.</span></li>
<li><b>Prepare senses</b><span>Accumulators, contacts, health.</span></li>
<li><b>Own senses</b><span>Pain fires its event.</span></li>
<li class="hi"><b>Each target</b><span>Every sense, then pain dulling, fusion, fairness rules and evidence.</span></li>
<li><b>Memory</b><span>Smoothing, decay, state changes.</span></li>
<li><b>Where you are</b><span>The spatial model.</span></li>
<li><b>Threat</b><span>And relationships.</span></li>
<li><b>Player model</b><span>What it learns about you.</span></li>
<li><b>Brain</b><span>Emotions, awareness, attention, squad sharing.</span></li>
<li><b>Events</b><span>Your Blueprint events fire.</span></li>
<li><b>Housekeeping</b><span>Every `Maintenance Interval` (0.5 s).</span></li>
</ol>

Two consequences:

- **Events fire on the perception tick, not the frame.** At 0.1 s an event can be up to 100 ms late. That is fine for AI behaviour, and it is why APS scales.
- **Perception runs on the server only.** Clients skip it; see [Multiplayer](guides/multiplayer.md).

## 11. Beliefs about places

A belief doesn't have to be about someone. A gunshot with no known shooter, a body, a forced lock: these are beliefs about a **place**, with the same states and their own confidence.

- **Emit Sound at Location** and discovered [evidence](features/search.md) create them for you.
- **Report Location Belief** (location, tag, confidence, accuracy) creates one from your own logic. Reports close together with the same tag merge into one.
- **On Location Belief Changed** fires on every change, with the location, tag, state and confidence. **Get Strongest Location Belief** and **Get Location Beliefs** read them back.

Places never take the AI's attention, change its awareness or stop **On AI All Clear**, so a noise can't steal focus from a person or keep the AI from standing down.

## 12. Level of detail

Every AI is scored for **significance**, 0 to 1, each subsystem tick, and the score picks its level of detail (its tier). No setup needed.

| Score | Tier | Perception runs | |
|---|---|---|---|
| 0.75 and up | **0** | every interval | Full rate |
| 0.50 and up | **1** | every 2 intervals | |
| 0.30 and up | **2** | every 5 intervals | |
| 0.15 and up | **3** | every 20 intervals | The component ticks only every 0.1 s |
| below | **4** | not at all | Suspended (unless the crowd tier is on); memory still fades; ticks every 0.25 s |

Two things follow, and both surprise people:

- **An idle AI never reaches tier 0.** With nothing going on its score tops out at 0.6: tier 1 out to 50 m, tier 2 to 150 m, tier 3 to 225 m, suspended beyond.
- **An engaged AI almost never drops out of tier 0.** Once it is Suspicious or more alert, it stays at full rate out to about 260 m, and tier 1 beyond. A chase doesn't stutter because the camera is far away.

*Viewer* means every local player camera, so split-screen and listen servers work; a dedicated server has no viewer and scores every AI as if at zero distance. Tiers also filter sounds: a sound type whose `Max LODTier` is 1 is ignored by a tier 2 AI. Replace the score with your own **APS Significance Policy**: see [Performance & crowds](guides/performance.md).

::: deep The significance score
```
Significance = 0.6 × (1 − distance to the nearest viewer / 30000 cm)
             + 0.55 if the AI is Suspicious or more alert
             + 0.25 × (awareness level / 4)
```
:::

## 13. Who it can perceive

- **Pawns are automatic**: no registration needed.
- **Other actors** (a security camera's target, a thrown item) call **Register Perceivable Actor**, or carry an **APS Target Component** with auto-register on.
- **The gather range** is the largest of `Vision Max Range`, `Hearing Max Range` and each sense's own reach (`Vibration Detect Range`, `Echo Range` and so on).
- An AI never perceives a Pawn with its own controller.
- Targets it already believes in stay on its list even out of range, so memory fades smoothly instead of freezing.
- Candidates come from a grid the subsystem rebuilds 5 times a second (15 m cells), so finding them costs the same however many AI and Pawns there are. The console variable `aps.UseSpatialIndex 0` switches back to scanning every Pawn, for comparing.

::: deep Where everything lives, and what happens in a crowd
| State | Lives in | For how long |
|---|---|---|
| Each target's belief | The AI's ledger of belief records | Until Expired and its slot is reused |
| Emotions | The APS Core | The component's life |
| Squads and roles | The world's APS subsystem | The world's life |
| Light, wind, weather | The world's APS subsystem | The world's life |
| Never-search zones | The world's APS subsystem | The world's life |
| Player models | The APS Core, per target | The component's life |
| The memory store | The APS Core, per subject | Bounded by `Memory Retention Seconds` |
| Scripted evidence | The APS Core, per target | Until it expires or is removed; kept even when the target leaves the ledger |
| Place beliefs | The ledger, like any target | Until Expired |
| Recorded frames | The APS Core | The recording window |

**The ledger is set up once** at `Max Tracked Targets` slots and reuses them, so steady-state perception allocates no memory. When it is full, a new target replaces the lowest-scoring Expired or Remembered slot, or an active one with a worse sort score.

**In a crowd** (more candidates in range than slots), slots go by priority first, score second:

1. Something that just **hit or touched** the AI.
2. Something it **perceives right now**.
3. Something it **hasn't looked at yet**.
4. An **ally** (Friendly or Teammate in **APS Relationship**, or the same team id with no rule).
5. Something it **looked at and found nothing of**: benched for a short, crowd-sized time, so slots rotate through a crowd instead of staying with whoever stands closest.

So a player in plain view is picked up even with more bystanders than slots around the guard, and a shot from out of range is always believed. Noises (place beliefs) never push out an actor it perceives.
:::

## 14. Make it your own

| You want to | Do this |
|---|---|
| Add a sense | A child of **Sense Unit**: see [Custom senses](guides/custom-senses.md) |
| Change how targets are ranked | The sort weights in the profile's **Performance** settings |
| Raise confidence from script | **Set Target Confidence** (raises only) |
| Lower, cap or clear belief from script | **Add Target Evidence** |
| Swap perception for a state (asleep, alerted) | **Set Profile** while playing |
| Read everything about a target | **Get Belief Data** |
| Change how senses combine, how threat is scored, or what gets attention | A policy on the profile: [Policies & adapters](guides/policies.md) |
| Tell APS where health or posture lives | An adapter interface: [Policies & adapters](guides/policies.md) |
| Scale cost without resetting belief | A **Quality Profile** with **Set Quality Profile** |
| Decide which AI get the CPU | An **APS Significance Policy**: [Performance & crowds](guides/performance.md) |

::: deep The sense contract
Every sense, built in or yours, follows the same four steps. The APS Core never needs to know which sense it is talking to, which is why adding one changes nothing else.

| Step | Called | For |
|---|---|---|
| Pre Tick | Once per AI, per tick | Accumulators, contacts, health |
| Evaluate | Once per target | Confidence, position, precision |
| Delegate payload | When active | Which built-in event to fire |
| Post Tick Flush | After all targets | Clearing per-tick caches |

A sense also states how it is lost (grace time, direct cut, loss reason), how far it reaches and which stimuli it listens to.
:::

::: deep Threads and cost
- Everything runs on the **game thread**. `Async Vision Traces` issues sight traces asynchronously and reads them one evaluation later; it falls back to normal traces when surface transmission or more than one occlusion channel is set.
- The main cost is **line traces**: sample points × occlusion channels, per target, per evaluation.
- Sounds reach only the AI near them: a cheap distance check first.
- An AI with nothing in range costs a distance check and an early exit.
- The subsystem's `Max Perception Updates Per Frame` caps how many AI run a full pass in one frame. The rest wait their turn with their time intact, and an AI's claim grows every frame it waits, so none is starved.

The [Performance & crowds](guides/performance.md) guide has the numbers.
:::
