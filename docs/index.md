# APS — Advanced Perception System

<div class="aps-hero" markdown>

<p class="aps-hero__tagline">An 8-sense belief-based AI perception engine for Unreal Engine 5.</p>
<p class="aps-hero__sub">Blueprint-first. Zero C++ required. Belief, not booleans.</p>

[Get started :material-arrow-right:](getting-started.md){ .md-button .md-button--primary }
[Build a complete guard](tutorial-complete-guard.md){ .md-button }

</div>

> **▶ Video walkthrough** — *What APS does (2 min).* Coming soon.
> When it is live, delete this block and uncomment the embed below.

<!-- VIDEO EMBED — replace VIDEO_ID with your YouTube id, then delete the comment markers
<div class="video">
  <iframe src="https://www.youtube.com/embed/VIDEO_ID" title="What APS does" allowfullscreen></iframe>
</div>
-->

APS is a drop-in replacement for Unreal's built-in `AIPerception` component. Instead of asking *"can this AI see the player: yes or no?"*, APS asks *"how confident is this AI that the player is at position X right now, and what is it going to do about it?"*

Every sense the AI owns produces a confidence value each tick. Those values are fused into one number per target. That number drives a lifecycle — **Undetected → Suspected → Detected → Tracked → Lost → Remembered → Expired** — and every transition fires a Blueprint event you can hook.

When the AI loses you, it does not simply forget. It records *why* it lost you (you broke line of sight / walked out of earshot / your scent faded), where you were, which direction you were heading, and what cover object you ducked behind. All of that is readable from Blueprint, and is exactly what a Behavior Tree needs to search intelligently instead of running a generic sweep.

---

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Install & Your First AI**

    ---

    Install the plugin and get a working detection — cone drawn, confidence climbing, events firing.

    [:octicons-arrow-right-24: 15 minutes](getting-started.md)

-   :material-school:{ .lg .middle } **Tutorial: A Complete Guard**

    ---

    Patrol → hear → investigate → chase → search the right cover → give up. The full loop, with a Behavior Tree.

    [:octicons-arrow-right-24: 45 minutes](tutorial-complete-guard.md)

-   :material-lightning-bolt:{ .lg .middle } **Cheat Sheet**

    ---

    Every node, event, threshold and fast fix worth knowing, on one page. Bookmark this one.

    [:octicons-arrow-right-24: Open](cheat-sheet.md)

-   :material-book-open-variant:{ .lg .middle } **How-To Guides**

    ---

    25 task recipes — stop AI seeing through doors, track by scent, add a detection meter, blind a guard.

    [:octicons-arrow-right-24: Browse recipes](how-to-guides.md)

</div>

---

## The 60-second version

1. Create a **Perception Profile** data asset. It ships with Vision and Hearing already enabled.
2. Add the **APS Core** component to your AI character. Assign the profile.
3. Add the **APS Perception Listener** component to the same character.
4. In the character's Event Graph, right-click → search **`OnAIDetect`** → override it.
5. Press Play. The AI sees you, builds confidence, and fires the event.

That is a working AI. Everything else in these docs is tuning and depth.

---

## Who it is for

- **Stealth games** — readable detection, safe rooms, reaction-time grace, telegraphed spotting.
- **Horror games** — creatures that hunt by sound, smell, ground vibration or echolocation with no line of sight.
- **Shooters** — peripheral vision, damage-aware threat scoring, squad intel sharing, combat roles.
- **Survival / animal AI** — wind-driven scent tracking, hearing-first predators, pack behaviour.
- **Anyone** who has hit the wall where Epic's perception "sees through a doorway" or "spots you the instant you enter the cone".

---

## What ships in the box

**8 built-in senses** — Vision, Hearing, Smell, Touch, Vibration, Damage, Pain, Echolocation. Up to 8 senses run per AI simultaneously, and you can add your own in Blueprint.

**Belief, not booleans** — continuous 0–1 confidence per target with a full lifecycle, smoothing, and configurable decay curves.

**Multi-point visibility** — the AI traces against head, chest, pelvis and shoulders (or your own socket list) and gets a *percentage exposed*, not a yes/no. Lean out of cover and only your head is visible — the AI reacts accordingly.

**Three vision cones** — a focal cone, an optional wider/weaker peripheral cone, and an optional rear cone that only registers *moving* targets. Plus keyhole vision (narrow at distance, wide up close).

**Vision bound to the mesh** — the cone origin and direction can come from a head socket, so head turns and aim offsets actually move the AI's gaze. A turn-rate limit stops the cone snapping to a target before the body has physically turned.

**Real occlusion** — multi-channel line-of-sight tests with per-physical-surface transmission. Glass is transparent, foliage dampens, concrete blocks. Optionally other pawns block sight too.

**Per-target lighting** — a shadow trace at the target's location, so a dark corner is genuinely dark, not just "night time".

