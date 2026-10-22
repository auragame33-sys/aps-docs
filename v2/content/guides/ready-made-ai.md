---
title: Ready-made AI
description: Five one-button archetypes built into every profile, then tested starting points for a stealth guard, a guard dog, a zombie, a blind creature, a sniper, a camera, a soldier and a horror stalker, and how to scale difficulty.
local: DA_Profile_Guard, DA_Profile_Guard_Easy
---
<div class="kicker">Guide</div>

# Ready-made AI

Start from a preset, not from a blank profile: five archetypes are one button away, and the recipes below cover the AI most games need.

::: fast
- Open a **Perception Profile**, pick an `Archetype` and press **Apply Archetype**: five presets (Guard, Civilian, Stalker, Military Patrol, Wildlife).
- Or copy a recipe below: only the settings that differ from the defaults are listed.
- Make variants (easy, alert, elite) as **child profiles** of one base, not copies ([Profiles](profiles.md)).
:::

## The built-in archetypes

In a Perception Profile's Details, **Archetype**: choose one in `Archetype`, then press **Apply Archetype**. It overwrites the settings below and leaves everything else alone; nothing reads `Archetype` while playing, so it is a starting point, not a mode.

| Setting | Guard | Civilian | Stalker | Military Patrol | Wildlife |
|---|---|---|---|---|---|
| `Vision Max Range` | 2500 | 1800 | 3500 | 4000 | 1500 |
| `Vision Half Angle Deg` | 55 | 70 | 35 | 50 | 80 |
| `Hearing Max Range` | 2000 | 2500 | 3000 | 2500 | 3500 |
| `Smell Max Range` | | | 2500 | | 4000 |
| `Enable Peripheral Cone` | On, 85° | On, 95° | Off | On, 80° | On, 110° |
| `Suspect Threshold` | 0.25 | 0.35 | 0.2 | 0.3 | 0.15 |
| `Detect Threshold` | 0.5 | 0.65 | 0.45 | 0.55 | 0.35 |
| `Track Threshold` | 0.75 | 0.85 | 0.7 | 0.8 | 0.6 |
| `Full Aware Threshold` | 0.9 | 0.95 | 0.88 | 0.92 | 0.8 |
| `Telegraph Threshold` | 0.375 | 0.5 | 0.32 | 0.42 | 0.25 |
| `Confidence Rise Rate` | 3 | 1.5 | 1.2 | 2.5 | 4 |
| `Memory Retention Seconds` | 300 | 45 | 900 | 420 | 90 |
| `Attention Stickiness Time` | 3 | 1 | 8 | 4 | 0.75 |
| `Max Tracked Targets` | 6 | 2 | 1 | 8 | 3 |
| `Max Fear` | 0.4 | 1 | 0 | 0.25 | 1 |
| Also | `Enable Prediction` | `Fear Rise Rate` 2.5, `Enable Statistical Tier` | `Enable Prediction` | `Squad Share Range` 5000, `Auto Share on Detect`, `Enable Prediction` | `Smell Accumulation Rate` 2, `Fear Rise Rate` 4 |

- **Guard:** alert and forward-facing; commits to a contact quickly and keeps it.
- **Civilian:** wide senses, high thresholds, short memory; reacts without investigating.
- **Stalker:** a narrow, long look and a memory that doesn't let go.
- **Military Patrol:** the longest sight; shares contacts with the squad.
- **Wildlife:** smell and hearing over sight; reacts long before it is sure.

::: warn Archetypes don't add senses
Applying one never changes `Sense Classes`. The Stalker and Wildlife set a smell range: add **Smell Sense** to `Sense Classes` yourself, or that range does nothing.
:::

![One Blueprint, different AI](media/cards/why_archetypes.webp "An example Blueprint: Set Profile on the guard's APS Core swaps in a whole new set of senses and settings while playing.")

## Recipes

Starting points to tune from. Settings not listed keep their defaults; values are what to type in the profile.

### Stealth guard

*Sharp but fair: believable reactions, a warning before it commits, never sees through walls.* Senses: **Vision**, **Hearing**.

| Setting | Value |
|---|---|
| `Vision Max Range`, `Hearing Max Range` | 2200, 1800 |
| `Vision Half Angle Deg` | 55 |
| `Enable Peripheral Cone`, `Peripheral Half Angle Deg`, `Peripheral Confidence Scale` | On, 100, 0.4 |
| `Keyhole Vision`, `Keyhole Near Angle`, `Keyhole Far Angle` | On, 85, 18 |
| `Eye Direction Mode`, `Use Eye Socket`, `Eye Turn Rate Deg Per Sec` | Socket Rotation (head bone), On (head), 200 |
| `Use Per Target Light` | On |
| `Min Visible Points Crouched` | 2 |
| `Suspect Threshold`, `Detect Threshold`, `Track Threshold` | 0.18, 0.40, 0.65 |
| `Vision Loss` › Grace Time | 0.8 |
| `Min Time in Lost` | 8 |
| `First Spot Reaction Time`, `Telegraph Threshold` | 0.4, 0.22 |
| `Offscreen Hearing Penalty` | On |
| `Auto Share on Detect` | Off: share after a call-out with **Share Target with Squad** |

