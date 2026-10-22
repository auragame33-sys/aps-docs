---
title: Cheat sheet
description: Everything you use daily on one page - setup, the words, the ten nodes and eight events, loss reasons, what feeds each sense, default thresholds, the difficulty and performance dials, quick fixes and the things that surprise people.
local: DA_Profile_MyAI, DA_Sound_Footstep
---
<div class="kicker">Reference</div>

# Cheat sheet

Everything you use daily, on one page.

## Setup in five lines

```
1. Content Browser › Miscellaneous › Data Asset › Perception Profile    DA_Profile_MyAI
2. The AI's Pawn › Add Component › APS Core                              assign the profile
3. APS Core › Details › Events › +                                      On AI Detect, On AI Lost
4. The player › Add Component › APS Target Component                     (optional: sample points, stance, light)
5. A footstep notify › Emit Sound (Self, DA_Sound_Footstep)              without it, hearing hears nothing
```

## Ten words

| Word | Meaning |
|---|---|
| **Confidence** | 0 to 1: how sure the AI is that a target is there. Every sense gives one per target each time it runs. |
| **Fused**, **Smoothed** | Fused is this update's combination of the senses. Smoothed drives everything: it rises while a sense reports, holds, and fades only once every sense is silent. |
| **States** | Undetected, Suspected, Detected, Tracked, Lost, Remembered, Expired: per target, with an event for each |
| **Awareness** | The AI's overall alert level, from its top target: Unaware, Peripheral, Suspicious, Alerted, Fully Aware |
| **Attention target** | The one target it focuses on, among those it has noticed. Sticky, so it doesn't flick between two. It may only be suspected: check the state before acting on it |
| **Loss Reason** | Why it lost you: OutOfRange, Occluded, SoundFaded, ScentLost, SensorDropout, TargetDestroyed. It decides how to search. |
| **Belief Record** | Everything it holds about one target; **Get Belief Data** returns it |
| **Profile** | The data asset with every perception setting for one kind of AI |
| **Evidence** | A scripted floor, ceiling, reduction or reset on belief: a disguise, an alibi, a cutscene |
| **Place belief** | A belief about a location, not an actor: a noise nobody made |

## Ten nodes

| Node (APS Core) | Gives | For |
|---|---|---|
| **Get Attention Target** | Actor | Its focus among the targets it has noticed. Chase it only at Suspicious or more (**Get Awareness Level for Target**) |
| **Get Last Known Position** | Vector | Where to search |
| **Get Loss Reason** | ELossReason | **How** to search: branch on it |
| **Get Uncertainty Radius** | Float | The search radius; grows while you hide |
| **Get Awareness Level** | EAwarenessLevel | Music, weapon poses, the HUD |
| **Get Belief Data** | Belief Record | Everything about one target (a meter: its Smoothed Confidence) |
| **Get Sense Contributions** | Each sense's share | Did it see me or only hear me? |
| **Emit Sound** | | A noise the AI can hear (any Blueprint) |
| **Set Target Confidence** | | Raise belief from script (it never lowers it) |
| **Set Profile** | | Swap the whole perception setup |

## Eight events

| Event | Fires when | Typical response |
|---|---|---|
| **On AI Telegraph** | It's about to notice you | A "Hm?", a head turn |
| **On AI Suspect** | Something is there | Look, walk over |
| **On AI Detect** | It's sure | Alert, take cover, call it in |
| **On AI Track** | Locked on | Chase, shoot |
| **On AI Lost** | Contact broken | Read **Get Loss Reason**, then search |
| **On AI Forget** | It gave up (Expired), or a target fell back to Undetected | Back to patrol |
| **On Attention Changed** | A new focus (maybe one it only suspects) | Re-plan between targets you know are Detected |
| **On AI Damaged** | It was hit | React to an unseen attacker |