**Spatial belief** — last known position, smoothed velocity and acceleration, an uncertainty radius that grows the longer you stay hidden, and predictive extrapolation of where you probably went.

**Episodic memory** — the last 5 engagements with each target: how it ended, where, which way you fled, peak threat.

**Emotional state** — five channels (Fear, Aggression, Curiosity, Alertness, Panic) driven by perception, with a dominant emotion and change events.

**Threat assessment** — a weighted composite score from confidence, damage taken, number of corroborating senses and relationship, mapped to five threat levels.

**Squad coordination** — range-gated intel sharing, positional alerts, and exclusive combat role claiming (Flanker, Suppressor, Investigator…).

**Player behaviour model** — observes how you play using only what the AI could legitimately perceive: movement style, engagement style, favourite hiding spots. It lives for the session, like everything else APS holds.

**Fairness rules** — first-spot reaction delay, telegraph events for "huh?" barks, off-screen hearing penalty, and designer-defined never-search zones for guaranteed safe rooms.

**Replication** — an opt-in compact per-target summary replicated to clients, so detection meters and spectator HUDs work without hand-rolled plumbing.

**7-mode debug suite** — on-screen overlays for Sense, Memory, Brain, Squad, Delegates, Player Model and Environment, plus a one-node print function for every single event.

---

## How it compares to Epic's AIPerception

| | Epic `AIPerception` | APS |
|---|---|---|
| Detection result | Boolean — seen / not seen | Continuous 0–1 confidence per target |
| Line of sight | One trace to capsule centre | Up to 5 weighted sample points → % exposed |
| Cover behaviour | Head fully exposed above a crate still reports "not seen" | Partial exposure produces partial confidence |
| Stance | Ignored | Crouched / prone can require more visible points |
| Vision cone | One symmetric 3D cone | Focal + peripheral + rear-motion + keyhole, separate vertical FOV |
| Cone origin | Actor root + fixed height | Optional mesh socket — follows head animation |
| Cone direction | Control rotation (snaps to MoveTo targets) | Actor / control / socket / blended, with a turn-rate limit |
| Occlusion | One collision channel | Multiple channels + per-surface transmission (glass, foliage, smoke) |
| Light | Not modelled | Global ambient *and* per-target sun-shadow tracing |
| Losing a target | Just stops reporting | Records loss reason, direction, cover actor, and an episode |
| Memory | Age-out only | Decay curves, long-term memory strength, refresh bonus, Remembered state |
| Prediction | None | Velocity/acceleration estimation, uncertainty radius, predicted position |
| Multi-sense | Senses reported independently | Fused into one confidence with a corroboration bonus |
| Threat / emotion | None | Weighted threat scoring, 5 emotion channels |
| Squad | None | Intel sharing, alerts, exclusive combat roles |
| Fairness tooling | None | Reaction delay, telegraph, off-screen penalty, safe rooms |
| Debug | Gameplay Debugger category | 7-mode overlay + per-event print nodes |

> **You can run both.** APS does not disable or interfere with `AIPerception`. If you already have systems bound to Epic's perception, they keep working while you migrate.

---

## Requirements

| | |
|---|---|
| **Engine version** | Unreal Engine 5.2 |
| **Project type** | Blueprint or C++ project — a Blueprint-only project works, the plugin ships its own compiled module |
| **Platforms** | Win64 (Editor + Game). Other platforms compile from source with the engine's normal toolchain. |
| **Module dependencies** | Core, CoreUObject, Engine, AIModule, GameplayTasks, GameplayTags, GameplayDebugger, PhysicsCore, NavigationSystem — all engine modules, no third-party code |
| **Network** | Server-authoritative. Perception does not run on clients. Optional replicated summary for client UI. |

APS has **no external dependencies**, ships **no content assets you are forced to use**, and adds **no required project settings**.

The plugin contains two modules. **APS** is the perception kernel and is all most projects need. **APS Knowledge** is optional and adds the faction-level systems — [descriptions and comms channels](knowledge-and-comms.md), [evidence and search](evidence-and-search.md). The kernel never depends on it, which is what keeps the core genre-blind.

---

## What APS does *not* do

Being clear about scope saves you time:

- **It is not a Behavior Tree.** APS tells your AI *what it believes*. What the AI *does* about it is your BT or state machine. [Behavior Trees](behavior-trees.md) shows the wiring.
- **It does not move your AI.** No pathfinding, no steering, no cover selection. It reports where to search; you drive the movement.
- **It does not play audio.** `Emit Sound` tells the AI a sound happened — you still play your own `Sound Cue` alongside it.
- **It does not manage health.** The Pain sense models *perception impairment*, not hit points. You call it from your own damage/health system, or let it read yours through a [health adapter](adapters.md).
- **It does not decide what an AI should remember.** [Memory](memory-and-recall.md) is a store you write into and read from; what is worth remembering, and what it means, is your game's logic.
- **It does not ship animations, meshes or a sample level** — it is a runtime system, not a template project.

---

# Documentation

