# Enum & Type Reference

Every enum and struct APS exposes to Blueprint.

---

## Enums

### EBeliefLifecycleState — per-target state

| Value | Meaning |
|---|---|
| `Undetected` | Slot exists, confidence below threshold |
| `Suspected` | Above `Suspect Threshold` — something is there |
| `Detected` | Above `Detect Threshold` — confirmed |
| `Tracked` | Above `Track Threshold` — full engagement |
| `Lost` | Senses silent, grace expired |
| `Remembered` | Decaying in long-term memory |
| `Expired` | Forgotten, slot freed |

### EAwarenessLevel — per-AI awareness

`Unaware` · `Peripheral` · `Suspicious` · `Alerted` · `Fully Aware`

### ELossReason — why contact was lost

| Value | Meaning | Recommended search |
|---|---|---|
| `Unknown` | Fallback | Broad area search |
| `Occluded` | Broke line of sight behind geometry | Go to last known position, search the cover |
| `OutOfRange` | Left the sense range | Move to last known, expand outward using `Loss Direction` |
| `SoundFaded` | The noise stopped | Investigate the area, do not chase |
| `ScentLost` | Scent dissipated | Follow `Loss Direction` as a trail |
| `SensorDropout` | Signal stopped, no geometric reason | Short investigation, resume patrol |
| `TargetDestroyed` | The actor is gone | Clear the target |

### EStimulusSource — which sense drove this

`Unknown` · `Vision` · `Hearing` · `Smell` · `Damage` · `Shared Intel`

### EThreatLevel

`None` · `Low` · `Medium` · `High` · `Critical`

### ETargetRelationship

| Value | Meaning | Threat modifier |
|---|---|---|
| `Unknown` | No rule matched | 0.5 |
| `Neutral` | Civilians, wildlife | 0.3 |
| `Friendly` | Allied faction | 0 — threat forced to `None` |
| `Teammate` | Same squad | 0 — threat forced to `None` |
| `Enemy` | Hostile | 1.0 |
| `HighValue` | Priority target | 1.2 |
| `Feared` | Something to flee from | 1.5 |

`Friendly` and `Teammate` short-circuit threat assessment entirely — score 0, level `None`, regardless of confidence or damage taken.

### EEmotionType — dominant emotion

`Calm` · `Curious` · `Alert` · `Aggressive` · `Fearful` · `Panicked`

### ECombatRole

`None` · `Approacher` · `Flanker` · `Suppressor` · `Investigator` · `Support`

### EContactType — Touch sense

`Bump` · `Grab` · `Explosion` · `Collision`
Priority when several land in one tick: **Explosion > Grab > Collision > Bump**

### ESurfaceType — Vibration sense

`Any` · `Ground` · `Water` · `Metal`

### EAPSStance — target posture

`Standing` · `Crouched` · `Prone`

### EAPSVisionCone — which cone detected

`None` · `Focal` · `Peripheral` · `RearMotion`

### EAPSEyeDirectionMode

| Value | Meaning |
|---|---|
| `Actor Rotation` | Cheapest, matches the body capsule |
| `Control Rotation` | Epic's behaviour — snaps to `MoveTo` / `SetFocus` |
| `Socket Rotation` | Follows the head bone animation |
| `Blended` | Mix of actor and socket by `Eye Socket Rotation Weight` |

### EAPSEyeSocketAlignment

| Value | Meaning |
|---|---|
| `Automatic` | **Recommended.** Derives the correction from the skeleton's reference pose. Works with a raw bone name on any rig. |
| `Raw Rotation` | Use the socket's rotation exactly as authored |
| `Manual Offset` | Apply `Eye Socket Rotation Offset` by hand |

### ESoundCategory

`Enemy` · `Friendly` · `Animal` · `Environment` · `Custom`

### ESoundAlertLevel

`Whisper` · `Normal` · `Loud` · `Explosive`

### EPainState — legacy health path

