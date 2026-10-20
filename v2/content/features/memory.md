---
title: Memory
description: How an APS AI remembers you - why it lost you, what hid you, where you were heading, a diary of every encounter, a memory store your game writes to, and a model of how you play.
local: SeenNearVault, AttackedMe, SeenAtScene, Armed, FoundHiding, S
---
<div class="kicker">Pillar 3 of 4</div>

# Memory

Losing you isn't the end. An APS AI knows **why** it lost you, **what** hid you and **where** you were heading, keeps a diary of every encounter, and learns how you play.

<div class="meta"><span>Works out of the box</span><span>Settings in the profile's <b>Memory</b>, <b>Loss</b> and <b>Spatial</b></span><span>Demo: the <b>Memory</b> wing, M1 to M6</span></div>

::: fast
![Room M6: the guard goes round the back of the cover you hid behind](media/memory/cover.mp4 "Room M6. You break line of sight behind the block. The guard knows what hid you, so it goes straight round to the back of that cover.")
- **On AI Lost** hands you where it last saw you, where it thinks you went, and **what you hid behind**.
- **Get Loss Reason** says **why**: hidden behind something, out of range, a sound that stopped, a scent that faded.
- It keeps **a diary** of each encounter, a **memory store** your game writes to, and a **model of how you play**.
:::

## What it knows the moment it loses you

**On AI Lost** (Target, Last Known, Predicted, Last Cover Actor) is the start of every good search. The guard's *reaction* is your Blueprint; the knowledge comes from APS:

| You get | From | Use it to |
|---|---|---|
| **Where it last saw you** | Last Known, **Get Last Known Position** | The first place to go |
| **Where it thinks you went** | Predicted, **Get Predicted Position** (with `Enable Prediction`) | Cut you off |
| **What hid you** | Last Cover Actor, **Get Last Seen Cover Actor**, **Was Target in Cover** | Look behind that crate |
| **Why** | **Get Loss Reason** | Choose *how* to search |
| **Which way you ran** | **Get Loss Direction** | Follow the trail |
| **How far you could be** | **Get Uncertainty Radius** | A search radius that grows while you hide |

### Why it lost you

![Room M5: hidden behind something, or out of its sight](media/memory/lossreason.mp4 "Room M5. APS records why it lost you: hidden behind something, or out of its sight. This guard searches differently for each.")

| Loss reason | What happened | A good search |
|---|---|---|
| **Occluded** | You broke line of sight behind something | It knows where you hid: just past where you vanished |
| **OutOfRange** | Out of range, or out of the side of its view | Along the way you were going (**Get Loss Direction**) |
| **SoundFaded** | The noise stopped | Where it went quiet; don't chase |
| **ScentLost** | The scent faded | Follow the loss direction like a trail |
| **SensorDropout** | Too dark, cloaked, or blinded | A short look, then patrol |
| **TargetDestroyed** | The actor is gone | Drop it |

