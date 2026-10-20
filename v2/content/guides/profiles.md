---
title: Profiles
description: A Perception Profile holds everything about how a kind of AI perceives. Make variants by inheritance instead of copies, change one value for one AI, swap profiles while playing without losing what it knows, and use the workbench buttons - budget, compare, composition, validate.
local: DA_Profile_Guard, DA_Profile_Guard_Alert, DA_Profile_Guard_Elite, DA_Profile_Guard_Copy
---
<div class="kicker">Guide</div>

# Profiles

A **Perception Profile** is a data asset holding everything about how one kind of AI perceives: its senses, ranges, thresholds, memory, emotions. AI with the same profile share it; you tune them all in one place.

::: fast
- Content Browser › Miscellaneous › Data Asset › **Perception Profile**; assign it to the **APS Core**'s `Profile`.
- Variants (alert, elite, easy) are **children**: set `Parent Profile` and change only what differs.
- One AI slightly different: **Set Profile Number** or the core's `Profile Overrides`, with no new asset.
- Press **Validate Profile** after editing: it catches settings that contradict each other.
:::

Every setting, with its default and its override name, is on the [profile reference](../reference/profile.md). This page is how profiles work.

## Senses: which, how much, how often

**Senses › Setup** decides what the AI can perceive at all:

| Setting | What it does |
|---|---|
| `Sense Classes` | The senses it runs, at most 8 (Vision Sense and Hearing Sense by default). Your own Blueprint senses go here too. |
| `Sense Weights` | How much each sense counts, by class; a sense not listed counts 1 |
| `Sense Intervals` | How often each sense updates, in seconds; not listed uses the sense's own (Vision 0.15, Smell 0.25, Echolocation 0.3, the others 0.1) |

The rest of the profile is grouped the way the Details panel groups it: **Ranges**, **Detection** (vision's cones, eyes, light, occlusion, visibility; hearing; the other senses), **Loss**, **Fusion**, **Memory**, **Awareness**, **Attention**, **Spatial**, **Performance**, **Brain** (emotions, threat, squad, player model), **Senses** (pain, touch), **Fairness**, **Replication**, **Composition**, **Policies** and **Workbench**. The feature pages explain each group with what it does to play.

## Start from an archetype

**Archetype** › choose one › **Apply Archetype** stamps a preset (Guard, Civilian, Stalker, Military Patrol, Wildlife) onto the asset. **Apply Archetype To** (Target, In Archetype) does the same from Blueprint, on a profile you created at runtime. What each sets: [Ready-made AI](ready-made-ai.md#the-built-in-archetypes).

## Variants: inherit, don't copy

Set `Parent Profile` (Composition) and the asset takes everything from its parent. Fields you leave alone follow the parent for good; fields you change are yours.

There is no list to keep: a field counts as **changed when it differs from the class default**, which is exactly where the Details panel shows its reset arrow. See the arrow, and that field is overridden.

```
DA_Profile_Guard              the base: every tuned value
├── DA_Profile_Guard_Alert    Parent: Guard. Changes Vision Max Range and the thresholds
└── DA_Profile_Guard_Elite    Parent: Guard. Changes Confidence Rise Rate
```

::: warn Make a new profile, don't duplicate the parent
A duplicate (DA_Profile_Guard_Copy) copies every tuned value, and each one then reads as a deliberate change: the child inherits nothing while looking wired up. Create a new profile, set its parent, change only what differs. **Validate Profile** warns when a child changes most of its fields.
:::

**To keep a value that equals the class default** (which would otherwise read as "not set, follow the parent"), put it in the profile's `Overrides` list: entries of `Property`, `Number` and `Flag` applied after inheritance. The demo uses this to switch a guard's side vision **off** (off is the default, so only an override can say it).

**When it resolves:** once, when an AI starts or swaps profiles, into a private copy for that AI. Editing a parent affects AI that start afterwards, not those already running. A profile with no parent and no overrides is shared as it is: nothing is copied. **Show Composition** logs, field by field, what is inherited and what isn't. Chains can be up to 8 parents deep; a loop is reported and stopped.

## One AI, slightly different

Skip new assets. On the **APS Core**:

- `Profile Overrides` in its Details: the same `Property`, `Number`, `Flag` entries, for this AI only.
- While playing:

| Node (APS Core) | What it does |
|---|---|
| **Set Profile Number** (Property, Value) | Change one number for this AI |
| **Set Profile Flag** (Property, Value) | Change one tickbox |
| **Get Profile Number** (Property, Fallback) | Read one back |
| **Clear Profile Overrides** | Back to the asset as authored |
| **Get Source Profile** | The asset as assigned, before composition |

```
Set Profile Number (VisionMaxRange, 7777)
```

`Property` is the setting's **override name**, shown on every setting in the [profile reference](../reference/profile.md). It is not always the label without spaces: a tickbox keeps its b (bEnablePeripheralCone) and some keep an underscore (MinVisiblePoints_Crouched). A name that doesn't exist is refused and logged, never silently ignored.

- The change lands on a **private copy**: the asset and every other AI using it are untouched.
- It **survives a profile swap**: it belongs to the AI, not the asset.
- Nothing the AI believes is reset; the value is read on its next update.

For every AI at once while playing, without touching any asset: `aps.Tune VisionMaxRange 5000` in the console (a tickbox takes 1 or 0). It's gone next launch, which is what makes it safe to try anything mid-session ([Visualizer & debugging](../features/visualizer.md#pause-print-and-tune-live)).

## Swapping profiles while playing

**Set Profile** (New Profile) on the APS Core: an alarm makes every guard sharper, a far-away AI drops to a cheaper profile.

- **It keeps everything the AI knows** (beliefs, emotions, attention, its combat role) when the new profile runs **the same senses in the same order** with the same `Max Tracked Targets`. Children of one base profile are like that by construction.
- Otherwise the senses are rebuilt and that state starts fresh.
- Called from inside a perception event (**On AI Detect** → **Set Profile** is common), the swap waits until that update ends.

For cost alone, a **Quality Profile** changes how much work an AI does with no risk to what it knows: [Performance](performance.md).

## The workbench

On the profile's Details:

| Button or node | What it does |
|---|---|
| **Validate Profile** | Lists every problem in the Output Log (below) |
| **Show Budget** · **Estimate Budget** (Agent Count, Targets Per Agent) | Estimates traces and sense updates per second for a level of AI, and names the setting behind each number. An estimate from the settings, not a measurement: what the asset **asks for**. |
| `Compare To` + **Compare With** · **Diff Against** (Other) | Every field where two profiles differ, as Field: theirs → mine |
| **Show Composition** · **Get Overridden Property Names** | What a child inherits and what it sets itself |

**Validate Profile** catches the mistakes that cost an afternoon and leave nothing in the log:

- Inheritance: a profile that is its own parent, a parent loop, a child that changes nothing, a child that looks like a duplicate, an override naming a setting that doesn't exist.
- Senses: none at all, more than 8, an empty entry, the same sense twice, a weight or interval for a sense the profile doesn't run.
- Order: Detect not above Suspect, Track not above Detect, Full Aware not above Track, Memory Expire at or above Suspect, Telegraph outside the Suspect-to-Detect band.
- Vision: a side cone inside the focal cone, keyhole angles inverted, Use Eye Socket with no socket name, an exposure rule nothing can meet, Vision Sample Count ignored because samples are authored.
- Brain: both auto-share settings on (the second does nothing), every threat weight zero, every sort weight zero.

Run it after editing a profile, and whenever an AI does something its settings don't seem to explain.