| Value | Health ratio |
|---|---|
| `Healthy` | > 0.75 |
| `Wounded` | > 0.40 |
| `Critical` | > 0.15 |
| `Near Death` | ≤ 0.15 |

### EAPSBeliefSubject — what a belief is about

A belief no longer has to be about an actor. See [Core Concepts](core-concepts.md#11-beliefs-about-places).

| Value | Meaning |
|---|---|
| `Actor` | A specific actor. The original behaviour |
| `Location` | A place something happened, with no known author |
| `Descriptor` | A described presence — "someone in a red coat" — not yet resolved to an actor |
| `Object` | A perceivable thing rather than a person — a body, a forced lock |

### EAPSPerceptionBlocker — why a sense is silent

Returned by **Get Sense Blocker**. See [Explaining & Recording](explaining-and-recording.md).

| Value | Meaning |
|---|---|
| `None` | Nothing is blocking it |
| `Out Of Range` | Beyond that sense's reach |
| `Outside Cone` | In range, but outside the cone |
| `Occluded` | Line of sight blocked by geometry |
| `Below Min Exposure` | Visible, but not enough of the target is exposed |
| `Too Few Visible Points` | Not enough sample points cleared for this stance |
| `Target Opted Out` | The target excluded itself from this sense |
| `Suppressed By Pain` | The AI is too hurt to use this sense |
| `Fairness Reaction Hold` | The telegraph window is running — deliberate, not a fault |
| `Not Evaluated This Tick` | This sense did not run on this tick |
| `No Context` | The sense had nothing to evaluate against |

### EAPSEvidenceOp — how evidence moves belief

Used by **Add Target Evidence**.

| Value | Meaning |
|---|---|
| `Raise (floor)` | Belief is at least `Value`. What **Set Target Confidence** does |
| `Clamp (ceiling)` | Belief is at most `Value` — a disguise that stops the AI ever becoming certain while it holds |
| `Lower (relative reduction)` | Belief settles `Value` *below* where the senses alone would have put it. Applies only while something is actually being sensed |
| `Invalidate (force zero)` | Belief forced to zero, and the target steps back down the lifecycle. The AI concluding it was a false alarm |

!!! note "`Clamp` is absolute, `Lower` is relative"
    A clamp of 0.5 caps belief at 0.5 no matter how good the evidence gets.
    A lower of 0.5 means "half a unit less sure than the senses say" — doubt that
    scales with the evidence rather than a hard ceiling.

    `Lower` only applies while a sense is actually reading. Once every sense is
    silent there is no reading left to reduce and normal memory decay owns the
    fade; use `Invalidate` to force belief down regardless.

### EAPSArchetype — built-in profile presets

See [Profile Composition](profile-composition.md).

| Value | Character |
|---|---|
| `Guard` | Alert, forward-facing, commits quickly and holds on |
| `Civilian` | Wide senses, high thresholds, short memory |
| `Stalker` | Narrow, long look; a memory that does not let go |
| `Military Patrol` | Longest sight, shares with the squad, holds through cover |
| `Wildlife` | Smell and hearing over sight; reacts before it is sure |

### EAPSCommsChannel — how information travels

APS Knowledge module. See [Knowledge & Comms](knowledge-and-comms.md).

| Value | Delay | Position error | Trait loss | Confidence |
|---|---|---|---|---|
| `Direct (witnessed)` | 0 s | 0 cm | 0% | ×1.00 |
| `Shout` | 0.5 s | 300 cm | 25% | ×0.85 |
| `Radio` | 2 s | 600 cm | 35% | ×0.75 |
| `Report (in person)` | 8 s | 1500 cm | 55% | ×0.60 |

### EPerceptionDebugMode

`Sense` · `Memory` · `Brain` · `Squad` · `Delegates` · `Player Model` · `Environment`

---

## Structs

### Belief Record

Everything the AI believes about one target. Returned by `Get Belief Data`, `Get Top Target Belief`, `Get Targets Sorted By Score`.

**Identity:** `Target` · `Target ID`
**Confidence:** `Fused Confidence` · `Smoothed Confidence` · `Lifecycle State`
**Timing:** `Time Since Last Sensed` · `Total Time Tracked` · `Time In Current State` · `First Detected Time`
**Space:** `Last Known Position` · `Estimated Velocity` · `Estimated Acceleration` · `Uncertainty Radius` · `Predicted Position`
**Memory:** `Long Term Memory Strength` · `Detection Count` · `b Was Ever Detected` · `Episodes`
**Cover:** `Last Seen Cover Actor` · `Last Seen Cover Position` · `b Was In Cover`
**Loss:** `Loss Reason` · `Loss Direction`
**Brain:** `Primary Stimulus Source` · `Dominant Stimulus Source` · `Threat Level` · `Threat Score` · `Damage Received From Target` · `Damage Dealt To Target` · `b Is Known Threat` · `Encounter Count` · `Last Threat Level` · `Relationship`

### Perception Sense Result

One sense's output for one target.

| Field | Meaning |
|---|---|
| `Confidence` | 0–1 belief from this sense |
| `Raw Signal Strength` | Pre-falloff signal |
| `Estimated Location` | Where this sense thinks the target is |
| `Location Accuracy` | 0–1 precision of that estimate |
| `Sense ID` | The sense's name |
| `b Is Active` | Is this sense detecting right now |
| `Exposure Ratio` | Vision only — weighted fraction of sample points with a clear line |
| `Visible Point Count` | Vision only — unweighted count |
| `Detected By Cone` | Vision only — which cone produced it |

### Perception Episode

One past engagement. Up to 5 per target, ring buffer, written on `Detected`/`Tracked` → `Lost`.

`How Lost` · `State When Lost` · `Location When Lost` · `AI Camera Direction` · `Target Flee Direciton` · `Engagement Duration` · `Peak Threat Level` · `World Time Stamp`

Two notes: `Target Flee Direciton` is misspelled in v3.0 — that is the actual pin name. `Engagement Duration` holds the target's *cumulative* tracked time, not the length of that single engagement.

### Perception Context

Passed to every sense's `Evaluate`.

`Owner Actor` · `Owner Location` · `Owner Rotation` · `Owner Eye Location` · `Owner Eye Forward` · `Delta Time` · `Ambient Light Level` · `Weather Visibility Mod` · `Target Location` · `Target Velocity` · `b Owner Offscreen` · `Environment`

> Senses should prefer `Owner Eye Forward` over `Owner Rotation` — it is the facing after eye-mode resolution and turn-rate limiting.

### Environment State

| Field | Range | Effect |
|---|---|---|
| `Light Level` | 0–1 | Vision: `Lerp(Darkness Min Detection, 1, level)`, unless per-target light overrides it |
| `Rain Intensity` | 0–1 | Vision, Hearing and Smell all multiplied by `1 − rain` |
| `Wind Speed` | 0–2000 | Smell ×1.0 → ×0.25 at 800 and above, outdoors only |
| `Wind Direction` | vector | Stored only. The Smell sense reads its own `Wind Direction` property for the downwind bonus |
| `b Is Indoors` | bool | Smell ×1.2, and wind is ignored |
| `Time Of Day` | 0–24 | Informational |

### Emotional State

`Fear` · `Aggression` · `Curiosity` · `Alertness` · `Panic` (all 0–1) · `Dominant Emotion` · `Fear Input`

### Player Behavior Model

`Crouch Ratio` · `Sprint Ratio` · `Walk Ratio` · `Stealth Ratio` · `Aggression Ratio` · `Recent Hide Locations` · `Custom Behavior Ratios` · `Engagement Count` · `b Has Enough Data`

Movement ratios use the target's **observed posture** when anything reports one, and fall back to speed bands only when nothing does. `Stealth Ratio` and `Aggression Ratio` are complements of one measurement and always sum to 1. `Recent Hide Locations` holds up to 5 positions at least 200 cm apart. See [Player Behavior Model](player-behavior-model.md).

### Sense Loss Config

`Grace Time` · `b Direct Cut` · `Confidence Decay Multiplier`

### APS Visibility Sample

`Socket Name` · `Offset` (local space) · `Weight` (0–1)

### APS Stimulus Event

`Stimulus Tag` · `Location` · `Source` · `Strength` · `Radius` · `Max LOD Tier` · `b Requires Clear Path` · `b Team Filter`

### APS Replicated Target State

`Target` · `Confidence` · `State` · `Threat Level` · `Last Known Position`

### Perception Debug Settings

**Master:** `b Enabled` · `b Editor Preview`
**Text:** `b Screen Panel` · `b Show Sparkline` · `b Show Target Text` · `b Show AI Text` · `Debug Mode` · `Text Scale` · `b Scale Text With Distance` · `b Show Emotion Bars` *(not read)* · `b Show Legend`
**World geometry:** `b Vision Cone` · `b Hearing Rings` · `b Smell Range` · `b Awareness Arc` · `b Last Known And Uncertainty` · `b Predicted Position` · `b Sound Event Lines` · `b Sense Beams` · `b Sense Fields` · `b Environment Visuals` · `Sound Linger Seconds`
**Style:** `Palette` · `b Animated Visuals` · `b Cone Volume` · `b Secondary Cones` · `b Draw Through Walls` · `Line Thickness` · `b Ground Anchor`
**Controls:** `b Freeze Snapshot` · `b Pause Perception` · `Agent Scope` · `b Nearest AI Only` *(legacy alias)*

---

## Classes

### Components

| Class | Blueprint name | Purpose |
|---|---|---|
| `UPerceptionCore` | **APS Core** | The main perception component. One per AI. |
| `UAPPerceptionListener` | **APS Perception Listener** | No-binding overridable events |
| `UAPSTargetComponent` | **APS Target Component** | Makes an actor properly perceivable |
| `URelationshipComponent` | **APS Relationship** | Team and class relationship rules |
| `UAPSPerceptionRelay` | **APS Perception Relay** | Carries replicated state when the owner cannot replicate. Auto-managed. |
| `UAPSEnvironmentComponent` | **APS Environment** | Local light, weather, wind and sense range inside a radius |
| `UAPSObserverComponent` | **APS Observer** | Publishes one AI's perception into faction knowledge. Knowledge module |
| `UAPSSignatureComponent` | **APS Signature** | Describable traits on an actor. Knowledge module |
| `UAPSEvidenceComponent` | **APS Evidence** | A trace left in the world that an AI can discover. Knowledge module |
| `UAPSSearchComponent` | **APS Search** | Where to look next, as a probability field. Knowledge module |

### Data assets

| Class | Purpose |
|---|---|
| `UPerceptionProfile` | All perception settings for one archetype |
| `USoundTypeDefinition` | One kind of sound |
| `USoundFilterProfile` | Which sounds an archetype hears |
| `UPainTypeDefinition` | One kind of pain and what it impairs |
| `UAPSQualityProfile` | Cost controls layered on a profile without resetting belief |

### Policies and adapters

| Class | Blueprint name | Purpose |
|---|---|---|
| `UAPSFusionPolicy` | APS Fusion Policy | How several senses become one confidence |
| `UAPSThreatPolicy` | APS Threat Policy | How dangerous a target is |
| `UAPSAttentionPolicy` | APS Attention Policy | Which target the AI commits to |
| `UAPSSignificancePolicy` | APS Significance Policy | Which agents deserve CPU. Lives on the subsystem |
| `IAPSHealthProvider` | APS Health Provider | Interface: how hurt an actor is |
| `IAPSStanceProvider` | APS Stance Provider | Interface: what posture an actor is in |

### Senses

| Class | Display name | Sense ID |
|---|---|---|
| `USenseUnit` | *(abstract base)* | — |
| `USenseUnit_Vision` | Vision Sense | `Vision` |
| `USenseUnit_Hearing` | Hearing Sense | `Hearing` |
| `USenseUnit_Smell` | Smell Sense (Custom Example) | `Smell` |
| `USenseUnit_Touch` | Sense: Touch | `Touch` |
| `USenseUnit_Vibration` | Sense: Vibration | `Vibration` |
| `USenseUnit_Damage` | Damage Sense | `Damage` |
| `USenseUnit_Pain` | Sense: Pain / Health | `Pain` |
| `USenseUnit_Echolocation` | Sense: Echolocation / Sonar | `Echolocation` |

### Function libraries & subsystems

| Class | Purpose |
|---|---|
| `UPerceptionSoundSystem` | `Emit Sound` / `Emit Sound At Location` |
| `UAPSDebugHelper` | Print nodes and squad debug utilities |
| `UAPSSubsystem` | World state, registry, spatial index, significance, never-search zones, stimulus bus |
| `UAPSKnowledgeSubsystem` | Faction knowledge, comms channels and alert level. Knowledge module |

---

## Constants

| Constant | Value | Meaning |
|---|---|---|
| Max sense slots | **8** | Senses per AI. Extra entries in `Sense Classes` are ignored. |
| Max episodes | **5** | Stored engagements per target |
| Max tracked targets | **1–32** | Configurable, default 16 |
| LOD tiers | **0–4** | 0 = full rate, 4 = suspended. Derived from significance, not raw distance |
| Significance bands | **0.75 / 0.50 / 0.30 / 0.15** | Score thresholds for tiers 0 to 3 |
| Spatial grid cell | **1500 cm** | Candidate broadphase, rebuilt every 0.2 s |
| Place-belief merge cell | **400 cm** | Reports with the same tag inside one cell merge into one belief |
| Meaningful confidence floor | **0.02** | A sense reporting below this counts as silent |
| Recent hide locations | **5** | Distinct spots, min 200 cm apart |
| Lifecycle hysteresis | **0.04** | Confidence must fall this far below a threshold to step down |
| Focal cone tolerance | **×1.1** | Applied when `b Use Separate Vertical FOV` is off |
| Exposure EMA | **0.35** | Snaps instead when exposure hits 0 or changes by >0.4 |
| Target gather rate | **max(0.2 s, tick)** | At most 5 Hz |
| Damage → confidence | **/ 100** | 100 damage in one hit = full confidence |
| Off-screen cone | **~75°** | Dot > 0.25 against player camera 0's forward |

### Fixed gather ranges

Target gathering uses the largest of `Vision Max Range`, `Hearing Max Range` and each sense's declared maximum. Two senses declare a **fixed** value that does not follow their profile setting:

| Sense | Declared gather range | Profile setting it ignores |
|---|---|---|
| Vibration | 800 cm | `Vibration Detect Range` |
| Echolocation | 2000 cm | `Echo Range` |
| Smell | follows `Smell Max Range` | — |
| Touch | 50 cm | — |

Raising either profile value beyond its declared range needs another sense on the same profile reaching that far, or distant targets are never handed to it.

## Log category

All APS logging goes to `LogAdvancedPerception`.

```bash
Log LogAdvancedPerception Verbose
```

---

## Console commands

| Command | Does |
|---|---|
| `aps.Tune <PropertyName> <Value>` | Set a profile value on every running agent, without touching the asset. Gone at the next launch |
| `aps.UseSpatialIndex 0\|1` | Turn the spatial candidate index off or on. For A/B testing only |

---

## Persistence

**APS writes nothing to disk.** There are no save files, no `Saved/` folder, and no cross-session state of any kind.

Both the [memory store](memory-and-recall.md) and the [player behaviour model](player-behavior-model.md) live for the session and no longer — a freshly spawned AI has met nobody and remembers nothing until it perceives something itself.

To persist either, read the values you care about and write them into your own save game. Your game knows what a save means; APS does not, and guessing would be worse than asking.

---