![The demo guard's Plan by Loss Reason function](media/cards/memory_loss.webp "How the demo's guard does it (BP_DemoGuard › Plan by Loss Reason): a Switch on Get Loss Reason. Behind something: just past where you vanished. Out of sight: along the way you were going. Gone quiet: where the noise stopped.")

### What hid you

When it loses you from Detected or Tracked, APS traces from the guard's eyes to where you are **before** the event fires, and records the first thing in the way: **Last Cover Actor** on **On AI Lost**, or **Get Last Seen Cover Actor**. It is cleared on every loss, so it is always about this loss. Look behind it.

![The demo guard's Plan by Cover function](media/cards/memory_cover.webp "BP_DemoGuard › Plan by Cover: from the guard, through the middle of the cover, out past its far side.")

### Where you were heading

![Room M1: it predicts where you went](media/memory/predict.mp4 "Room M1. When the guard loses you, it predicts where you went from how you were moving, and looks there first.")

With `Enable Prediction` on (it's off by default: a slow patrolling guard that predicts feels psychic), **Predicted** is where your last run would have taken you, `Prediction Horizon` ahead. The guard measures your velocity from its own samples, so a fast run reads as fast. See [Where it thinks you are](../how-it-works.md#7-where-it-thinks-you-are) for the details.

![The demo guard's Plan by Prediction function](media/cards/memory_prediction.webp "BP_DemoGuard › Plan by Prediction: the predicted spot, stopped short of the first wall on the way.")

## Short-term and long-term memory

- **Short term:** after a loss, confidence fades (Lost → Remembered → Expired). `Min Time in Lost` makes it search at least that long before giving up; `Decay Curve` (or `Default Decay Exponent`) shapes the fade.
- **Long term:** `Long Term Memory Strength` is a second number on the belief, 0 to 1 (read it with **Get Belief Data**). It builds by 0.02 a second while the AI senses you, so it takes long contact to fill, and fades by about 1% a second after (or as `Long Term Decay Curve` says). APS itself doesn't act on it: read it to keep a guard twitchy for a minute after an encounter.
- **Coming back:** while you are Lost or Remembered, each update a sense picks you up again adds `Memory Refresh Bonus` to confidence, so it locks on faster the second time.

| Setting | Default | What it does |
|---|---|---|
| `Min Time in Lost` | 0 | The least time in Lost before it may give up (8 makes it really search) |
| `Memory Refresh Bonus` | 0.1 | Extra confidence per update when it senses a Lost or Remembered target again |
| `Memory Expire Threshold` | 0.05 | Below this, a remembered target is forgotten (Expired) |
| `Default Decay Exponent` | 0.3 | How fast confidence fades with no curve set |

## A diary of every encounter

APS keeps the last **5** encounters with each target. Read them with **Get Recent Episodes** or **Get Last Episode**; clear them with **Clear Episodes**.

An encounter is written when the AI loses you **straight from Detected or Tracked**. With the default Loss settings only Vision and Echolocation do that (they have **direct cut**). A loss that fades down through Suspected first, such as a sound or a scent going quiet, writes no encounter.

| Field | What it holds |
|---|---|
| `How Lost` | The loss reason that time |
| `State when Lost` | Tracked, or only Detected |
| `Location when Lost` | Where |
| `AICamera Direction` | Which way the AI was looking: its own blind spot |
| `Target Flee Direciton` | Which way you ran (the source spells it this way) |
| `Engagement Duration` | **All** the time this target has spent Tracked so far, not just this encounter: it only grows |
| `Peak Threat Level` | The threat level at the moment it lost you (despite the name, not the highest of the encounter) |
| `World Time Stamp` | When: for "was this recent?" |

The payoff: *the last three times I lost this player, they were Occluded within 2 m of the same pillar*, so search there first.

## A memory store your game writes to

![Room M2: it remembers where it caught you](media/memory/remember.mp4 "Room M2. This guard remembers where it found you hiding last time, and checks there first.")

APS gives each AI somewhere to put a thought. **What** goes in and **what it means** are yours: APS doesn't decide that clothing matters, or vehicles, or which hand you swung with.

A memory is a **tag** on a **subject** (an actor, or a place), plus optional data:

| Field | Holds |
|---|---|
| `Tag` | What it is: WoreRed, AttackedMe, DroveTruck |
| `Number` | A count, a strength, a damage total: whatever the tag means |
| `Place` | A location it is about |
| `Related Actor` | Another actor it is about: an accomplice, a vehicle |
| `Count` | How many times this tag was written for this subject: kept for you |
| `Age` | Seconds since it was last written: kept for you |

`Count` and `Age` are the ones that make behaviour interesting: *he has done this four times* and *that was a long time ago* are different beliefs from *he did this*.

| Node | What it does |
|---|---|
| **Make Actor Subject** (Actor), **Make Place Subject** (Location, Place Tag) | Who or where a memory is about |
| **Remember** (Subject, Tag, Number, Place, Related Actor) | Store it. Writing the same tag again updates it and counts up. |
| **Recall** (Subject) | Everything about a subject, newest first |
| **Recall Tag** (Subject, Tag) | One memory: "have I been attacked by this one?" |
| **Has Memory Of** (Subject) | Anything at all? The cheapest check |
| **Forget** (Subject, Tag), **Forget Subject**, **Forget Everything** | Drop one tag, one subject, or the lot |
| **Get Remembered Subject Count** | How many subjects it holds |

There is **no "on recall" event**, on purpose: deciding *when* to remember is the interesting part of your AI. Call **Recall** where your logic wants to know: on detect, in a decorator, when choosing a line of dialogue.

![The demo guard's Plan by Memory function](media/cards/memory_memory.webp "BP_DemoGuard › Plan by Memory: Recall Tag FoundHiding gives the place it found you hiding before; if that is near where it lost you, look there.")

::: deep A witness who builds a case
None of this is APS logic: it is what you write, with the store APS gives you.

```
On AI Detect (Target)
  → Make Actor Subject (Target) → S
  → Remember (S, "SeenAtScene", Place: Target's location)
  → Branch: holding a weapon? → Remember (S, "Armed")

On AI Damaged (Instigator, Amount)
  → Make Actor Subject (Instigator) → S
  → Remember (S, "AttackedMe", Number: Amount)
```

Later, deciding how to react:

```
Recall Tag (S, "AttackedMe") → Memory
  → Count ≥ 3   → not a suspect any more: a threat
  → Age > 120   → a while ago: challenge rather than open fire
```

Three strikes and a two-minute cool-off are yours; APS supplied Count, Age, and somewhere to put AttackedMe. Swap the tags and the same code is a shopkeeper who remembers shoplifters, or a detective who remembers what you wore.
:::

| Setting | Default | What it does |
|---|---|---|
| `Memory Max Subjects` | 32 | Subjects per AI; past this the least recently written goes |
| `Memory Max Tags Per Subject` | 16 | Tags per subject; past this the oldest goes |
| `Memory Retention Seconds` | 300 | A subject untouched this long is let go |

::: info It lasts for the session
No save file: a freshly spawned AI has met nobody and remembers nothing. On purpose: an AI that already knows the player when it spawns is hard to reason about and to test. To keep memories across a save, **Recall** what you care about into your own save game and **Remember** it back on load.
:::

## It learns how you play

An AI that notices you always crouch, always break away behind it, always hide behind the same crate, and starts checking there first. This is the **player model**, and it is automatic (`Enable Player Behavior Model`, on by default).

**It is fair by design:** it only records what the AI could perceive. It never reads your input. It watches your speed and stance while it can see you, and records where it lost you. If it never saw you crouch, it doesn't know you crouch.

Read it with **Get Player Behavior Model** (Target):

| Field | What it measures |
|---|---|
| `Crouch Ratio` | Share of observed time you were crouched or prone (from your posture: a Character's crouch, an APS Target Component's stance, or your stance adapter). Only with no posture to read does speed decide: slower than `Player Crouch Speed Threshold` (120) counts, standing still included. |
| `Sprint Ratio` | Share faster than `Player Sprint Speed Threshold` (500) |
| `Walk Ratio` | Everything else |
| `Stealth Ratio` | Share of encounters that ended with you **behind** the AI (more than about 107° off its facing) |
| `Aggression Ratio` | The rest: encounters that ended with you in front. It and Stealth Ratio always add up to 1. |
| `Recent Hide Locations` | Up to 5 **different** places it lost you (each more than 2 m from the others) |
| `Engagement Count` | Encounters observed |
| `Has Enough Data` | True once `Engagement Count` reaches `Min Engagements Required` (3) |

**Always check Has Enough Data** before adapting: it stops the AI concluding anything from one encounter.

- It observes while you are **Detected or Tracked**. An encounter **closes, and the ratios update, only when Tracked turns into Lost**. One that peaks at Detected and fades rolls into the next; a cautious player who never lets it reach Tracked teaches it nothing.
- So mid-fight you read the *previous* encounters: established history, which is what you want to act on.
- **Reset Player Behavior Model** (Target) forgets it all: a story beat, a difficulty reset, an accessibility option. Like memory, it lasts for the session.

::: warning Custom Behavior Ratios stays empty in APS 3.0
The model has a `Custom Behavior Ratios` map, but no node (or anything in APS) records into it. Keep your own counts in the memory store instead: **Remember** with a tag and read `Count`.
:::

![The demo guard's Plan by Habits function](media/cards/memory_habits.webp "BP_DemoGuard › Plan by Habits: once it has seen enough escapes (Has Enough Data), the place it lost you before that is nearest to where it lost you now.")

**Adapt behaviour, not numbers.** Secretly sharpening the AI's eyes against a sneaky player feels like cheating, even when players can't name it. Change *where it looks* instead: patrol routes, facing, search order, how long it lingers. And let the player see it: a line of dialogue ("not this time"), a changed patrol. Adaptation nobody can perceive is just the game getting harder for no reason.

## APS and Unreal's AI Perception

| | Unreal AI Perception | APS |
|---|---|---|
| Losing you | Stops reporting you | Why, what hid you, where you were heading |
| A search radius | None | Grows while you hide |
| Encounters | None | The last 5 per target |
| A memory | None | Tags on actors and places, with count and age |
| How you play | None | Crouch, sprint, break-away and hiding spots, fair by design |

::: try M1 to M6
In the demo, take the **Memory** door from the hub. Each room is a getaway: break line of sight and watch where the guard looks. M1 predicts, M2 remembers, M3 learns your favourite exit, M4 never searches the safe room, M5 searches by loss reason, M6 checks behind your cover.
:::