## I want to…

| | Go to |
|---|---|
| …see whether this fits my project | You're on that page. Read up ↑ |
| …get something working right now | [Install & Your First AI](getting-started.md) |
| …build a real guard end to end | [Tutorial: A Complete Guard](tutorial-complete-guard.md) |
| …look up a node or a number, fast | [Cheat Sheet](cheat-sheet.md) |
| …do one specific thing | [How-To Guides](how-to-guides.md) — 25 recipes |
| …move off Epic's `AIPerception` | [Migrating from AIPerception](migrating-from-aiperception.md) |
| …understand why it behaves like that | [Core Concepts](core-concepts.md) · [How It Works](how-it-works.md) |
| …fix something that's wrong | [Troubleshooting & FAQ](troubleshooting.md) |
| …make it faster | [Performance](performance.md) |
| …copy a ready-made AI archetype | [Archetype Cookbook](archetype-cookbook.md) |

---

## How-to

| Page | What it covers |
|---|---|
| **[How-To Guides](how-to-guides.md)** | 25 task recipes — hearing, occlusion, search, squads, HUD meters, creatures, difficulty |
| **[Migrating from AIPerception](migrating-from-aiperception.md)** | Concept mapping, step-by-step port, an Epic-parity profile |

## Understand

| Page | What it covers |
|---|---|
| **[Core Concepts](core-concepts.md)** | Confidence, fusion, the lifecycle, awareness, attention, loss reasons, memory |
| **[How It Works](how-it-works.md)** | Architecture, the tick pipeline, LOD, where state lives, extension points |

## Senses & configuration

| Page | What it covers |
|---|---|
| **[The Senses](senses.md)** | All 8 senses, what feeds each one, per-sense formulas and tuning |
| **[Perception Profile Reference](perception-profile.md)** | Every setting on the profile data asset, with defaults |
| **[Sound System](sound-system.md)** | Sound data assets, filters, the per-agent pipeline |
| **[Pain & Damage](pain-and-damage.md)** | Damage reactions, pain types, sense degradation |

## Systems

| Page | What it covers |
|---|---|
| **[Squad & Relationships](squad-and-relationships.md)** | Intel sharing, alerts, combat roles, teams |
| **[Memory & Recall](memory-and-recall.md)** | A tagged store per agent — you decide what is worth remembering |
| **[Evidence & Search](evidence-and-search.md)** | Things left in the world, and a search that gets colder as it goes |
| **[Knowledge & Comms](knowledge-and-comms.md)** | Faction-wide knowledge, descriptions, and what gets lost in the telling |
| **[Player Behavior Model](player-behavior-model.md)** | AI that learns how you play over a session |
| **[Environment & Fairness](environment-and-fairness.md)** | Light, weather, wind, safe rooms, reaction time, telegraphing |
| **[Multiplayer](multiplayer.md)** | Server authority, replicated detection meters, the relay component |

## Scripting

| Page | What it covers |
|---|---|
| **[Blueprint API](blueprint-api.md)** | Every Blueprint node, grouped by category |
| **[Events Reference](events.md)** | Every event, its parameters, exactly when it fires |
| **[Behavior Trees](behavior-trees.md)** | Blackboard wiring, search behaviour driven by loss reason |
| **[Policies](policies.md)** | Take over fusion, threat scoring or attention with your own rule |
| **[Adapters](adapters.md)** | Tell APS how your project stores health and posture |

## Build & ship

| Page | What it covers |
|---|---|
| **[Profile Composition](profile-composition.md)** | Inheritance, per-agent overrides, built-in archetypes, live tuning |
| **[Archetype Cookbook](archetype-cookbook.md)** | Copy-paste settings: stealth guard, dog, zombie, blind creature, sniper, camera, soldier, horror stalker |
| **[Custom Senses](custom-senses.md)** | Build your own sense in Blueprint or C++, and the stimulus bus |
| **[Debugging](debugging.md)** | The 7-mode overlay and the one-node print library |
| **[Explaining & Recording](explaining-and-recording.md)** | Ask why it cannot see you, and read back a moment already gone |
| **[Scale & Crowds](scale-and-crowds.md)** | Significance, frame budget, the crowd tier, environment volumes |
| **[Performance](performance.md)** | LOD tiers, tick budgets, scaling to hundreds of agents |
| **[Troubleshooting & FAQ](troubleshooting.md)** | Every common failure, and the settings that are inert in v3.0 |
| **[Enum & Type Reference](enum-reference.md)** | Every enum value, struct field and constant |

---

## A note on accuracy

Every formula, default value and firing condition in these pages was read out of the v3.0 source rather than inferred from the property names. Where a setting exists in the editor but is not wired up, or where behaviour differs from what its name implies, it is flagged inline with ⚠ rather than quietly omitted. [Troubleshooting](troubleshooting.md) collects those in one place.

---

*Documentation for APS v3.0 · Unreal Engine 5.2 · by AuraGame*

