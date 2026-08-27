# How-To Guides

**For:** developers who know roughly what they want and need the specific steps.
**Assumes:** you've done [Install & Your First AI](getting-started.md).

Each recipe is self-contained. Skim the headings, take what you need.

---

## Detection

### Make the AI hear footsteps

1. Content Browser → **Data Asset → SoundTypeDefinition** → `DA_Sound_Footstep`.
   Set `Base Loudness` 1.0, `Max Range` 800, `Max LOD Tier` 1.
2. In your player's walk/run animation, add an anim notify called `Footstep`.
3. In the player Blueprint:
   ```
   Event AnimNotify_Footstep
     └─► Emit Sound (World Context: Self, Source: Self, Sound Type: DA_Sound_Footstep)
   ```
4. Confirm `Hearing Sense` is in the profile's `Sense Classes`.

**Why:** APS never infers sound from velocity. Nothing is audible until you emit it — which means your AI hears exactly what your game decides is audible, and nothing else.

---

### Make sprinting louder than walking

Create a second asset `DA_Sound_Sprint` (`Base Loudness` 1.8, `Max Range` 1600, `Alert Level` Loud), then branch in the same notify:

```
Event AnimNotify_Footstep
  └─► Get Velocity → Vector Length → Branch: > 450
        True  → Emit Sound (DA_Sound_Sprint)
        False → Emit Sound (DA_Sound_Footstep)
```

Add `DA_Sound_Crouch_Step` (`Loudness` 0.3, `Range` 300, `Alert Level` Whisper) on the crouched branch and you have a three-tier movement stealth system.

---

### Stop the AI seeing through doors, vehicles and other pawns

1. Profile → **Detection | Occlusion → `Vision Occlusion Channels`** → add the channel your doors and vehicles block. Empty means `Visibility` only.
2. For bodies blocking sight, tick **`b Pawns Block Sight`**.
3. Verify the geometry actually blocks that channel in its collision settings.

**Why:** Epic tests exactly one channel, which is why AI routinely see through props set to a custom channel. Each extra channel costs one more trace per sample point, so add only what you need.

---

### Make foliage and smoke partly conceal instead of fully hiding

Profile → **Detection | Occlusion → `Surface Vision Transmission`** → add entries:

| Physical surface | Value |
|---|---|
| `SurfaceType_Glass` | 1.0 |
| `SurfaceType_Foliage` | 0.4 |
| `SurfaceType_Smoke` | 0.15 |

**Why:** the value is the fraction of vision that *passes through*. Anything not listed blocks completely, so an empty map behaves exactly like normal occlusion. Transmission multiplies into the exposure ratio, so a player in tall grass produces genuine partial confidence.

---

### Make crouching actually hide the player

1. Player → **APS Target Component** → leave `b Auto Detect Stance` ticked.
2. Profile → **Detection | Visibility** → `Min Visible Points Crouched` = **2**, `Min Visible Points Prone` = **3**.

**Why:** all three default to 1, so adding the component never silently makes a character harder to see. Raising the crouched requirement means a crouched target behind cover must expose two sample points before it registers at all — the *Splinter Cell* rule.

---

### Make the AI's vision follow its head

Profile → **Detection | Eyes**:

| Setting | Value |
|---|---|
| `b Use Eye Socket` | ✅ |
| `Eye Socket Name` | `head` |
| `Eye Direction Mode` | `Socket Rotation` |
| `Eye Socket Alignment` | `Automatic` |
| `Eye Turn Rate Deg Per Sec` | `200` |

**Why:** `Automatic` reads the skeleton's reference pose and cancels the bone's rest orientation, so a raw bone name works on any rig with no hand-dialled offsets. The turn rate stops the cone snapping to a `MoveTo` target before the body has physically turned.

---

### Make a dark corner genuinely dark

1. Level Blueprint → `Event Begin Play` → **Get APS Subsystem** → **Set Sun Direction** (your directional light → `Get Forward Vector`).
2. Profile → **Detection | Light** → `b Use Per Target Light` ✅, `b Trace Sun Shadow` ✅, `Shadow Light Level` 0.25.
3. Optional, for exact control: set `Light Level Override` on the player's APS Target Component from your own light-gem system.

**Why:** global ambient only models day and night. The per-target path traces from the target toward the sun and applies the shadow level when that trace is blocked.

