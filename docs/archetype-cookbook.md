# Archetype Cookbook

Copy-paste profile settings for common AI types. Every one of these is a **starting point** — tune from here, do not treat them as gospel.

Settings not listed keep their defaults.

> **One rule that shapes several of these builds:** targets are only handed to the senses if they fall inside the largest gather range on the profile, and Vibration and Echolocation declare fixed gather ranges of 800 and 2000 cm regardless of their profile settings. That is why the Zombie and Blind Creature builds below both carry a long `Hearing Max Range` — it is what pulls distant targets into evaluation range for their short-range senses.

---

## Stealth Guard

*Sharp but fair. Reacts believably, gives the player readable warnings, cannot see through walls.*

**Senses:** Vision, Hearing
**Weights:** Vision 1.0, Hearing 1.0

| Section | Setting | Value |
|---|---|---|
| Ranges | Vision Max Range | 2200 |
| Ranges | Hearing Max Range | 1800 |
| Detection | Vision Half Angle Deg | 55 |
| Detection\|Cones | b Enable Peripheral Cone | ✅ |
| Detection\|Cones | Peripheral Half Angle Deg | 100 |
| Detection\|Cones | Peripheral Confidence Scale | 0.4 |
| Detection\|Keyhole | b Keyhole Vision | ✅ |
| Detection\|Keyhole | Keyhole Near Angle | 85 |
| Detection\|Keyhole | Keyhole Far Angle | 18 |
| Detection\|Eyes | Eye Direction Mode | Socket Rotation |
| Detection\|Eyes | b Use Eye Socket | ✅ (`head`) |
| Detection\|Eyes | Eye Turn Rate Deg Per Sec | 200 |
| Detection\|Light | b Use Per Target Light | ✅ |
| Detection\|Visibility | Min Visible Points Crouched | 2 |
| Awareness | Suspect / Detect / Track | 0.18 / 0.40 / 0.65 |
| Loss | Vision Loss Grace | 0.8 |
| Memory | Min Time In Lost | 8.0 |
| Attention | Attention Stickiness Time | 2.0 |
| Fairness | First Spot Reaction Time | 0.4 |
| Fairness | Telegraph Threshold | 0.22 |
| Fairness | b Offscreen Hearing Penalty | ✅ |
| Squad | b Auto Share On Detect | ❌ (share manually after a call-out) |

**Why the vision grace is 0.8 s:** the guard keeps staring at where you were instead of dropping you the instant a pillar clips the trace. It reads as *"I know you're behind there"* rather than *"you vanished"*.

---

## Guard Dog

*Hunts by nose and ears. Weak eyes. Nearly impossible to sneak past downwind.*

**Senses:** Smell, Hearing, Vision
**Weights:** Smell 1.5, Hearing 1.3, Vision 0.5

| Section | Setting | Value |
|---|---|---|
| Ranges | Smell Max Range | 1400 |
| Ranges | Hearing Max Range | 2200 |
| Ranges | Vision Max Range | 1000 |
| Detection | Vision Half Angle Deg | 70 |
| Detection | Smell Accumulation Rate | 0.25 |
| Detection | Smell Decay Rate | 0.03 |
| Detection | Sound Filter | `DA_Filter_Dog` (Whisper, ×2.0) |
| Awareness | Suspect / Detect / Track | 0.12 / 0.30 / 0.55 |
| Loss | Smell Loss Grace | 30.0 |
| Attention | Attention Stickiness Time | 3.0 |
| Brain\|Emotions | Aggression Rise Rate | 1.2 |
| Brain\|Squad | b Auto Share On Detect | ✅ |

Subclass **Smell Sense** in Blueprint with `Downwind Bonus` 2.5 and `Scent Threshold` 0.25, and put your Blueprint in `Sense Classes`.

Drive **Set Wind State** from your weather system, and the level becomes a genuine wind-direction puzzle.

---

## Zombie / Infected

*Feels you through the floor. Hears everything. Barely sees. Once it locks on, it does not let go.*

**Senses:** Hearing, Vibration, Vision, Touch
**Weights:** Hearing 1.4, Vibration 1.3, Vision 0.35, Touch 1.0

