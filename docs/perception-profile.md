# Perception Profile Reference

The **Perception Profile** is a Data Asset that defines everything about how one AI archetype perceives the world. Swap it at runtime with **Set Profile** to instantly change an AI's entire perceptual character.

Create one: Content Browser → right-click → **Miscellaneous → Data Asset** → `PerceptionProfile`.

> **Every setting below ships with a working default.** Create a profile, assign it, press Play — you get a functional AI. Only open the sections you actually need.

**Section map:** Senses|Setup · Ranges · Detection · Loss · Fusion · Memory · Awareness · Attention · Spatial · Performance · Brain|Emotions · Brain|Threat · Brain|Squad · Brain|PlayerModel · Senses|Pain · Senses|Touch · Fairness · Replication

---

## Senses | Setup

| Setting | Default | Meaning |
|---|---|---|
| `Sense Classes` | Vision, Hearing | Which senses this AI has. Order = slot index, first 8 used. An empty list means the AI perceives nothing at all. |
| `Sense Weights` | empty (= 1.0) | Map of sense class → confidence multiplier |
| `Sense Intervals` | empty (= sense default) | Map of sense class → seconds between evaluations |

---

## Ranges

| Setting | Default | Meaning |
|---|---|---|
| `Vision Max Range` | 2000 cm | Maximum sight distance |
| `Hearing Max Range` | 1500 cm | Maximum hearing distance. Individual sound assets define their own per-type range. |
| `Smell Max Range` | 400 cm | Maximum scent distance |
| `Vibration Detect Range` | 800 cm | Ground vibration range. Passes through walls. |
| `Echo Range` | 1500 cm | Sonar pulse range |
| `b Auto Confidence From Damage` | true | Damage automatically builds confidence toward the instigator. Set false to handle damage yourself via `On AI Damaged`. |

---

## Detection | Vision

| Setting | Default | Meaning |
|---|---|---|
| `Vision Half Angle Deg` | 60° | Focal cone half-angle |
| `Vision Sample Count` | 5 | Ray samples per target (1–5) — **only for the built-in fallback set**. Ignored for targets carrying an APS Target Component, and when `Default Visibility Samples` is filled in. |
| `Darkness Min Detection` | 0.1 | Vision floor in total darkness. `0` = fully blind. |
| `Eye Height Offset` | 64 cm | Eye height above the actor root, when not using a socket |
| `Vision Distance Curve` | none | X = normalised distance [0–1], Y = confidence multiplier |
| `Vision Angle Curve` | none | X = normalised angle [0–1], Y = confidence multiplier |
| `Motion Bonus Curve` | none | X = target speed (cm/s), Y = detectability multiplier [0.5–1.5] |

## Detection | Eyes