⚠ `Light Level Override` is only read when `b Use Per Target Light` is on.

---

## Fairness

### Give the player a beat to duck back out of sight

Profile → **Fairness → `First Spot Reaction Time`** = `0.4`.

**Why:** on first acquisition of a target, confidence does not start accumulating until the AI has held it for this long. It is reaction time. Note it applies only until that target has been detected once — afterwards re-acquisition is instant, which is correct.

---

### Warn the player before the AI commits

1. Profile → **Fairness → `Telegraph Threshold`** = `0.22` (between Suspect and Detect).
2. In the AI Blueprint:
   ```
   Event On AI Telegraph (Target, Confidence)
     ├─► Play Sound ("Hmm?")
     ├─► Set Focus (Target)          // head turns toward the player
     └─► show a detection pip on the HUD
   ```

**Why:** this is the highest-value fairness feature in the plugin. It converts *"the AI spotted me out of nowhere"* into *"I saw it start to notice me and I chose wrong."* It fires once per target and re-arms only when that target falls back to Undetected.

---

### Give the player a guaranteed safe room

1. Safe room volume → `Event Begin Play`:
   ```
   Get APS Subsystem → Register Never Search Zone (Center: Get Actor Location, Radius: 600)
   ```
2. **Then honour it — this part is required:**
   ```
   Event On AI Lost (Target, Last Known, …)
     └─► Is Location In Never Search Zone (Last Known)
           True  → do NOT set the search keys. Give up, return to patrol.
           False → search normally
   ```
3. Add the same check to any BT task that picks a search point.

⚠ **Zones are advisory.** Registering one does not stop anything by itself — the plugin gives you the query, your BT does the honouring.

---

## Search behaviour

### Investigate a noise without abandoning a chase

```
Event On AI Hear (Location, Loudness, Sound Type Name)
  └─► Branch: Blackboard "bHasTarget" == false
        True → Set Blackboard Vector "InvestigateLocation" = Location
```

**Why:** without the guard, a distant footstep interrupts an active pursuit every time it fires.

---

### Search the exact corner the player hid behind

```
Event On AI Lost (Target, Last Known, Predicted, Last Cover Actor)
  └─► Blackboard
        ├─ Set Vector "LastKnownPosition"  = Last Known
        ├─ Set Object "LastCoverActor"     = Last Cover Actor
        ├─ Set Enum   "LossReason"         = Get Loss Reason (Target)
        ├─ Set Vector "LossDirection"      = Get Loss Direction (Target)
        └─ Set Float  "SearchRadius"       = Get Uncertainty Radius (Target)
```

Then branch the BT on `LossReason` — see the table in [Cheat Sheet](cheat-sheet.md) or the full tree in [Behavior Trees](behavior-trees.md).

**Why:** `Last Cover Actor` is the actual object the AI traced against when it lost you. Sending the AI to flank *that object* rather than a generic point is the single biggest perceived-intelligence win available.

---

### Widen the search the longer the player stays hidden

```
BT Task: Search Step
  └─► Get Random Reachable Point In Radius
        Origin = Blackboard "LastKnownPosition"
        Radius = Blackboard "SearchRadius"
  └─► MoveTo → Look Around (1s)
```

Loop it 3–4 times. With EQS, expose `SearchRadius` as the generator radius instead.

**Why:** `Uncertainty Radius` grows at `Uncertainty Growth Rate` cm/s while the target is lost, up to `Max Uncertainty Radius`, and grows up to 3× faster if the target was sprinting. The search naturally spirals outward without any timer logic of your own.

---

### Make the AI search longer before giving up

Profile → **Memory → `Min Time In Lost`** = `8.0` (or `25.0` for a horror stalker).

**Why:** the target cannot move from `Lost` to `Remembered` until it has spent this long in `Lost`, no matter how far confidence has decayed. This is the "how stubborn is this AI" dial.

---

## Reactions & UI

### Show a detection meter on the HUD

**Single player:**
```
Widget Tick (or a 0.1s timer)
  └─► APS Core → Smoothed Confidence  →  Progress Bar Percent
```

Or for a specific target: `Get Belief Data (Player)` → break → `Smoothed Confidence`.

**Multiplayer:** see the next recipe — perception does not run on clients.

---

### Show a detection meter in multiplayer