| Section | Setting | Value |
|---|---|---|
| Ranges | Hearing Max Range | 2500 |
| Ranges | Vibration Detect Range | 1200 |
| Ranges | Vision Max Range | 700 |
| Detection | Vision Half Angle Deg | 90 |
| Detection | Vibration Min Speed | 150 |
| Detection | Darkness Min Detection | 0.5 |
| Awareness | Suspect / Detect / Track | 0.10 / 0.25 / 0.45 |
| Fusion | Confidence Rise Rate | 7.0 |
| Attention | Attention Stickiness Time | 5.0 |
| Attention | Attention Switch Threshold | 0.4 |
| Memory | Default Decay Exponent | 0.15 |
| Brain\|Emotions | Max Fear | 0.0 |
| Brain\|Emotions | Aggression Rise Rate | 1.5 |
| Brain\|Squad | b Auto Share On Detect | ✅ |
| Brain\|Squad | Squad Share Range | 6000 |

`Vibration Min Speed` at 150 is the design lever: **walk and it feels you, crouch-walk and it does not.** That single number is the whole stealth mechanic.

Fear capped at 0 means a zombie never flees.

---

## Blind Creature

*Echolocation and vibration. No eyes at all. Freeze and it loses you completely.*

**Senses:** Echolocation, Hearing, Vibration
**Weights:** Echolocation 1.2, Hearing 1.1, Vibration 1.0

| Section | Setting | Value |
|---|---|---|
| Ranges | Echo Range | 2200 |
| Ranges | Hearing Max Range | 3000 |
| Ranges | Vibration Detect Range | 1500 |
| Detection | b Echo Directional | ✅ |
| Detection | Vibration Min Speed | 80 |
| Senses\|Setup | Sense Intervals → Echolocation | 0.4 |
| Awareness | Suspect / Detect / Track | 0.15 / 0.35 / 0.60 |
| Loss | Echolocation Loss Grace | 1.0 |
| Attention | Attention Stickiness Time | 4.0 |

No Vision sense at all. Light does nothing — the room can be pitch dark and it makes no difference.

The player mechanic: **stand perfectly still.** Vibration drops instantly, echolocation still pings but confidence never accumulates enough. Slowing the echo interval to 0.4 s gives the player readable windows between pulses.

---

## Sniper / Overwatch

*Sees a long way in a narrow cone. Almost deaf. Once it has you, it keeps you.*

**Senses:** Vision, Hearing, Damage
**Weights:** Vision 1.4, Hearing 0.6

| Section | Setting | Value |
|---|---|---|
| Ranges | Vision Max Range | 9000 |
| Ranges | Hearing Max Range | 900 |
| Detection | Vision Half Angle Deg | 25 |
| Detection\|Cones | b Use Separate Vertical FOV | ✅ |
| Detection\|Cones | Vision Vertical Half Angle Deg | 20 |
| Detection | Sound Filter | `DA_Filter_HeavyArmor` (Loud+) |
| Awareness | Suspect / Detect / Track | 0.20 / 0.45 / 0.70 |
| Awareness | Min Track Duration | 1.2 |
| Spatial | b Enable Prediction | ✅ |
| Spatial | Prediction Horizon | 1.5 |
| Performance | Sort Weight Confidence | 0.7 |
| Performance | Sort Weight Proximity | 0.05 |
| Attention | Attention Stickiness Time | 4.0 |
| Loss | Vision Loss Grace | 2.0 |
| Fairness | First Spot Reaction Time | 0.8 |

Prediction is on so the sniper leads a moving target. Proximity is weighted almost to nothing so it targets by confidence, not distance.

The 0.8 s reaction time is essential — an instant-detect sniper at 90 m with no warning is one of the least fair things you can build.

---

## Security Camera / Turret

*Perfectly consistent. No mercy, no emotion, no fairness allowances.*

**Senses:** Vision
**Weights:** Vision 1.0

| Section | Setting | Value |
|---|---|---|
| Ranges | Vision Max Range | 2500 |
| Detection | Vision Half Angle Deg | 40 |
| Detection | Darkness Min Detection | 1.0 (infrared — dark does not matter) |
| Detection | Vision Sample Count | 3 |
| Detection\|Eyes | Eye Direction Mode | Actor Rotation |
| Awareness | Suspect / Detect / Track | 0.20 / 0.40 / 0.60 |
| Fusion | Confidence Rise Rate | 3.0 |
| Loss | Vision Loss Grace | 0.1 |
| Memory | Default Decay Exponent | 1.0 (forgets fast) |
| Performance | Max Tracked Targets | 4 |
| Performance | Base Update Interval | 0.15 |
| Attention | Attention Stickiness Time | 0.5 |
| Brain\|Emotions | all Max values | 0.0 |
| Fairness | First Spot Reaction Time | 0.0 |
| Brain\|Squad | b Auto Share On Detect | ✅ |

