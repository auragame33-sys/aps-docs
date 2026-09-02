# The Senses

An AI runs up to **8 senses at once**. Which ones it has is decided entirely by the `Sense Classes` array on its Perception Profile — so a guard, a zombie and a guard dog are three data assets, not three code paths.

## Adding and removing senses

Open your profile → **Senses | Setup** → `Sense Classes`.

| Class (as shown in the dropdown) | Sense ID | Needs input from you? |
|---|---|---|
| **Vision Sense** | `Vision` | No — fully automatic |
| **Hearing Sense** | `Hearing` | **Yes** — call `Emit Sound` |
| **Smell Sense (Custom Example)** | `Smell` | No — automatic while in range |
| **Sense: Touch** | `Touch` | No if auto-wiring is on, otherwise report contacts |
| **Sense: Vibration** | `Vibration` | No for moving targets; optional explicit events |
| **Damage Sense** | `Damage` | No — all UE damage events are auto-wired |
| **Sense: Pain / Health** | `Pain` | **Yes** — call `Report Pain From Definition` |
| **Sense: Echolocation / Sonar** | `Echolocation` | No — fully automatic |

Order in the array is the slot index. The first 8 entries are used; extras are ignored.

### Sense weights

**Senses | Setup → Sense Weights** — a map of sense class → multiplier. Anything not listed is `1.0`.

```
Guard dog:   Smell 1.5,  Hearing 1.2,  Vision 0.6
Sniper:      Vision 1.3,  Hearing 0.8
Zombie:      Hearing 1.4,  Vibration 1.3,  Vision 0.4
```

### Sense intervals

**Senses | Setup → Sense Intervals** — a map of sense class → seconds between evaluations. Anything not listed uses that sense's own default (Vision 0.15 s, Hearing 0.1 s, Smell 0.25 s, Echolocation 0.3 s).

Slowing an expensive sense down is the cheapest performance win available. Vision at 0.3 s on background AI is usually indistinguishable from 0.15 s.

---

## Tuning a sense's own properties

Most sense tuning lives on the **Perception Profile** (ranges, angles, thresholds, loss behaviour). But a few senses — **Smell** and **Touch** in particular — also carry their own `EditAnywhere` properties on the sense class itself.

Because `Sense Classes` holds a **class**, not an instance, those properties come from the **class defaults**. To change them:

1. Content Browser → right-click → **Blueprint Class**
2. Search for the sense (e.g. `SenseUnit_Smell`) and pick it as the parent
3. Name it `BP_Sense_Smell_Bloodhound`, open it, edit the values in **Class Defaults**
4. Put **your Blueprint** into `Sense Classes` instead of the base class

This is also how you make two archetypes that share a profile shape but differ in one sense's internals.

---

## Vision

**Fully automatic.** Nothing to call — if the target is in range, in the cone, lit, and not occluded, confidence rises.

### What it evaluates, in order

1. **Camouflage** — a `Visibility Multiplier` of 0 on the target's APS Target Component exits immediately, before any traces are spent
2. **Range** — distance falloff, optionally shaped by `Vision Distance Curve`
3. **Cone** — focal first, then peripheral, then rear-motion. Outside all three, the sense returns nothing.
4. **Visibility** — traces to the weighted sample points → a continuous **exposure ratio** 0–1
5. **Stance gate** — is the number of visible points enough for the target's current stance?
6. **Light** — global ambient, or a per-target sun-shadow trace
7. **Motion bonus** — a faster target is easier to spot, shaped by `Motion Bonus Curve`

### The confidence formula

Everything multiplies. Any single factor at zero means no detection:

```
Confidence = DistanceFalloff × AngleFalloff × ExposureRatio × LightFactor
           × MotionBonus × WeatherMod × VisibilityMultiplier × ConeScale
```

| Factor | Default behaviour (no curve assigned) |
|---|---|
| `DistanceFalloff` | `1 − (dist / coneRange)²` — quadratic, so confidence holds up well until roughly two-thirds of range |
| `AngleFalloff` | `cos(normalisedAngle × 90°)` — full at dead centre, zero at the cone edge |
| `ExposureRatio` | Weighted fraction of sample points with a clear line |
| `LightFactor` | `Lerp(DarknessMinDetection, 1.0, lightLevel)` |
| `MotionBonus` | `Lerp(1.0, 1.3, clamp(speed / 600, 0, 1))` — up to a 30% bonus for a sprinting target |
| `WeatherMod` | The subsystem's weather modifier |
| `ConeScale` | `1.0` focal · `Peripheral Confidence Scale` · `Rear Motion Confidence Scale` |