1. Profile → **Replication** → `b Replicate Perception State` ✅, `Max Replicated Targets` 1, `Replication Interval` 0.25.
2. On the client:
   ```
   Event On Replicated State Changed
     └─► Get Replicated Perception State
           → Out Targets (array) → find yours → Confidence → update widget
   ```

**Why:** perception is server-authoritative and skipped entirely on clients. `Get Replicated Perception State` resolves the relay automatically, so it works whether the component sits on the Pawn or the AIController.

---

### React differently to seeing vs hearing

```
Event On AI Detect (Target, Threat Level, Stimulus)
  └─► Switch on EStimulusSource (Stimulus)
        ├─ Vision      → engage immediately
        ├─ Hearing     → move to investigate, weapon lowered
        ├─ Damage      → take cover first, then look
        └─ SharedIntel → approach cautiously, don't fire yet
```

Or for finer detail, `Get Sense Contributions (Target)` returns a map of `Vision → 0.7, Hearing → 0.3`.

---

### React to being shot from an unknown direction

```
Event On AI Damaged (Instigator, Amount, Damage Type Tag, Hit Location)
  ├─► Play flinch montage
  ├─► Set Blackboard Vector "InvestigateLocation" = Hit Location
  └─► Report Pain From Definition (DA_Pain_Bleeding, Amount / 200)
```

For hardcore stealth, set `b Auto Confidence From Damage` to **false** first, so a silenced hit hurts without revealing the shooter — then `Set Target Confidence` yourself only for loud weapons.

---

## Squads

### Make one AI alert the others

1. Both AI: `Event Begin Play → Set Squad ID ("Patrol_A")`.
2. Profile → **Brain | Squad** → `b Auto Share On Detect` ✅, `Squad Share Range` 3000.

**Why:** auto-share on Detect is horde behaviour — one zombie sees you, the pack converges.

---

### Make a squad converge without becoming telepathic

1. Profile → set **both** `b Auto Share On Detect` and `b Auto Share On Track` to **false**.
2. Share only after a visible call-out:
   ```
   Event On AI Detect
     └─► Play "Contact!" montage
           └─► (montage notify) → Share Target With Squad (Target)
   ```
3. On the receiving side, branch on `Stimulus == Shared Intel` and approach cautiously.

**Why:** without step 3 a squad becomes telepathic — one guard spots you and four others headshot you through a wall. The branch is what makes them feel coordinated instead of psychic.

---

### Divide up combat roles automatically

```
Event On AI Detect
  └─► Request Combat Role (Flanker)
        True  → Blackboard "Role" = Flanker
        False → Request Combat Role (Suppressor)
                  True  → Blackboard "Role" = Suppressor
                  False → Blackboard "Role" = Approacher

Event On AI Forget
  └─► Release Combat Role
```

**Why:** roles are exclusive per squad, so four guards spotting you naturally produce one flanker, one suppressor and two approachers — with no manager actor. Restrict what an archetype may claim with the profile's `Eligible Roles`.

---

## Creature archetypes

### Build a guard dog that tracks by scent

1. Profile `Sense Classes`: **Smell, Hearing, Vision**.
2. `Sense Weights`: Smell `1.5`, Hearing `1.3`, Vision `0.5`.
3. `Smell Max Range` 1400, `Smell Accumulation Rate` 0.25, `Smell Decay Rate` 0.03.
4. `Smell Loss → Grace Time` 30.
5. Tag your player with the actor tag `Scent.Human` so `On AI Smell` reports it.

**Wind:** create a Blueprint subclass of `SenseUnit_Smell`, set `Wind Direction` and `Downwind Bonus` 2.5 in its Class Defaults, and put *that* class in `Sense Classes`.

⚠ `Set Wind State` on the subsystem controls wind *speed* only — the directional bonus reads the sense's own `Wind Direction` property.

**Why:** standing upwind drops the scent signal to **0.1×**, a 10× penalty. That asymmetry is what makes wind a real mechanic rather than a modifier.

---

### Build a creature that hunts by ground vibration

1. `Sense Classes`: **Hearing, Vibration, Vision, Touch**.
2. `Vibration Detect Range` 1200, `Vibration Min Speed` **150**.
3. `Hearing Max Range` 2500 — needed so distant targets are gathered at all.
4. Tag surfaces on the player with `Surface.Metal` / `Surface.Water` / `Surface.Ground` to drive `On AI Sense Vibration`.