The 0.8 s vision grace keeps it staring where you were instead of dropping you the moment a pillar clips the trace: *"I know you're behind there"*, not *"you vanished"*.

### Guard dog

*Hunts by nose and ears, weak eyes; very hard to pass with the wind at your back.* Senses: **Smell**, **Hearing**, **Vision**, weighted 1.5, 1.3 and 0.5 in `Sense Weights`.

| Setting | Value |
|---|---|
| `Smell Max Range`, `Hearing Max Range`, `Vision Max Range` | 1400, 2200, 1000 |
| `Vision Half Angle Deg` | 70 |
| `Smell Accumulation Rate`, `Smell Decay Rate` | 0.25, 0.03 |
| `Suspect Threshold`, `Detect Threshold`, `Track Threshold` | 0.12, 0.30, 0.55 |
| `Smell Loss` › Grace Time | 30 |
| `Attention Stickiness Time` | 3 |
| `Aggression Rise Rate` | 1.2 |

Make a Blueprint child of **Smell Sense** with `Downwind Bonus` 2.5 and `Scent Threshold` 0.25 and put it in `Sense Classes`; give it a `Sound Filter` that boosts quiet sounds ([Hearing](../features/hearing.md)). Call **Set Wind State** and the level becomes a wind puzzle ([Smell](../features/senses.md#smell)).

### Zombie

*Feels you through the floor, hears everything, barely sees, never lets go.* Senses: **Hearing**, **Vibration**, **Vision**, **Touch**.

| Setting | Value |
|---|---|
| `Hearing Max Range`, `Vibration Detect Range`, `Vision Max Range` | 2500, 1200, 700 |
| `Vision Half Angle Deg` | 90 |
| `Vibration Min Speed` | 320 |
| `Darkness Min Detection` | 0.5 |
| `Suspect Threshold`, `Detect Threshold`, `Track Threshold` | 0.10, 0.25, 0.45 |
| `Confidence Rise Rate` | 7 |
| `Attention Stickiness Time`, `Attention Switch Threshold` | 5, 0.4 |
| `Default Decay Exponent` | 0.15 |
| `Max Fear` | 0: it never flees |
| `Aggression Rise Rate` | 1.5 |
| `Squad Share Range` | 6000 (with the default `Auto Share on Detect`: one sees you, the pack comes) |

`Vibration Min Speed` is the whole stealth mechanic: set it just above your crouch speed (Unreal's default crouch is 300 cm/s), and walking is felt while crouch-walking isn't.

### Blind creature

*No eyes: sonar and the floor. Light means nothing to it.* Senses: **Echolocation**, **Hearing**, **Vibration**.

| Setting | Value |
|---|---|
| `Echo Range`, `Hearing Max Range`, `Vibration Detect Range` | 2200, 3000, 1500 |
| `Echo Directional` | On |
| `Vibration Min Speed` | 80 |
| `Sense Intervals` | Echolocation Sense → 0.4 |
| `Echolocation Loss` › Grace Time | 1 |
| `Attention Stickiness Time` | 4 |

**How the player beats it:** standing still beats vibration, but **not** echolocation, which doesn't care whether you move. Stay **behind** it (Echo Directional ignores what is more than about 101° off its facing) or **far**: echo confidence is (1 − distance ÷ range)², so beyond about two thirds of `Echo Range` it stays under Suspected. The 0.4 s ping interval gives readable windows between pulses.

### Sniper

*A long, narrow look; nearly deaf; once it has you it keeps you.* Senses: **Vision**, **Hearing**, **Damage**.

| Setting | Value |
|---|---|
| `Vision Max Range`, `Hearing Max Range` | 9000, 900 |
| `Vision Half Angle Deg` | 25 |
| `Use Separate Vertical FOV`, `Vision Vertical Half Angle Deg` | On, 20 |
| `Suspect Threshold`, `Detect Threshold`, `Track Threshold` | 0.20, 0.45, 0.70 |
| `Min Track Duration` | 1.2 |
| `Enable Prediction`, `Prediction Horizon` | On, 1.5 |
| `Sort Weight Confidence`, `Sort Weight Proximity` | 0.7, 0.05: it picks by certainty, not by distance |
| `Attention Stickiness Time` | 4 |
| `Vision Loss` › Grace Time | 2 |
| `First Spot Reaction Time` | 0.8 |

Prediction lets your aim lead a moving target (**Get Predicted Position**). The 0.8 s reaction time matters: an instant sniper at 90 m with no warning is one of the least fair things you can build.

### Security camera or turret

*Consistent, emotionless, no allowances.* Senses: **Vision** only.

| Setting | Value |
|---|---|
| `Vision Max Range`, `Vision Half Angle Deg` | 2500, 40 |
| `Darkness Min Detection` | 1: infrared, darkness doesn't matter |
| `Eye Direction Mode` | Actor Rotation |
| `Suspect Threshold`, `Detect Threshold`, `Track Threshold` | 0.20, 0.40, 0.60 |
| `Confidence Rise Rate` | 3: a visible fill-up, not an instant trigger |
| `Vision Loss` › Grace Time | 0.1 |
| `Default Decay Exponent` | 1: forgets fast |
| `Max Tracked Targets`, `Base Update Interval` | 4, 0.15 |
| `Attention Stickiness Time` | 0.5 |
| `Max Fear`, `Max Aggression`, `Max Curiosity`, `Max Alertness`, `Max Panic` | 0: it just reports |

### Soldier

*Coordinated, disciplined, reacts to damage: the workhorse.* Senses: **Vision**, **Hearing**, **Damage**, **Pain**.

| Setting | Value |
|---|---|
| `Vision Max Range`, `Hearing Max Range` | 3500, 3000 |
| `Enable Peripheral Cone`, `Enable Rear Motion Cone` | On, On |
| `Pawns Block Sight` | On: squadmates block each other's view, which spreads them out |
| `Threat Weight Damage Received`, `Threat Damage Decay Rate` | 0.40, 0.02 |
| `Auto Share on Detect`, `Auto Share on Track` | Off, On: the squad converges only on a confirmed contact |
| `Squad Share Range` | 4000 |
| `Eligible Roles` | Approacher, Flanker, Suppressor |
| `Attention Stickiness Time` | 1.5 |
| `First Spot Reaction Time` | 0.25 |

With Pain Sense, a flashbang and a bleed ([Emotions & pain](../features/emotions.md#a-useful-set)) make suppression tactical.

### Horror stalker

*Slow, patient, remembers everything, learns you.* Senses: **Hearing**, **Vision**, **Smell**, **Vibration**.

| Setting | Value |
|---|---|
| `Hearing Max Range`, `Vision Max Range`, `Smell Max Range` | 4000, 1800, 900 |
| `Keyhole Vision` | On |
| `Suspect Threshold`, `Detect Threshold`, `Track Threshold` | 0.12, 0.32, 0.58 |
| `Default Decay Exponent` | 0.08: forgets very slowly |
| `Min Time in Lost` | 25: once it hunts, it hunts for a long time |
| `Memory Refresh Bonus` | 0.25: finding you again locks on fast |
| `Enable Prediction` | On |
| `Uncertainty Growth Rate`, `Max Uncertainty Radius` | 35, 1800 |
| `Attention Stickiness Time` | 8 |
| `Min Engagements Required` | 2 |
| `Telegraph Threshold` | 0.20 |

**Register a never-search zone around every save room and locker** ([World & fairness](../features/world.md#safe-rooms)) and honour it in its search: without a certainly safe place this AI stops being tense and becomes exhausting.

## Difficulty

Make one child profile per difficulty (DA_Profile_Guard_Easy as a child of DA_Profile_Guard) and assign it, or swap with **Set Profile** at Begin Play. Change only how fast it acts on what it sees:

| Setting | Default | Easy | Normal | Hard |
|---|---|---|---|---|
| `Suspect Threshold` | 0.15 | 0.25 | 0.15 | 0.10 |
| `Detect Threshold` | 0.35 | 0.50 | 0.35 | 0.25 |
| `Track Threshold` | 0.60 | 0.75 | 0.60 | 0.45 |
| `Confidence Rise Rate` | 5 | 3 | 5 | 7 |
| `First Spot Reaction Time` | 0 | 0.8 | 0.4 | 0.1 |
| `Min Time in Lost` | 0 | 3 | 8 | 15 |
| `Memory Refresh Bonus` | 0.1 | 0.05 | 0.10 | 0.20 |
| `Vision Max Range` | 2000 | × 0.8 | × 1 | × 1.2 |

**Keep cone angles and occlusion the same on every difficulty.** What a guard can see should be something the player learns once; only how quickly it acts on it should change.