Assigning `Vision Distance Curve`, `Vision Angle Curve` or `Motion Bonus Curve` replaces the corresponding default. Curve outputs are clamped to `[0,1]` for distance and angle, and `[0.5, 1.5]` for motion.

The angle test is measured against the **first sample point** — the head, by convention — not the actor's centre. A target whose head clears cover is evaluated as a head, not a pelvis.

### Multi-point visibility

Epic traces one ray to the capsule centre. Stand behind a waist-high crate with your head fully exposed and you register as *not seen*. APS traces a **set** of points and returns the weighted fraction that have a clear line.

```
                                              ○ head      w 1.0   ✓ clear
   AI eye                        ┄┄┄┄┄┄┄┄┄┄┄┄►
      ●┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄►  ○ shoulder  w 0.6   ✓ clear
       ┆ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄╳         ○ chest      w 0.9   ✗ blocked
       ┆ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄╳         ○ shoulder   w 0.6   ✗ blocked
       ┆ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄╳ ██████  ○ pelvis     w 0.7   ✗ blocked
                         crate

   exposure = (1.0 + 0.6) ÷ (1.0 + 0.9 + 0.7 + 0.6 + 0.6) = 0.41

   →  41% exposed  →  confidence scaled to 41%  →  a slow, uncertain detection
      Epic would report:  "not seen"
```

Peek your head over the crate and exposure climbs; duck fully and it snaps to zero. That continuous middle ground is the whole reason partial cover feels like cover.

Where the points come from, in priority order:

1. The target's **APS Target Component** `Visibility Samples` — which ships **pre-filled with 5 entries**, so a component that exists always wins
2. The observing profile's `Default Visibility Samples`, if you filled that array in
3. A built-in head / chest / pelvis / shoulders set, count-limited by `Vision Sample Count`

!!! warning "`Vision Sample Count` only limits option 3"
    Any target carrying an APS Target Component is traced against all of that component's samples, five by default, no matter what `Vision Sample Count` says. To cut trace cost on targets that have the component, remove entries from **its** `Visibility Samples` array. A quality profile's `Max Vision Samples` caps every source at once. See [Performance](performance.md).

The component's defaults are `head` (weight 1.0), a chest offset (0.9), a pelvis offset (0.7), and `clavicle_l` / `clavicle_r` (0.6 each). Points are resolved from **mesh sockets** each evaluation, so they follow animation — leaning out of cover genuinely exposes your head. An entry whose socket does not exist on the skeleton falls back to its local-space offset rather than being dropped, so a mis-typed bone name degrades instead of silently disabling the sample.

Two gates control what counts:

- **Min Exposure To Register** — the minimum weighted exposure before the target registers at all. `0` = any non-zero exposure is enough. Raise it so a sliver of shoulder is not a full detection.
- **Min Visible Points (Standing / Crouched / Prone)** — the count of points that must be visible per stance. All three default to `1`, so adding a Target Component never silently makes a character harder to see. Set Crouched `2` and Prone `3` for stance-aware stealth.

A point only counts toward the *stance* threshold when more than **50%** of vision survives the path to it. A point behind heavy foliage still adds to the exposure ratio, but does not count as "visible" for the stance gate.

Results are exposed on the sense result as `Exposure Ratio` and `Visible Point Count`. Exposure is smoothed with an EMA so a player standing at a geometry edge does not make confidence flicker — but it **snaps instantly** when exposure hits zero, or when it changes by more than 0.4. Ducking fully behind a wall is registered immediately; stepping fully into the open is too.

### The three cones

```
                              forward
                                 ▲
                                 │
          ╲                      │                      ╱
            ╲      FOCAL         │        FOCAL       ╱
              ╲   ×1.00 conf     │      ×1.00 conf  ╱
                ╲   full range   │     full range ╱
                  ╲              │              ╱
    ╲               ╲────────────┼────────────╱               ╱
      ╲   PERIPHERAL  ╲          │          ╱  PERIPHERAL   ╱
        ╲  ×0.45 conf   ╲        │        ╱   ×0.45 conf  ╱
          ╲  0.6× range    ╲     │     ╱    0.6× range  ╱
            ╲                 ╲  │  ╱                 ╱
              ╲─────────────────╲│╱─────────────────╱
                                 ●  AI
                              ╱  │  ╲
                            ╱    │    ╲
                          ╱  REAR-MOTION ╲
                        ╱   ×0.25 conf    ╲
                      ╱     0.35× range     ╲
                    ╱   moving targets only   ╲
                                 ▼
```