| Setting | Default | Meaning |
|---|---|---|
| `b Use Eye Socket` | false | Take the cone origin from a mesh socket instead of `Eye Height Offset` |
| `Eye Socket Name` | `head` | Socket or bone the eyes sit on |
| `Eye Direction Mode` | Actor Rotation | `Actor Rotation` · `Control Rotation` (Epic's behaviour) · `Socket Rotation` (follows the head bone) · `Blended` |
| `Eye Socket Alignment` | Automatic | How the socket's rotation becomes a look direction. **Leave on Automatic** — it derives the correction from the skeleton's reference pose and works on any rig with a raw bone name. |
| `Eye Socket Rotation Offset` | zero | Manual correction, used only with `Manual Offset` alignment |
| `Eye Socket Rotation Weight` | 0.5 | Blended mode: 0 = pure actor rotation, 1 = pure socket |
| `Eye Turn Rate Deg Per Sec` | 0 | Degrees/second the facing may turn. `0` = instant. Set near your mesh's real turn rate so the AI cannot see you before it has turned. |

## Detection | Visibility

| Setting | Default | Meaning |
|---|---|---|
| `Default Visibility Samples` | empty | Sample points used when the target has no APS Target Component. Offsets are local-space, so they rotate with the target. Empty = built-in head/chest/pelvis/shoulders set. |
| `Min Exposure To Register` | 0.0 | Minimum weighted exposure before a target counts as seen at all |
| `Min Visible Points Standing` | 1 | Points that must be visible when standing |
| `Min Visible Points Crouched` | 1 | …when crouched. Raise to 2 for stance-aware stealth. |
| `Min Visible Points Prone` | 1 | …when prone. Raise to 3. |

> All three default to 1 on purpose: adding an APS Target Component must never silently make a character harder to see.

## Detection | Occlusion

| Setting | Default | Meaning |
|---|---|---|
| `Vision Occlusion Channels` | empty (= Visibility) | Collision channels tested for line of sight. Add channels so doors, vehicles and props actually block sight. |
| `b Pawns Block Sight` | false | Other perceivable actors become occluders |
| `Surface Vision Transmission` | empty | Map of physical surface → fraction of vision passing through [0–1]. `1` glass, `0.4` foliage/smoke, `0` solid. Unlisted surfaces block completely. |

## Detection | Cones

| Setting | Default | Meaning |
|---|---|---|
| `b Use Separate Vertical FOV` | false | Make the cone elliptical instead of round |
| `Vision Vertical Half Angle Deg` | 40° | Pitch half-angle |
| `b Enable Peripheral Cone` | false | A wider, weaker cone outside the focal one |
| `Peripheral Half Angle Deg` | 110° | Should exceed `Vision Half Angle Deg` |
| `Peripheral Confidence Scale` | 0.45 | Confidence multiplier for peripheral detections |
| `Peripheral Range Scale` | 0.6 | Fraction of `Vision Max Range` the peripheral cone reaches |
| `b Enable Rear Motion Cone` | false | A rear cone that only registers **moving** targets |
| `Rear Motion Half Angle Deg` | 60° | Measured from directly behind |
| `Rear Motion Min Speed` | 300 cm/s | Minimum target speed to register |
| `Rear Motion Confidence Scale` | 0.25 | Keep low — this is a hint, not sight |
| `Rear Motion Range Scale` | 0.35 | Fraction of `Vision Max Range` |

## Detection | Light

| Setting | Default | Meaning |
|---|---|---|
| `b Use Per Target Light` | false | Sample light at the target instead of one global value |
| `b Trace Sun Shadow` | true | Trace toward the sun to detect shadow. Requires **Set Sun Direction**. |
| `Shadow Light Level` | 0.25 | Light level applied when the target is in shadow |
| `Sun Trace Distance` | 5000 cm | How far the shadow trace reaches |

## Detection | Keyhole

| Setting | Default | Meaning |
|---|---|---|
| `b Keyhole Vision` | false | Narrow at distance, wide up close |
| `Keyhole Near Angle` | 90° | Half-angle at close range |
| `Keyhole Far Angle` | 15° | Half-angle at maximum range |
| `Keyhole Near Distance` | 400 cm | Distance at which the near angle is fully applied |

## Detection | Hearing

| Setting | Default | Meaning |
|---|---|---|
| ⚠ `Hearing Base Threshold` | 0.3 | **Not used in v3.0.** There is no noise floor — control sensitivity with `Suspect Threshold` and the sound filter's `Min Alert Level`. |
| `Wall Absorption Coeff` | 0.4 | Occlusion exponent. For sound-system sounds this is **binary** — `exp(-coeff)` when the path is blocked, `1.0` when clear — not a per-wall count. Smell does count walls. |
| ⚠ `b Sound Event Only Mode` | true | **Not used in v3.0.** Hearing is always event-only regardless of this value. |
| `Sound Filter` | none | Sound Filter Profile asset — which categories and alert levels this AI hears |
| `Sound Accumulation Rate` | 0.5 | Confidence built per second from repeated sounds |
| `Sound Accumulation Hold Time` | 1.0 s | Silence before accumulated confidence starts decaying |
| `Sound Accumulation Decay Rate` | 0.2 | Decay per second after hold expires |

## Detection | Smell, Vibration, Touch, Echolocation

| Setting | Default | Meaning |
|---|---|---|
| `Smell Accumulation Rate` | 0.1 | Scent confidence built per second in range |
| `Smell Decay Rate` | 0.05 | Decay per second out of range |
| `Vibration Min Speed` | 10 cm/s | Minimum target speed to produce detectable vibration |
| ⚠ `Touch Confidence` | 1.0 | **Not used in v3.0.** Contact strength comes from the report call and the per-type multiplier. |
| `Touch Max Impulse For Full Strength` | 1000 | Physics impulse mapping to strength 1.0 |
| `Touch Persistent Accumulation Rate` | 0.3 | Confidence per second while a contact is held |
| `Touch Max Persistent Bonus` | 0.5 | Cap on that bonus |
| `b Echo Directional` | false | Restrict the sonar pulse to the front hemisphere |

---

## Loss

One `Sense Loss Config` per sense. Each has three fields:

- **Grace Time** — seconds after the sense goes silent before transitioning to `Lost`
- **b Direct Cut** — `true` jumps straight to `Lost`; `false` decays down through the thresholds
- **Confidence Decay Multiplier** — how much faster confidence falls once this sense goes quiet

| Setting | Grace | Direct cut | Decay × |
|---|---|---|---|
| `Vision Loss` | 0.3 s | ✅ | 3.0 |
| `Hearing Loss` | 3.0 s | ❌ | 1.0 |
| `Smell Loss` | 20.0 s | ❌ | 0.3 |
| `Touch Loss` | 0.5 s | ❌ | 2.0 |
| `Vibration Loss` | 0.0 s | ❌ | 5.0 |
| `Damage Loss` | 8.0 s | ❌ | 0.5 |
| `Echolocation Loss` | 0.6 s | ✅ | 2.0 |

**Tuning tip:** raising `Vision Loss → Grace Time` to 1.0–1.5 s makes an AI that keeps looking at where you were instead of instantly losing you behind a thin pillar. Great for tense stealth; frustrating if overdone.

---

## Fusion

| Setting | Default | Meaning |
|---|---|---|
| `Corroboration Bonus` | 0.1 | Flat bonus per extra active sense. Keep in 0.05–0.15. `0` = best-sense-only. |
| `Confidence Rise Rate` | 5.0 | How fast confidence climbs while a sense is active. Higher = snappier. |
| `Standing Dwell Rate` | 0.02 | Extra confidence climb per second for a stationary target |
| `Moving Dwell Rate` | 0.12 | Extra confidence climb per second for a target at 600+ cm/s |
| ⚠ `Confidence Decay Smoothing` | 1.5 | **Not used in v3.0** — no code path reads it |
| ⚠ `Confidence Reduce Delay` | 3.0 s | **Not used in v3.0** — no code path reads it |

While any sense is active, confidence rises or holds — it never falls. Reduction happens only once every sense is silent, driven by `Default Decay Exponent` / `Decay Curve` and scaled by the last dominant sense's `Confidence Decay Multiplier`. See [Core Concepts](core-concepts.md).

---

## Memory

| Setting | Default | Meaning |
|---|---|---|
| `Decay Curve` | none | X = seconds since last sensed, Y = decay multiplier. Null = exponential fallback. |
| `Long Term Decay Curve` | none | Much slower curve for long-term memory |
| `Default Decay Exponent` | 0.3 | Exponential decay rate when no curve is set. Higher = forgets faster. |
| `Memory Refresh Bonus` | 0.1 | Confidence head start when re-detecting a previously lost target |
| `Memory Expire Threshold` | 0.05 | Confidence below which a Remembered target expires and its slot is freed |
| `Min Time In Lost` | 0.0 s | Minimum seconds in `Lost` before the AI may move to `Remembered`. Raise it to force longer searches. |

These govern how *belief* decays. The settings below bound the separate, developer-driven [memory store](memory-and-recall.md) — what the AI has been told to remember, as opposed to how sure it is of a contact.

| Setting | Default | Meaning |
|---|---|---|
| `Memory Max Subjects` | 32 | Distinct subjects one agent may hold memories about (1–512). Least recently written is dropped past this |
| `Memory Max Tags Per Subject` | 16 | Distinct tags per subject (1–64). Oldest is dropped past this |
| `Memory Retention Seconds` | 300 s | A subject untouched for this long is released |

---

## Awareness

| Setting | Default | Meaning |
|---|---|---|
| `Suspect Threshold` | 0.15 | Confidence to enter `Suspected` |
| `Detect Threshold` | 0.35 | Confidence to enter `Detected` |
| `Track Threshold` | 0.60 | Confidence to enter `Tracked` |
| `Full Aware Threshold` | 0.85 | Confidence for the `Fully Aware` awareness level |
| `Min Track Duration` | 0.5 s | Minimum time in `Detected` before `Tracked`. Prevents instant lock-on. |

**Difficulty tuning lives here.** Easy: 0.25 / 0.50 / 0.75. Hard: 0.10 / 0.25 / 0.45.

---

## Attention

| Setting | Default | Meaning |
|---|---|---|
| `Attention Stickiness Time` | 2.0 s | Minimum focus time before considering a switch. Guard 2 · zombie 5 · robot 0.5 · animal 3 · boss 1 |
| `Attention Switch Threshold` | 0.2 | How much better a rival target must score to steal focus |

---

## Spatial

| Setting | Default | Meaning |
|---|---|---|
| `b Enable Spatial Model` | true | Last known position, predicted position, uncertainty radius |
| `b Enable Prediction` | false | Extrapolate where the target went after loss. Off by default — on a slow patrolling guard it feels psychic. |
| `Prediction Horizon` | 1.0 s | Seconds ahead to project |
| `Max Prediction Time` | 3.0 s | Hard cap on prediction |
| `Uncertainty Growth Rate` | 50 cm/s | How fast the search radius expands after loss |
| `Max Uncertainty Radius` | 500 cm | Cap on that radius |
| `b Velocity Scaled Uncertainty` | true | Fast-moving targets produce larger uncertainty when lost |
| `Velocity EMA Weight` | 0.3 | Velocity smoothing. Lower = smoother, higher = more reactive. |

---

## Performance

| Setting | Default | Meaning |
|---|---|---|
| `Base Update Interval` | 0.1 s | Perception tick rate. **The single biggest performance lever.** |
| `Maintenance Interval` | 0.5 s | How often the ledger expires and compacts records |
| `Max Tracked Targets` | 16 | Simultaneous tracked targets (1–32). Pre-allocated — lower is cheaper. |
| `Sort Weight Confidence` | 0.5 | Target scoring: confidence weight |
| `Sort Weight Recency` | 0.3 | …recency weight |
| `Sort Weight Proximity` | 0.2 | …proximity weight |
| `Max Sort Distance` | 5000 cm | Distance considered for proximity scoring |
| `b Async Vision Traces` | false | Move visibility tracing off the critical path. Same answer, arriving a frame later. Falls back to synchronous for multi-channel and surface-transmission setups |

## Performance | Crowd

The statistical tier drops line tracing entirely for agents distant enough not to matter, rolling for detection instead. See [Scale & Crowds](scale-and-crowds.md).

| Setting | Default | Meaning |
|---|---|---|
| `b Enable Statistical Tier` | false | Turn the crowd tier on |
| `Statistical Tier Threshold` | 3 | LOD tier at which an agent goes statistical (1–4). A value of 1 makes almost everything statistical |
| `Statistical Detection Rate` | 1.0 | Rolls per second, scaled by distance, facing, light and target motion (0–10) |
| `Statistical Detection Confidence` | 0.5 | Confidence granted on a hit (0–1) |

---

## Brain | Emotions

Five channels, each with a cap, a rise rate and a decay rate. **Set a cap to 0 to disable that emotion entirely** — that is how you build an emotionless robot without touching code.

| Emotion | Max | Rise | Decay |
|---|---|---|---|
| Fear | 1.0 | 0.5 | 0.2 |
| Aggression | 1.0 | 0.8 | 0.3 |
| Curiosity | 1.0 | 0.4 | 0.6 |
| Alertness | 1.0 | 0.6 | 0.1 |
| Panic | 1.0 | 0.3 | 0.15 |

| Setting | Default | Meaning |
|---|---|---|
| `Emotion Active Threshold` | 0.2 | Minimum value for an emotion to be considered active |
| `Panic Override Threshold` | 0.75 | Panic above this overrides every other emotion |

---

## Brain | Threat

Threat score is a weighted blend, then mapped to a level.

| Weight | Default |
|---|---|
| `Threat Weight Confidence` | 0.35 |
| `Threat Weight Damage Received` | 0.30 |
| `Threat Weight Senses` | 0.15 |
| `Threat Weight Relationship` | 0.10 |
| `Threat Weight Approach` | 0.10 |

| Threshold | Default |
|---|---|
| `Threat Threshold Low` | 0.15 |
| `Threat Threshold Medium` | 0.35 |
| `Threat Threshold High` | 0.60 |
| `Threat Threshold Critical` | 0.85 |

| Setting | Default | Meaning |
|---|---|---|
| `Threat Damage Decay Rate` | 0.05 | How fast the damage contribution decays while the target is unsensed. `0` = never forgets who shot it. |

---

## Brain | Squad

| Setting | Default | Meaning |
|---|---|---|
| `Squad Share Range` | 3000 cm | Maximum range to share intel |
| `Min Threat To Share` | Low | Minimum threat before sharing |
| `b Auto Share On Detect` | true | Share automatically at `Detected`. **True = horde/pack behaviour.** |
| `b Auto Share On Track` | false | Share at `Tracked` instead. Only used when auto-share-on-detect is off. |
| `Eligible Roles` | empty (= any) | Combat roles this archetype may claim |

Set both auto-share flags to false for tactical AI that only shares when *you* call `Share Target With Squad`.

---

## Brain | Player Model

| Setting | Default | Meaning |
|---|---|---|
| `b Enable Player Behavior Model` | true | Observe how the player plays |
| `Min Engagements Required` | 3 | Engagements before the model is considered ready (`b Has Enough Data`) |
| `Player Crouch Speed Threshold` | 120 cm/s | Below this counts as crouching |
| `Player Sprint Speed Threshold` | 500 cm/s | Above this counts as sprinting |

---

## Senses | Pain

| Setting | Default | Meaning |
|---|---|---|
| `Pain Vision Floor` | 0.0 | Vision floor at maximum pain. `0` = a blinded AI truly sees nothing. |

## Senses | Touch

| Setting | Default | Meaning |
|---|---|---|
| `b Auto Wire Touch Events` | true | Route the owner's collision hits and overlaps into the Touch sense automatically |
| `b Auto Wire Overlap As Grab` | false | Treat overlaps (not just blocking hits) as persistent contact |

---

## Fairness

Deliberate player-favouring rules. All opt-in, all default to off, so they never change behaviour until you ask for them.

| Setting | Default | Meaning |
|---|---|---|
| `First Spot Reaction Time` | 0.0 s | On **first acquisition only**, the AI must hold the target this long before confidence starts accumulating. This is reaction time — it gives the player a beat to break line of sight after stepping into view. Try 0.3–0.5 s. |
| `Telegraph Threshold` | 0.25 | Confidence at which `On AI Telegraph` fires. Should sit between `Suspect Threshold` and `Detect Threshold`. |
| `b Offscreen Hearing Penalty` | false | Reduce hearing sensitivity while this AI is off every player's screen — stops unseen AI reacting to noise the player never saw them hear |
| `Offscreen Hearing Multiplier` | 0.75 | Hearing multiplier while off-screen |
| `b Respect Never Search Zones` | true | Gates whether this AI's **Is Location In Never Search Zone** query returns results. Zones are **advisory** — nothing is suppressed automatically, so branch on the query in your Behavior Tree. |

---

## Replication

| Setting | Default | Meaning |
|---|---|---|
| `b Replicate Perception State` | false | Replicate a compact per-target summary to clients. Perception itself stays server-authoritative. |
| `Max Replicated Targets` | 3 | Targets included in the summary (1–8). Keep small — this is bandwidth on **every** AI. |
| `Replication Interval` | 0.25 s | Seconds between refreshes |
| `b Use Replication Relevance` | true | Filter the summary before sending it |
| `Replication Relevance Range` | 15000 cm | Drop targets further than this from every viewer. `0` disables the distance test |
| `Replication Min Confidence` | 0.1 | Drop contacts below this — a meter that has barely flickered is not worth the bandwidth |
| `b Skip Unchanged Replication` | true | Do not resend a summary that has not meaningfully moved |
| `Replication Confidence Delta` | 0.02 | How far confidence must move to be worth sending (0–0.5) |

---

## Composition

Inherit from another profile instead of duplicating one. See [Profile Composition](profile-composition.md).

| Setting | Default | Meaning |
|---|---|---|
| `Parent Profile` | none | Inherit everything from this profile, keeping only the fields changed here |
| `Overrides` | empty | Extra changes stamped on after inheritance resolves. Use this to pin a value that equals the class default |

## Archetype

| Setting | Default | Meaning |
|---|---|---|
| `Archetype` | Guard | Which preset **Apply Archetype** stamps on. Nothing reads this at runtime |

**Apply Archetype** writes ordinary values onto ordinary fields. It is a starting point, not a mode.

## Policies

Leave a slot empty and the built-in rule runs. See [Policies](policies.md).

| Setting | Default | Meaning |
|---|---|---|
| `Fusion Policy` | none | How several senses combine into one confidence |
| `Threat Policy` | none | How dangerous a target is |
| `Attention Policy` | none | Which target the AI commits to |

## Workbench

Editor buttons, not runtime settings.

| Button / setting | Does |
|---|---|
| **Validate Profile** | Report settings that are contradictory, unreachable or inert |
| **Show Budget** | Estimate traces and sense evaluations per second for a level of agents |
| **Show Composition** | Log field by field what is inherited from the parent |
| `Compare To` + **Compare With** | Log every field where this profile differs from another |

---