**Why:** `Vibration Min Speed` at 150 *is* the stealth mechanic — walk and it feels you, crouch-walk and it does not. Vibration passes through walls and ignores light entirely.

⚠ Vibration declares a fixed 800 cm gather range, so another sense on the profile must reach far enough to pull distant targets into evaluation.

---

### Build a blind creature (echolocation)

1. `Sense Classes`: **Echolocation, Hearing, Vibration** — no Vision at all.
2. `Echo Range` 2200, `b Echo Directional` ✅.
3. `Sense Intervals` → Echolocation `0.4`.
4. `Hearing Max Range` 3000 (gather range, as above).

**Why:** with no Vision sense, light is irrelevant — the room can be pitch black. The player mechanic is *stand still*: vibration drops instantly and echolocation alone accumulates too slowly. The slow pulse interval gives readable windows between pings.

---

## Advanced

### Blind an AI with a flashbang

1. **Data Asset → PainTypeDefinition** → `DA_Pain_Flashbang`.
   `Decay Rate` 0.8, `Amount Override` 1.0, `Sense Effects`: `Vision Sense → 1.0`, `Hearing Sense → 0.7`.
2. On the grenade:
   ```
   Sphere Overlap Actors (radius 800)
     └─► ForEach → Get Component By Class (APS Core)
           └─► Branch: Line Trace clear to grenade?
                 True → Report Pain From Definition (DA_Pain_Flashbang, 1.0)
   ```

**Why:** guards behind cover are unaffected; guards looking at it are blind for about a second. No special-case AI code — the perception system simply stops feeding them vision, and because the sense goes inactive the memory system correctly starts its loss timer.

---

### Hot-swap perception for an alert state

```
Alarm triggered
  └─► ForEach guard → Set Profile (DA_Profile_Guard_Alerted)
```

`DA_Profile_Guard_Alerted` = a copy with longer ranges, lower thresholds, wider cones.

⚠ `Set Profile` rebuilds senses and **resets the ledger, emotions and attention**. Don't call it every tick, and avoid swapping mid-engagement — gate it on `Has Any Detection == false` if that matters.

---

### Add a custom sense (thermal)

1. **Blueprint Class → All Classes → `SenseUnit`** → `BP_Sense_Thermal`.
2. Override **Get Sense ID** → return `"Thermal"`.
3. Override **Evaluate**:
   ```
   Distance = Vector Distance (Context.Owner Location, Target Location)
   Branch: Distance > 3000 → return
   Confidence = (1 - Distance / 3000) × HeatValue
   Set Out Result: b Is Active = Confidence > 0.1
                   Confidence, Estimated Location = Target Location
                   Location Accuracy = 0.8, Sense ID = "Thermal"
   ```
4. Add `BP_Sense_Thermal` to the profile's `Sense Classes`.

It now fuses with every other sense, drives the lifecycle, feeds threat, and appears in the debug overlay. Full detail and the C++ limits are in [Custom Senses](custom-senses.md).

---

### Tune difficulty without changing what the AI can see

Make one profile per difficulty and swap on Begin Play. Vary only:

| Setting | Easy | Normal | Hard |
|---|---|---|---|
| Suspect / Detect / Track | 0.25 / 0.50 / 0.75 | 0.15 / 0.35 / 0.60 | 0.10 / 0.25 / 0.45 |
| Confidence Rise Rate | 3.0 | 5.0 | 7.0 |
| First Spot Reaction Time | 0.8 | 0.4 | 0.1 |
| Min Time In Lost | 3.0 | 8.0 | 15.0 |

**Why:** leave cone angles, ranges and occlusion identical. The player builds a mental model of what a guard can see; changing that between difficulties feels arbitrary. Changing how *fast* it acts on what it sees feels fair.

---

### Perceive something that isn't a Pawn

```
Turret / vehicle / prop, Event Begin Play
  └─► Get APS Subsystem → Register Perceivable Actor (Self)

Event End Play
  └─► Get APS Subsystem → Unregister Perceivable Actor (Self)
```

Or just add an **APS Target Component** with `b Auto Register As Perceivable` ticked — it does both for you.

**Why:** all Pawns are candidates automatically. Non-Pawn actors need registering.

---