Cones are resolved in order — focal first, then peripheral, then rear-motion. Outside all three, vision returns nothing at all.

| Cone | Setting | Purpose |
|---|---|---|
| **Focal** | `Vision Half Angle Deg` (60°) | The main cone. Full confidence. Note: with `b Use Separate Vertical FOV` **off**, the focal test carries a 10% tolerance — a 60° setting admits targets out to 66°. |
| **Peripheral** | `b Enable Peripheral Cone` → `Peripheral Half Angle Deg` (110°) | Wider, weaker, shorter. `Peripheral Confidence Scale` 0.45, `Peripheral Range Scale` 0.6. Catches movement at the edge of sight. |
| **Rear motion** | `b Enable Rear Motion Cone` → `Rear Motion Half Angle Deg` (60° measured from directly behind) | Only registers targets moving faster than `Rear Motion Min Speed`. Confidence scale 0.25, range scale 0.35. Stops players walking up behind a guard with total impunity, without making it omniscient. |

`b Use Separate Vertical FOV` gives the cone a distinct pitch half-angle, making it elliptical instead of perfectly round — essential in games with verticality.

The detection reports which cone produced it via `Detected By Cone` on the sense result.

### Keyhole vision

`b Keyhole Vision` makes the cone **narrow at distance and wide up close** — the shape used in *The Last of Us*.

```
        near (≤ 400 cm)                    far (max range)
              ╱                                   ╲
        ╱                                            ╲
   ╱         90° wide                    15° narrow    ╲
  ●═══════════════════════════════════════════════════════►
  AI    ╲                                             ╱
        ╲                                            ╱
              ╲                                   ╱

   you can slip past at 20 m by drifting off centre …
   … but at 3 m the guard catches you in a wide arc
```

| Setting | Meaning |
|---|---|
| `Keyhole Near Angle` (90°) | Half-angle at close range |
| `Keyhole Far Angle` (15°) | Half-angle at max range |
| `Keyhole Near Distance` (400) | Distance at which the near angle is fully applied |

The practical effect: you can sneak past a guard at 20 m by staying slightly off his centre line, but at 3 m he catches you in a wide arc. It reads as far more natural than a fixed cone.

### Eye origin and facing

Epic anchors the cone to the actor root plus a fixed height, facing the **control rotation** — which has no connection to the mesh. Head turns, aim offsets and lean animations never move it, and the cone snaps instantly to a `MoveTo` target before the body has turned.

**Detection | Eyes** fixes both halves:

| Setting | What it does |
|---|---|
| `b Use Eye Socket` | Take the cone's **origin** from a mesh socket instead of `Eye Height Offset` |
| `Eye Socket Name` | Typically `head`, `eyes`, or your own socket |
| `Eye Direction Mode` | Where the **facing** comes from: `Actor Rotation` (default, cheapest), `Control Rotation` (Epic's behaviour), `Socket Rotation` (follows the head bone), `Blended` |
| `Eye Socket Alignment` | How the socket's rotation becomes a look direction — **leave on `Automatic`** |
| `Eye Socket Rotation Weight` | Blended mode only: 0 = pure actor rotation, 1 = pure socket |
| `Eye Turn Rate Deg Per Sec` | Degrees/second the facing may turn. `0` = instant. **Set this near your mesh's real turn rate** so the AI cannot see you before it has physically turned to look. |

!!! info "Why `Automatic` matters"
    A bone's local axes are arbitrary. On Epic's mannequin the head bone's X axis runs *up the neck*, so binding a cone straight to it aims the AI at the sky. `Automatic` reads the skeleton's reference pose, works out how the bone is oriented relative to the character, and cancels it. You can point `Eye Socket Name` at a raw bone name like `head` on any rig with zero other setup.

### Occlusion

| Setting | What it does |
|---|---|
| `Vision Occlusion Channels` | Which collision channels block sight. Empty = `Visibility` only. Epic tests one channel, which is why AI routinely sees through doors and vehicles. |
| `b Pawns Block Sight` | Other perceivable actors become occluders — bodies block sight |
| `Surface Vision Transmission` | Map of physical surface → fraction of vision that **passes through** [0–1]. `1` = glass, `0.4` = foliage or smoke, `0` = solid. Surfaces not listed block completely. |

Per-surface transmission is what lets a player hide in tall grass and be *partly* visible instead of fully hidden or fully exposed.

### Light

| Setting | What it does |
|---|---|
| `Darkness Min Detection` | Vision floor in total darkness. `0` = fully blind in the dark; `0.1` default. |
| `b Use Per Target Light` | Sample light **at the target** instead of one global value. Without this a dark corner is indistinguishable from broad daylight. |
| `b Trace Sun Shadow` | Trace from the target toward the sun to decide if it is in shadow. Requires **Set Sun Direction** on the subsystem. |
| `Shadow Light Level` | Light level applied when the target is in shadow (0.25) |
| `Sun Trace Distance` | How far the shadow trace reaches (5000) |

Resolution order, when `b Use Per Target Light` is **on**:

1. The target's **APS Target Component → Light Level Override**, if it is ≥ 0
2. The sun-shadow trace, if `b Trace Sun Shadow` is on **and** `Set Sun Direction` has been called — a blocked trace yields `min(ambient, ShadowLightLevel)`, so shadow can only darken, never brighten
3. Global ambient light

!!! warning "`Light Level Override` does nothing while `b Use Per Target Light` is off"
    The whole per-target light path is skipped and global ambient is used. If you drive lighting from your own light-gem system, you must still tick this box.

### Loss behaviour

Grace 0.3 s, **direct cut**, decay multiplier ×3, loss reason `Occluded`. Vision sees instantly and loses instantly.

---

## Hearing

**Event-driven. Sounds only exist if you emit them.** There is no passive velocity-based hearing.

### Emitting sound

Two Blueprint nodes, both static (no component reference needed):

| Node | Use for |
|---|---|
| **Emit Sound** (`Source`, `Sound Type`) | Sounds attached to an actor — footsteps, reloads, grunts, vehicles |
| **Emit Sound At Location** (`Sound Location`, `Sound Type`) | Sourceless sounds — explosions, traps, breaking glass, falling objects |

Both take a **Sound Type Definition** data asset, which carries loudness, range, category, alert level, priority and LOD tier. See [Sound System](sound-system.md) for the full workflow.

### Per-agent pipeline

When a sound is emitted, every agent goes through this filter chain — cheapest first, so distant AI cost almost nothing:

1. **Range** — beyond `Sound Type → Max Range`? skipped
2. **LOD tier** — agent LOD above `Sound Type → Max LOD Tier`? skipped
3. **Category** — does the agent's `Sound Filter` accept this category?
4. **Alert level** — is it at or above the filter's `Min Alert Level`?
5. **Team** — same team as the source and `b Filter Friendly Team` is on? skipped
6. **Wall trace** — occlusion check, done last because it is the expensive one

### The confidence formula

```
Confidence = Loudness × DistanceAttenuation × WallFactor × WeatherMod

Loudness              = SoundType.BaseLoudness × SoundFilter.LoudnessMultiplier
DistanceAttenuation   = 1 − (dist / SoundType.MaxRange)²
WallFactor            = 1.0 if the path was clear, else exp(−WallAbsorptionCoeff)  (≈0.67 at the default 0.4)
```

Two things follow:

- **The wall penalty is binary, not per-wall.** A sound from the sound system either had a clear path or it did not; one wall and five walls attenuate identically. (The per-wall counting path only runs for legacy sounds emitted without a Sound Type Definition.)
- **Loudness above 1.0 mainly extends useful range, not peak confidence.** Confidence is clamped to 1, so a `Base Loudness` of 3.0 does not make a close gunshot "three times louder" — it keeps confidence pinned at 1.0 out to a much greater distance. That is usually what you want; just do not expect the number to behave linearly.

### Accumulation

Hearing builds. One footstep is a blip; a series of them in the same place is a detection. The final value is `max(instant, accumulated)`, so accumulation can only ever help.

| Setting | What it does |
|---|---|
| `Sound Accumulation Rate` | Confidence built per second from repeated sounds (0.5) |
| `Sound Accumulation Hold Time` | Seconds of silence tolerated before accumulated confidence starts decaying (1.0) |
| `Sound Accumulation Decay Rate` | Decay per second after hold expires (0.2) |
| `Wall Absorption Coeff` | Occlusion penalty exponent (0.4) |

Accumulation is tracked **per source actor**. Sounds emitted with `Emit Sound At Location` have no source actor and therefore do not accumulate — they are evaluated as instant signals only.

!!! warning "Two settings in this section do nothing in v3.0"
    `Hearing Base Threshold` and `b Sound Event Only Mode` are not read by any code path. Hearing is *always* event-only, and there is no noise floor. Use `Suspect Threshold` and the sound filter's `Min Alert Level` to control sensitivity instead.

### Sourceless sounds become beliefs about places

`Emit Sound At Location` has no source actor, so it is not evidence about any particular target and the hearing sense never scores it against one. Instead it becomes a **place belief** with its own lifecycle:

- confidence is the sound's loudness clamped to 1, with no distance or wall attenuation beyond the sound system's range cull,
- the belief's tag is the asset's `Sound Name`,
- `Location Accuracy Override` sets how tight the resulting uncertainty radius is, defaulting to 0.4,
- repeated sounds in the same spot merge into one belief rather than stacking.

Read it with **On Location Belief Changed** or **Get Strongest Location Belief**. `On AI Hear` does **not** fire for these sounds, because there is no target to fire it about. See [Core Concepts](core-concepts.md#11-beliefs-about-places).

### Sound filter profile

Attach a **Sound Filter Profile** data asset to `Detection → Sound Filter` to give an archetype specific ears:

- `Accepted Categories` — an AI that ignores `Animal` sounds but reacts to `Enemy` ones
- `Min Alert Level` — set to `Loud` and the AI only reacts to gunshots and above
- `Loudness Multiplier` — 2.0 for a dog, 0.5 for an old man
- `b Filter Friendly Team` — ignore your own squad's footsteps

### Loss behaviour

Grace 3.0 s, no direct cut, decay ×1.0, loss reason `SoundFaded`. Sound lingers, and confidence steps down gradually rather than cutting.

---

## Smell

**Automatic while in range.** Also the reference example for writing your own sense — the source is heavily commented for that reason.

### The confidence formula

```
Confidence = max(instant, accumulated)

instant = (BaseScentIntensity / ScentThreshold)
        × (1 − dist / SmellMaxRange)          linear falloff — scent disperses slowly
        × WindFactor
        × exp(−WallAbsorptionCoeff × wallCount)
        × WeatherMod
        × EnvironmentSmellMultiplier
```

`WindFactor = Lerp(0.1, DownwindBonus, (dot + 1) / 2)`, where `dot` compares the wind direction against the target→observer direction.

**The upwind penalty is the important half.** Standing directly upwind of a dog drops its scent signal to **0.1×** — a 10× penalty, not merely "no bonus". Perfect downwind gives the full `Downwind Bonus` (2.0). That asymmetry is what makes wind direction a real mechanic rather than a modifier.

`EnvironmentSmellMultiplier` comes from the subsystem: **1.2× indoors**, and falling from 1.0× to 0.25× as wind *speed* climbs to 800 cm/s.

Note the base term: with the defaults (`BaseScentIntensity` 1.0 / `ScentThreshold` 0.4) the formula starts at **2.5×**, so scent saturates at full confidence well before the target reaches point-blank range. Lowering `Scent Threshold` makes the sense *more* sensitive.

Smell is **unaffected by light** — it works in total darkness — and produces deliberately poor location accuracy (0.15–0.4), so the AI knows roughly where a scent comes from, never exactly.

### Tuning

Range and accumulation come from the profile when set (`Smell Max Range` 400, `Smell Accumulation Rate` 0.1, `Smell Decay Rate` 0.05), falling back to the sense's own values. The rest live only on the sense class — subclass it in Blueprint to change them:

| Property | Default | Meaning |
|---|---|---|
| `Max Smell Range` | 400 | Fallback range when the profile's is 0 |
| `Wind Direction` | zero | World direction the wind blows **from**. Zero disables the wind factor entirely (returns 1.0). |
| `Downwind Bonus` | 2.0 | Multiplier at perfect downwind |
| `Base Scent Intensity` | 1.0 | How strongly targets smell. Raise for animals, sewage, explosives. |
| `Scent Threshold` | 0.4 | Divisor on intensity — **lower is more sensitive** |
| `Wall Absorption Coeff` | 0.25 | Per-wall exponent. Lower than hearing, since scent seeps under doors. |

!!! warning "`Set Wind State` on the subsystem does not drive the directional wind bonus"
    It sets wind *speed*, which dampens scent globally through the environment multiplier. The direction used for the upwind and downwind calculation is the `Wind Direction` property on the **sense instance**. There is no Blueprint path to a live sense instance, so in practice you set it as a class default on a Blueprint subclass of `SenseUnit_Smell`. Runtime wind direction needs a small C++ addition.

### Scent tags

The `On AI Smell` event returns a `Scent Tag`. It is taken from the **first actor tag on the target that starts with `Scent.`** — so tag your player `Scent.Human`, a deer `Scent.Prey`, a corpse `Scent.Blood`, and branch on it.

### Loss behaviour

Grace **20 s**, no direct cut, decay ×0.3, loss reason `ScentLost`. Scent persists long after the target has gone.

---

## Touch

Physical contact. Instant, maximum-certainty detection at zero range.

### Getting contacts in

**The easy way** — profile → **Senses | Touch** → `b Auto Wire Touch Events` (**on by default**). APS hooks the owner's collision hits and overlaps automatically. Turn on `b Auto Wire Overlap As Grab` to treat overlaps as persistent contact.

**The manual way** — call these from your own collision events:

| Node | Call from |
|---|---|
| **Report Touch Contact** (`Instigator`, `Type`, `Strength`, `b Persistent`, `Contact Location`) | `OnComponentBeginOverlap` / `OnActorHit` |
| **Report Touch Contact With Impulse** (`Instigator`, `Type`, `Impulse`) | physics `OnComponentHit` — maps impulse magnitude to strength automatically |
| **End Touch Contact** (`Instigator`) | `OnComponentEndOverlap`, to end a persistent contact |

### Contact types and priority

`Explosion` > `Grab` > `Collision` > `Bump`. When several contacts land in one tick, the highest priority sets the confidence.

### Persistent contacts

A one-shot hit is a spike. A **persistent** contact (a grab, an ongoing overlap) holds and accumulates:

```
Confidence = Strength + min(Duration × PersistentAccumulationRate, MaxPersistentBonus)

Strength = reported strength × ContactTypeStrengthMultiplier[type]
         (or |Impulse| / TouchMaxImpulseForFullStrength when reported with an impulse)
```

| Setting | Default | Meaning |
|---|---|---|
| `Touch Max Impulse For Full Strength` | 1000 | Physics impulse that maps to strength 1.0 |
| `Touch Persistent Accumulation Rate` | 0.3 | Confidence gained per second while held |
| `Touch Max Persistent Bonus` | 0.5 | Cap on that bonus |

These three profile values overwrite the equivalents on the sense class each tick, so the profile wins over a Blueprint subclass for them. `Contact Type Strength Multiplier` lives only on the sense — subclass it to change per-type weighting.

Touch reports `Location Accuracy` of 1.0 — contact is the only sense that knows exactly where the target is.

!!! warning "`Touch Confidence` in the profile does nothing in v3.0"
    It is not read anywhere. Strength comes from the report call and the per-type multiplier instead.

### Loss behaviour

Grace 0.5 s, no direct cut, decay ×2.0, loss reason `SensorDropout`.

---

## Vibration

Ground-transmitted movement detection. **Passes through walls. No line of sight needed.** The primary sense for zombies, burrowing creatures, blind bosses and anything that hunts by feel.

### How it works

Any target moving faster than `Vibration Min Speed` (default 10 cm/s) within `Vibration Detect Range` (default 800 cm) produces a signal. There is no occlusion test at all.

```
polling:  Confidence = (1 − dist / VibrationDetectRange) × clamp(speed / 600, 0, 1)
events:   Confidence = Strength × (1 − dist / VibrationDetectRange)
```

The `speed / 600` term is the design lever: a target at 150 cm/s produces only a quarter of the signal of one at 600 cm/s, regardless of distance. **Walking versus sprinting matters more than proximity.**

!!! warning "Raising `Vibration Detect Range` above 800 needs a matching range elsewhere"
    Candidate targets are gathered within the largest of `Vision Max Range`, `Hearing Max Range` and each sense's declared maximum, and Vibration declares a fixed 800 cm for that purpose regardless of the profile value. If you set `Vibration Detect Range` to 1500 on an AI whose vision and hearing are both shorter than that, targets beyond 800 cm never reach the sense. Raise `Hearing Max Range` to cover it.

### Surface detection

The reported surface comes from the target's **actor tags**: `Surface.Metal`, `Surface.Water` or `Surface.Ground`. Tag your characters (or re-tag them from your footstep logic as they move between materials) and the `On AI Sense Vibration` event tells you what they are walking on.

### Explicit events

For vibration **not** caused by a moving actor — a grenade, a collapsing wall, a vehicle impact — call **Report Vibration Event** (`Location`, `Strength`, `Surface`). These carry their own surface value directly.

### Stimulus bus

Vibration also listens on the stimulus bus for `Stimulus.Vibration.*` **and** `Stimulus.Sound.Explosion` — explosions shake the ground, so a vibration-only creature still feels a distant blast. See [Custom Senses](custom-senses.md) for the bus.

### Loss behaviour

Grace **0.0 s**, no direct cut, decay ×5.0, loss reason `SensorDropout`. Stop moving and the signal is gone instantly — stand still and a vibration-hunter loses you.

---

## Damage

A passive broadcaster. Add it and **every** UE5 damage path — `ApplyDamage`, `ApplyPointDamage`, `ApplyRadialDamage` — is wired up automatically. No setup.

### Two modes

`Ranges → b Auto Confidence From Damage`:

- **True (default)** — confidence toward the instigator is set to `clamp(DamageAmount / 100, 0, 1)`. **100 points of damage in one hit means instant full detection.** Multiple hits from the same instigator within one tick accumulate before that division. Scale to your game's damage numbers: if your rifle does 25 damage, one shot buys 0.25 confidence — enough to cross `Suspect` but not `Detect`.
- **False** — damage fires the **On AI Damaged** event only, and *you* decide. Call `Set Target Confidence` with your own value, or ignore it entirely for an AI that can be shot without ever locating you.

Reported hits carry a `Location Accuracy` of 0.95 — the AI knows almost exactly where the hit came from.

### The On AI Damaged event

Fires on every damage event with `Instigator`, `Amount`, `Damage Type Tag` (derived from the `UDamageType` class name — `Fire`, `Explosion`, …) and `Hit Location`. Typical wiring:

```
On AI Damaged
  ├─► Report Pain From Definition (DA_Pain_Bleeding, Amount / 100)
  └─► Set Target Confidence (Instigator, 0.9)
```

Damage instigators are always included in the target list **regardless of range** — a sniper 200 m away still becomes a tracked target the moment they land a hit.

### Loss behaviour

Grace **8.0 s**, no direct cut, decay ×0.5, loss reason `OutOfRange`. An AI remembers being hit for a long time.

---

## Pain / Health

**Pain is not health.** It is a perception *impairment* that you trigger. Flashbang a guard and it should be temporarily near-blind; set it on fire and it should be too distracted to hear well.

This sense is **owner-internal** — it evaluates the AI itself, not targets, and runs once per tick rather than once per target.

### Pain type data assets

Create one **Pain Type Definition** asset per kind of pain (`DA_Pain_Burning`, `DA_Pain_Bleeding`, `DA_Pain_Stunned`, `DA_Pain_Deafened`).

| Field | Meaning |
|---|---|
| `Display Name` | Shown in the debug overlay |
| `Debug Color` | Overlay colour |
| `Decay Rate` | Level lost per second. `0.05` bleeding lingers, `0.2` burning fades, `1.0` stun wears off fast, `0` never decays (manual clear only) |
| `Sense Effects` | Array of *sense class → effect [0–1]*. At full pain, effect `1.0` drops that sense to its floor. |
| `Max Level` | Cap for this pain type |
| `Amount Override` | If > 0, every report adds this fixed amount instead of the caller's value — useful for binary pain types |

Example — `DA_Pain_Flashbang`: Decay Rate `0.8`, Sense Effects `[Vision Sense → 1.0, Hearing Sense → 0.7]`.

### Using it

| Node | Purpose |
|---|---|
| **Report Pain From Definition** (`Pain Def`, `Pain Amount`) | Add pain. Always fires **On AI Pain Reported**. |
| **Get Pain Level From Definition** (`Pain Def`) | Current level 0–1 for one type |
| **Get Total Pain Level** | Combined level across all active types |
| **Clear Pain From Definition** (`Pain Def`) | Remove one type |
| **Clear All Pain** | Remove everything |
| **Set Pain Type Enabled From Definition** (`Pain Def`, `b Enabled`) | Turn a type on/off — e.g. an enemy immune to fire |

### How degradation is calculated

```
start:            Deg = Lerp(SenseFloor, 1.0, HealthRatio)
per pain type:    Deg = max(Deg × (1 − PainLevel × Effect), SenseFloor)
final:            SenseConfidence ×= clamp(Deg, SenseFloor, 1.0)
```

`SenseFloor` is `Pain Vision Floor` for the Vision sense (and any Blueprint subclass of it) and **0 for every other sense**.

Two consequences:

- **Health degrades every sense, not just vision.** At 50% health a non-vision sense is already at 0.5× — halved — because its floor is 0. If you do not want that, keep `Health Ratio` at 1.
- **Pain types stack multiplicatively.** Burning at 0.5 with effect 0.4, plus smoke at 0.8 with effect 0.9, compounds rather than adding.

When pain suppresses a sense to effectively zero, APS clears that sense's active flag, so the memory system correctly starts its loss timer. A blinded AI genuinely *loses* you rather than freezing on a stale detection.

**`Get Total Pain Level` sums** the levels of all enabled types and clamps to 1 — two types at 0.6 each report 1.0, not 0.6.

Only **one** `On AI Pain Reported` event fires per perception tick. If you report several pain types in the same frame, the first one is broadcast and the rest are applied silently. Poll `Get Pain Level From Definition` if you need per-type reactions.

### Automatic health detection

Every tick, the Pain sense asks the owning actor how hurt it is and reads the ratio automatically. It looks, in order, for:

1. an **APS Health Provider** interface on the actor, then on any of its components ([Adapters](adapters.md)),
2. a function named `GetHealthPercent` returning a number,
3. `GetHealth` **and** `GetMaxHealth`,
4. `GetCurrentHealth` **and** `GetMaxHealth`.

A percentage above 1 is treated as 0 to 100. If your health component exposes any of these, and most do, **health-based sense degradation works with zero setup**. You do not need to call `Set Health Ratio` at all.

!!! note
    `Set Health Ratio` is overwritten each tick whenever something answers. For manual control, implement the interface and return the value you want, or make sure nothing on the AI exposes one of those function names.

The legacy query API — **Get Health Ratio** and **Get Pain State** (`Healthy` >0.75 · `Wounded` >0.40 · `Critical` >0.15 · `Near Death`) — reads the same value, and works as a cheap Behavior Tree condition for "retreat when Critical".

---

## Echolocation

Pulse-based detection. **No line of sight required** — sonar bounces around geometry. For bats, aliens, blind bosses, cave creatures and sonar robots.

### How it works

The AI emits a sphere pulse every `Sense Interval` (default 0.3 s). Any Pawn within `Echo Range` (default 1500 cm) returns it. No occlusion test.

```
Confidence       = (1 − dist / EchoRange)²
LocationAccuracy = (1 − dist / EchoRange) × 0.85
```

Quadratic falloff means echolocation is precise up close and drops off hard — at half range confidence is only 0.25.

`Detection → b Echo Directional` restricts the pulse forward, but loosely: it rejects targets more than about **101°** off the AI's facing, not a strict 90° hemisphere. It also uses the actor's rotation rather than the resolved eye facing, so head-socket settings do not move the pulse.

!!! warning "Same gather-range caveat as Vibration"
    The sense declares 2000 cm for target gathering. Setting `Echo Range` beyond that needs another sense with a longer range on the same profile, or targets past 2000 cm are never evaluated.

Echolocation fires **On AI See** — from the AI's point of view it *is* sight. Bind it exactly as you would vision.

### Loss behaviour

Grace 0.6 s, **direct cut**, decay ×2.0, loss reason `OutOfRange`.

---

## Which senses for which archetype

| Archetype | Senses | Key weights |
|---|---|---|
| Stealth guard | Vision, Hearing | Vision 1.0, Hearing 1.0 |
| Guard dog | Smell, Hearing, Vision | Smell 1.5, Hearing 1.2, Vision 0.6 |
| Zombie | Hearing, Vibration, Vision, Touch | Hearing 1.4, Vibration 1.3, Vision 0.4 |
| Blind creature | Echolocation, Hearing, Vibration | Echo 1.2, Hearing 1.0, Vibration 1.0 |
| Turret / camera | Vision, Damage | Vision 1.0 |
| Soldier | Vision, Hearing, Damage, Pain | Vision 1.0, Hearing 1.0 |
| Boss | Vision, Hearing, Damage, Pain, Touch | tuned per fight |

Full copy-paste settings for each are in the [Archetype Cookbook](archetype-cookbook.md).

---