The slow `Confidence Rise Rate` of 3.0 gives the player a visible detection window — a camera should have a fill-up bar, not an instant trigger.

All emotion caps at 0: no fear, no panic, no curiosity. It just reports.

---

## Soldier / Tactical Enemy

*Coordinated, disciplined, reacts to damage. The workhorse combat archetype.*

**Senses:** Vision, Hearing, Damage, Pain
**Weights:** Vision 1.0, Hearing 1.0

| Section | Setting | Value |
|---|---|---|
| Ranges | Vision Max Range | 3500 |
| Ranges | Hearing Max Range | 3000 |
| Detection | Vision Half Angle Deg | 60 |
| Detection\|Cones | b Enable Peripheral Cone | ✅ |
| Detection\|Cones | b Enable Rear Motion Cone | ✅ |
| Detection\|Occlusion | b Pawns Block Sight | ✅ |
| Awareness | Suspect / Detect / Track | 0.15 / 0.35 / 0.60 |
| Brain\|Threat | Threat Weight Damage Received | 0.40 |
| Brain\|Threat | Threat Damage Decay Rate | 0.02 |
| Brain\|Squad | b Auto Share On Detect | ❌ |
| Brain\|Squad | b Auto Share On Track | ✅ |
| Brain\|Squad | Squad Share Range | 4000 |
| Brain\|Squad | Eligible Roles | Approacher, Flanker, Suppressor |
| Attention | Attention Stickiness Time | 1.5 |
| Fairness | First Spot Reaction Time | 0.25 |

Sharing on `Tracked` rather than `Detected` means the squad only converges once someone has *confirmed* the target — a glimpse does not mobilise everyone.

`b Pawns Block Sight` means squadmates block each other's lines, which produces natural spread and flanking.

Pain sense with `DA_Pain_Bleeding` and `DA_Pain_Flashbang` makes flashbangs and suppression genuinely tactical.

---

## Horror Antagonist

*The stalker. Slow, patient, remembers everything, and learns you across the whole game.*

**Senses:** Hearing, Vision, Smell, Vibration
**Weights:** Hearing 1.3, Vision 0.8, Smell 1.0, Vibration 0.9

| Section | Setting | Value |
|---|---|---|
| Ranges | Hearing Max Range | 4000 |
| Ranges | Vision Max Range | 1800 |
| Ranges | Smell Max Range | 900 |
| Detection\|Keyhole | b Keyhole Vision | ✅ |
| Awareness | Suspect / Detect / Track | 0.12 / 0.32 / 0.58 |
| Memory | Default Decay Exponent | 0.08 (forgets very slowly) |
| Memory | Min Time In Lost | 25.0 |
| Memory | Memory Refresh Bonus | 0.25 |
| Spatial | b Enable Prediction | ✅ |
| Spatial | Uncertainty Growth Rate | 35 |
| Spatial | Max Uncertainty Radius | 1800 |
| Attention | Attention Stickiness Time | 8.0 |
| Brain\|PlayerModel | b Enable Cross Session Memory | ✅ |
| Brain\|PlayerModel | Min Engagements Required | 2 |
| Fairness | Telegraph Threshold | 0.20 |
| Fairness | b Respect Never Search Zones | ✅ |

`Min Time In Lost` at 25 s means once it starts hunting, it hunts for a *long* time. That is the whole feeling.

`Memory Refresh Bonus` at 0.25 means the second contact locks on far faster than the first — it is getting to know you.

**Register never-search zones around every save room and locker.** Without a guaranteed-safe space, this archetype stops being tense and becomes exhausting.

---

## Difficulty scaling

The cleanest approach: **make one profile per difficulty** and swap with **Set Profile** on Begin Play. Vary only these:

| Setting | Easy | Normal | Hard |
|---|---|---|---|
| Suspect Threshold | 0.25 | 0.15 | 0.10 |
| Detect Threshold | 0.50 | 0.35 | 0.25 |
| Track Threshold | 0.75 | 0.60 | 0.45 |
| Confidence Rise Rate | 3.0 | 5.0 | 7.0 |
| First Spot Reaction Time | 0.8 | 0.4 | 0.1 |
| Vision Max Range | ×0.8 | ×1.0 | ×1.2 |
| Min Time In Lost | 3.0 | 8.0 | 15.0 |
| Memory Refresh Bonus | 0.05 | 0.10 | 0.20 |

**Leave the cone angles and occlusion identical across difficulties.** The player's spatial understanding of what a guard can see should not change between playthroughs — only how quickly it acts on what it sees.

---