Also: **On AI See**, **On AI Hear**, **On AI Smell**, **On AI Feel** (touch) and **On AI Sense Vibration** each time a sense reports; **On AI Remember**; **On AI All Clear** when it believes in nobody any more; **On AI Awareness Changed**; **On AI Think Threat** when a target's threat level changes, and **On Threat Identified** when one rises to High or Critical; **On Target State Changed** for every state change. All events: [Events](events.md).

## More queries

| Node (APS Core) | Gives |
|---|---|
| **Get Top Target**, **Get Top Target Belief** | The best-scoring target it has noticed, this update (it can change often) |
| **Get Targets Sorted by Score** | Every actor it holds a belief about, best first |
| **Get Threat Level** (Target), **Get Highest Threat Level**, **Has Threat at or Above** (Level) | Threat, per target or overall |
| **Get Stimulus Source** (Target) | The sense that **first** made the belief (the current one is the events' Stimulus) |
| **Has Any Detection**, **Get Active Target Count** | Is it aware of anyone; how many actors it is Suspected to Lost about |
| **Get Predicted Position**, **Get Estimated Velocity**, **Get Estimated Acceleration** (Target) | Where it thinks you're going ([Memory](../features/memory.md#where-you-were-heading)) |
| **Get Recent Episodes** (Target) | Its last five encounters with you ([Memory](../features/memory.md#a-diary-of-every-encounter)) |
| **Get Perceived Objects** | Beliefs about things (bodies, forced locks), not someone |
| **Get Location Beliefs**, **Get Strongest Location Belief**, **Report Location Belief**, **Clear Location Belief** | Beliefs about places: read them, add one, drop one ([How APS thinks](../how-it-works.md#11-beliefs-about-places)) |

On the APS Subsystem: **Get Agent Count** (how many APS Cores are running), **Is Perceived as Object** (Actor). On an APS Target Component: **Get Effective Stance**.

## Loss reason → search

| Loss reason | Meaning | The tree should |
|---|---|---|
| Occluded | It went behind something | Go to the last known position, search **that cover** |
| OutOfRange | Walked out of range or the cone | Go there, then on along **Get Loss Direction** |
| SoundFaded | The noise stopped | Look around there: **don't chase** |
| ScentLost | The trail went cold | Follow **Get Loss Direction** like a trail |
| SensorDropout | Too dark, cloaked, blinded, or a sense just stopped | A short look, then patrol |
| TargetDestroyed | The actor is gone | Clear the target |

## What feeds each sense

| Sense | Needs from you | Through walls? |
|---|---|---|
| Vision | Nothing | No (glass and leaves partly, by surface) |
| Hearing | **Emit Sound**: required | Muffled per wall |
| Smell | Nothing | Partly (seeps under doors) |
| Touch | Nothing: wired automatically | n/a |
| Vibration | Nothing for walking; **Report Vibration Event** for blasts | **Yes** |
| Damage | Nothing: wired automatically | **Yes**, any range |
| Pain | **Report Pain from Definition** | n/a |
| Echolocation | Nothing | **Yes** |

## Default thresholds

| Confidence | State | Awareness |
|---|---|---|
| 0.85 and up | Tracked | **Fully Aware** |
| 0.60 and up | **Tracked** | Alerted |
| 0.35 and up | **Detected** | Suspicious |
| 0.25 | **On AI Telegraph** fires | |
| 0.15 and up | **Suspected** | Peripheral |
| below 0.15 | Undetected | Unaware |

Steps down need a 0.04 margin below the line. Tracked also needs `Min Track Duration` (0.5 s) in Detected first.

## Difficulty dial

| Setting | Easy | Normal | Hard |
|---|---|---|---|
| `Suspect Threshold`, `Detect Threshold`, `Track Threshold` | 0.25, 0.50, 0.75 | 0.15, 0.35, 0.60 | 0.10, 0.25, 0.45 |
| `Confidence Rise Rate` | 3 | 5 | 7 |
| `First Spot Reaction Time` | 0.8 | 0.4 | 0.1 |
| `Min Time in Lost` | 3 | 8 | 15 |

Keep cone angles and occlusion the same on every difficulty. [Ready-made AI](../guides/ready-made-ai.md#difficulty)

## Performance dial

| Lever | Effect |
|---|---|
| `Base Update Interval` 0.1 → 0.2 | **Halves** the perception cost |
| The Target Component's `Visibility Samples` 5 → 3 | 40% fewer vision traces |
| `Max Tracked Targets` 16 → 4 | Less memory, less sorting |
| One occlusion channel instead of three | A third of the traces |
| An **APS Quality Profile** | Slower updates, fewer samples, nothing reset |
| `Enable Statistical Tier` | Distant AI stop tracing (and see through walls: keep the threshold at 3) |
| Tier 4 | Suspended by itself, beyond about 225 m for an idle AI |

[Performance & crowds](../guides/performance.md)

## See what it perceives

```
APS Core › Details › APS › View › Show Visualizer      tick it
console: aps.Visualizer 0 | 1 | 2      nothing · everything · status only
         aps.VisualizerPage 0..6       Senses · Memory · Brain · Squad · Events · Player Model · Environment
         aps.Tune VisionMaxRange 5000  a setting on every AI, live
```

The **Senses** page answers most "why doesn't it see me": each sense shows what it reads, or why it reads nothing. A sense draws only if it is in `Sense Classes`: no smell ring means no Smell Sense. [Visualizer & debugging](../features/visualizer.md)

## Quick fixes

| Symptom | Fix |
|---|---|
| Detects nothing at all | No profile assigned, `Sense Classes` empty, or the APS Core is on the controller (it must be on the Pawn) |
| Hears nothing | Nothing calls **Emit Sound** |
| Sees through doors | Add their channel to `Vision Occlusion Channels` (the list replaces Visibility: keep it in) |
| Sees you the instant you step out | `First Spot Reaction Time` 0.3 to 0.5 |
| Sees you before it has turned | `Eye Turn Rate Deg Per Sec` about 200 |
| Forgets instantly | `Vision Loss` Grace Time 0.8 to 1.5 |
| Never forgets | Raise `Default Decay Exponent` |
| Searches in a dumb circle | Branch on **Get Loss Reason** |
| The whole squad knows at once | `Auto Share on Detect` off |
| A client sees nothing | **Get Replicated Perception State** ([Multiplayer](../guides/multiplayer.md)) |
| The cone points at the sky | `Eye Socket Alignment` Automatic |
| Crouching doesn't hide you | `Min Visible Points Crouched` 2, and an **APS Target Component** on the player |
| "Why can't it see me?" | Print **Explain Perception** (Target) |
| A thrown can is ignored | Noises nobody made arrive on **On Location Belief Changed**, not **On AI Hear** |
| A setting seems to do nothing | Some do nothing in APS 3.0: the reference marks them ([Troubleshooting](../help/troubleshooting.md#settings-that-do-nothing)) |

## Things that surprise people

- **Confidence never falls while a sense reports you.** It rises or holds; fading starts only when every sense is silent.
- **`Vision Sample Count` is ignored** for a target with an **APS Target Component**: the component brings its own five points.
- **Never-search zones are advice.** Your search asks **Is Location in Never Search Zone**; nothing is blocked for you.
- **Pain Sense reads your health by itself** and dulls **every** sense with it: at half health, half strength.
- **Noises nobody made never fire On AI Hear.** **Emit Sound at Location** makes a belief about a place.
- **An idle AI never reaches tier 0**: it updates at half rate at best until it is Suspicious.
- **An explosion shakes the ground** for vibration only if its sound type's `Sound Name` is exactly Explosion.
- **100 damage from one attacker is full confidence.** Scale to your damage numbers.
- **Set Target Confidence only raises.** To lower or clear belief, use **Add Target Evidence**.
- **Allies count.** Guards perceive each other: they take target slots and count toward fear ("more than 2 targets").
