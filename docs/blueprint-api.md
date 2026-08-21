# Blueprint API

Every node APS adds, grouped the way it appears in the right-click menu. Nodes marked **⚡** are pure (no execution pin — just drag the return value).

Unless stated otherwise, these are called **on the Perception Core component**. Get a reference with `Get Component By Class → Perception Core`, or drag from the component in the My Blueprint panel.

---

## APS | Attention

The target the AI is **committed to**. This is what your Behavior Tree should use.

| Node | Returns | Description |
|---|---|---|
| **Get Attention Target** ⚡ | `Actor` | The target the AI is focused on. Persists through `Attention Stickiness Time` even if a slightly better target appears. Null when nothing is tracked. |
| **Get Attention Duration** ⚡ | `float` | Seconds focused on the current attention target. *"Have I been chasing this for over 10 s?"* |
| **Force Attention Target** (`New Target`) | — | Immediately switch focus, bypassing stickiness. Use when the player shoots this AI or trips a scripted trigger. Allocates a belief record if none exists. |

---

## APS | Query

| Node | Returns | Description |
|---|---|---|
| **Get Top Target** ⚡ | `Actor` | Highest-scoring target **this tick**. Can flicker — prefer `Get Attention Target` for behaviour. |
| **Get Top Target Belief** ⚡ | `bool` + `Belief Record` | Full belief data for the top target |
| **Get Belief Data** (`Target`) ⚡ | `bool` + `Belief Record` | Full belief data for a specific actor. The single most useful query in the plugin — see the struct breakdown below. |
| **Get Targets Sorted By Score** | `array<Belief Record>` | Every active target, best first. Use for multi-target logic and threat displays. |
| **Get Awareness Level** ⚡ | `EAwarenessLevel` | The AI's overall awareness across all targets |
| **Get Awareness Level For Target** (`Target`) ⚡ | `EAwarenessLevel` | Awareness relative to one actor |
| **Get Active Target Count** ⚡ | `int` | How many targets the AI is currently aware of |
| **Has Any Detection** ⚡ | `bool` | Quick "is this AI aware of anything at all?" |
| **Get Sense Contributions** (`Target`) | `bool` + `map<Name, float>` | Per-sense confidence breakdown — `Vision → 0.7`, `Hearing → 0.3`. Perfect for debug UI and for "did it *see* me or only *hear* me?" logic. |

### The Belief Record struct

`Get Belief Data` returns this. Break it to read everything the AI believes about one target.

| Field | Type | Meaning |
|---|---|---|
| `Target` | Actor | The actor |
| `Target ID` | int | Stable id |
| `Fused Confidence` | float | Raw fused value this tick |
| `Smoothed Confidence` | float | **The value that drives everything.** Use this for detection meters. |
| `Lifecycle State` | enum | Undetected → Expired |
| `Time Since Last Sensed` | float | Seconds since any sense was active |
| `Total Time Tracked` | float | Cumulative tracking time |
| `Time In Current State` | float | Seconds in the current lifecycle state |
| `Last Known Position` | Vector | Where it was when contact was lost |
| `Estimated Velocity` / `Estimated Acceleration` | Vector | Smoothed motion estimates |
| `Uncertainty Radius` | float | Search radius — grows while lost |
| `Predicted Position` | Vector | Extrapolated position (needs `b Enable Prediction`) |
| `Long Term Memory Strength` | float | Slow-decaying memory trace |
| `Detection Count` | int | How many separate times this target has been detected |
| `b Was Ever Detected` | bool | Has this target ever been confirmed |
| `First Detected Time` | float | World time of first detection |
| `Last Seen Cover Actor` | Actor | The cover object it ducked behind |
| `Last Seen Cover Position` | Vector | Where that cover was |
| `b Was In Cover` | bool | Was the target in cover at loss |
| `Loss Reason` | enum | **Why** contact was lost |
| `Loss Direction` | Vector | Which way it was heading |
| `Episodes` | array | Last 5 engagements |
| `Primary Stimulus Source` | enum | Which sense first detected it |
| `Dominant Stimulus Source` | enum | Which sense contributes most right now |
| `Threat Level` / `Threat Score` | enum / float | Assessed threat |
| `Damage Received From Target` / `Damage Dealt To Target` | float | Damage bookkeeping |
| `b Is Known Threat` | bool | Has this target ever hurt this AI |
| `Encounter Count` | int | Number of engagements |
| `Relationship` | enum | Resolved relationship |

---

## APS | Spatial

All ⚡ pure, all take a `Target`.

| Node | Returns | Use for |
|---|---|---|
| **Get Last Known Position** | `Vector` | The primary search destination |
| **Get Predicted Position** | `Vector` | Cut-off / intercept points. Needs `b Enable Prediction`. |
| **Get Uncertainty Radius** | `float` | Search radius — feed straight into EQS or `Get Random Reachable Point In Radius` |
| **Get Estimated Velocity** | `Vector` | Lead targeting, flee-direction checks |
| **Get Estimated Acceleration** | `Vector` | Detecting a sudden sprint or stop |

---

## APS | Cover

| Node | Returns | Description |
|---|---|---|
| **Get Last Seen Cover Actor** (`Target`) ⚡ | `Actor` | The actual object the target ducked behind. Send the AI to flank *that* object. |
| **Was Target In Cover** (`Target`) ⚡ | `bool` | Was the target in cover when contact was lost |

Cover is resolved by a single `Visibility` trace from the AI's eye to the target's last known position, taken at the moment of a `Detected`/`Tracked` → `Lost` transition. Whatever it hits becomes the cover actor; `Last Seen Cover Position` is that **actor's** origin, not the impact point. It uses the `Visibility` channel specifically, not the profile's `Vision Occlusion Channels`.

---

## APS | Loss

| Node | Returns | Description |
|---|---|---|
| **Get Loss Reason** (`Target`) ⚡ | `ELossReason` | Why the target was last lost. `Unknown` if never lost or currently active. **Branch your search behaviour on this.** |
| **Get Loss Direction** (`Target`) ⚡ | `Vector` | The AI's normalised velocity estimate for the target at the moment contact was lost. Written on **every** loss, not just `OutOfRange`/`ScentLost`. Zero when the target was stationary — always check `Is Nearly Zero` first. |

---

## APS | Memory

| Node | Returns | Description |
|---|---|---|
| **Get Recent Episodes** (`Target`) | `bool` + `array<Perception Episode>` | Up to 5 past engagements, oldest → newest |
| **Get Last Episode** (`Target`) ⚡ | `bool` + `Perception Episode` | *"What happened last time?"* |
| **Clear Episodes** (`Target`) | — | Wipe episode history. Use on respawn / new chapter. |

**Perception Episode fields:** `How Lost`, `State When Lost`, `Location When Lost`, `AI Camera Direction`, `Target Flee Direciton` *(sic — the field name is misspelled in v2.0)*, `Engagement Duration`, `Peak Threat Level`, `World Time Stamp`.

An episode is written whenever `Detected` **or** `Tracked` transitions to `Lost`. `Engagement Duration` records the target's *cumulative* tracked time, not the length of that single engagement, so it only ever increases across a target's episodes.

---

## APS | Brain

| Node | Returns | Description |
|---|---|---|
| **Get Emotional State** ⚡ | `Emotional State` | All five channels + dominant emotion + fear input |
| **Get Dominant Emotion** ⚡ | `EEmotionType` | `Calm / Curious / Alert / Aggressive / Fearful / Panicked` |
| **Get Threat Level** (`Target`) ⚡ | `EThreatLevel` | Threat from one target |
| **Get Highest Threat Level** ⚡ | `EThreatLevel` | Worst threat across all targets |
| **Has Threat At Or Above** (`Level`) ⚡ | `bool` | Cleanest BT decorator condition |
| **Get Relationship** (`Target`) ⚡ | `ETargetRelationship` | Resolved relationship |
| **Get Stimulus Source** (`Target`) ⚡ | `EStimulusSource` | Which sense is driving this belief |
| **Get Combat Role** ⚡ | `ECombatRole` | This AI's current squad role |
| **Set Fear Input** (`Value`) | — | External fear driver [0–1] for horror events and scripted sequences. Fear decays normally when this is 0. |
| **Set Emotion** (`Emotion`, `Value`) | — | Force one channel. The engine keeps driving channels naturally next tick, so call every tick for a sustained override — or use `Set Fear Input`. |
| **Reset Emotional State** | — | All channels to 0, dominant back to `Calm` |

---

## APS | Squad

| Node | Description |
|---|---|
| **Set Squad ID** (`New Squad ID`) | Put this AI in a squad. Call from Begin Play. Squad membership is just a matching `Name`. |
| **Share Target With Squad** (`Target`) | Push full belief data to every squadmate within `Squad Share Range` |
| **Broadcast Alert To Squad** (`Target`, `Alert Location`, `Threat Level`) | Positional alert without full belief data — *"I heard something over there"* |
| **Request Combat Role** (`Role`) → `bool` | Claim an exclusive role. Returns false if a squadmate already holds it or the archetype is not eligible. |
| **Release Combat Role** | Give the role back |

---

## APS | Input

| Node | Description |
|---|---|
| **Report Touch Contact** (`Instigator`, `Type`, `Strength`, `b Persistent`, `Contact Location`) | Feed the Touch sense from a collision or overlap |
| **Report Touch Contact With Impulse** (`Instigator`, `Type`, `Impulse`, …) | Same, but maps a physics impulse vector to strength automatically |
| **End Touch Contact** (`Instigator`) | End a persistent contact |
| **Report Vibration Event** (`Location`, `Strength`, `Surface`) | Explicit vibration — grenades, collapses, vehicle impacts. Moving actors are detected automatically without this. |
| **Set Target Confidence** (`Target`, `Confidence`) | Raise confidence directly, clamped 0–1. Your escape hatch for scripted reveals, custom damage reactions, or any bespoke detection rule. ⚠ **It only raises** — the value is `max(current, yours)`, so you cannot use it to suppress or clear a detection. Allocates a belief record if the target has none. |

---

## APS | Pain

| Node | Description |
|---|---|
| **Report Pain From Definition** (`Pain Def`, `Pain Amount`) | Add pain. Always fires `On AI Pain Reported`. |
| **Get Pain Level From Definition** (`Pain Def`) ⚡ | Current level 0–1 for one type |
| **Get Total Pain Level** ⚡ | Combined across all active types |
| **Clear Pain From Definition** (`Pain Def`) | Remove one type |
| **Clear All Pain** | Remove everything |
| **Set Pain Type Enabled From Definition** (`Pain Def`, `b Enabled`) | Toggle a type — immunities, resistances |

---

## APS | Player Model

| Node | Description |
|---|---|
| **Get Player Behavior Model** (`Target`) ⚡ | `bool` + `Player Behavior Model` — crouch/sprint/walk ratios, stealth and aggression ratios, recent hide locations, custom ratios, engagement count, `b Has Enough Data` |
| **Reset Player Behavior Model** (`Target`) | Wipe observations for one target |
| **Save Cross Session Memory** | Write models to `Saved/APS/PlayerModel/`. Called automatically on End Play. |
| **Load Cross Session Memory** | Read them back. Called automatically on Begin Play. |
| **Clear Cross Session Memory** | Delete the saved files |

---

## APS | Config & Replication

| Node | Description |
|---|---|
| **Set Profile** (`New Profile`) | Hot-swap the entire perception profile at runtime. Rebuilds senses, resets the ledger, emotions and attention. Use for alert states, difficulty changes, or transformations. |
| **Get Replicated Perception State** → `array<Replicated Target State>`, `EAwareness Level` | Read the replicated summary on clients. Always use this rather than the raw array — it resolves the relay automatically. See [Multiplayer](multiplayer.md). |

---

## APS | Fairness

| Node | Description |
|---|---|
| **Is Location In Never Search Zone** (`Location`) ⚡ | True if the location is inside a designer-flagged safe zone |

---

## APS | Debug

Compiled out of Shipping builds.

| Node | Description |
|---|---|
| **Debug Print Belief State** | Dump the full ledger to the log |
| **Debug Toggle Pause** | Freeze perception evaluation (memory still decays) |
| **Debug Toggle Freeze Snapshot** | Freeze the on-screen overlay |
| **Debug Cycle Display Mode** | Step through the 7 debug modes |
| **Debug Reset Damage Tracking** | Clear damage bookkeeping |

---

## Component properties

Readable and settable directly on the component.

| Property | Type | Notes |
|---|---|---|
| `Profile` | Perception Profile | Editable in the Details panel; use **Set Profile** at runtime |
| `Debug Settings` | struct | See [Debugging](debugging.md) |
| `Smoothed Confidence` | float (read-only) | Top target's smoothed confidence — the easy hook for a detection meter |
| `Current State` | String (read-only) | Human-readable state string |
| `Replicated Targets` | array (read-only) | Raw replicated array — prefer `Get Replicated Perception State` |
| `Replicated Awareness` | enum (read-only) | Replicated awareness level |

---

# Global nodes — no component needed

## Sound (`Perception | Sound`)

| Node | Description |
|---|---|
| **Emit Sound** (`Source`, `Sound Type`) | Emit a sound from an actor. Only agents within the sound type's `Max Range` are notified. |
| **Emit Sound At Location** (`Sound Location`, `Sound Type`) | Emit from a world position with no source actor |

## APS Subsystem

Get it with **Get APS Subsystem** (static, world context), then drag off the return.

### Environment

| Node | Description |
|---|---|
| **Set Ambient Light** (`Level`) | Global light level 0–1. Drive from your day/night cycle. |
| **Set Weather Modifier** (`Mod`) | Global weather visibility modifier 0–1 |
| **Set Environment State** (`New State`) | Set light, rain, wind, indoors and time of day in one call |
| **Get Environment State** ⚡ | Read the current environment struct |
| **Set Wind State** (`Direction`, `Speed`) | Wind for the Smell sense |
| **Set Indoors** (`b Indoors`) | Indoors boosts scent, since it does not disperse |
| **Set Time Of Day** (`Hour`) | 0–24 |
| **Set Sun Direction** (`Direction`) | Pass your directional light's forward vector. **Required for per-target shadow tracing.** |

### Registry

| Node | Description |
|---|---|
| **Register Perceivable Actor** (`Actor`) | Make a non-Pawn actor perceivable — turrets, vehicles, interactive props. Pawns are found automatically. |
| **Unregister Perceivable Actor** (`Actor`) | Stop it being perceivable |
| **Get Agent Count** | How many APS agents exist in the world |

### Fairness

| Node | Description |
|---|---|
| **Register Never Search Zone** (`Center`, `Radius`) | A sphere AI will never search or pursue into. Guarantees the player a safe room. |
| **Unregister Never Search Zone** (`Center`, `Tolerance`) | Remove the closest zone within tolerance |
| **Clear Never Search Zones** | Remove all of them |
| **Is In Never Search Zone** (`Location`) ⚡ | Test a location |

### Stimulus bus

| Node | Description |
|---|---|
| **Emit Stimulus** (`Event`) | Broadcast a custom stimulus to every agent that registered a matching tag prefix. See [Custom Senses](custom-senses.md). |

---

## Other component nodes

**APS Target Component**
- **Get Effective Stance** ⚡ → `EAPSStance` — the stance in effect right now, honouring `b Auto Detect Stance`

**APS Relationship**
- **Get Relationship** (`Target`) → `ETargetRelationship`
- **Set Relationship Override** (`Target`, `Relationship`) — runtime override for one actor

**Smell Sense**
- **Set Wind Direction** (`Direction`)

**Touch Sense** (if you hold a reference to the sense itself)
- **Report Contact**, **Report Contact With Impulse**, **End Touch Contact** — the Perception Core wrappers are usually easier

**Pain Sense**
- **Set Health Ratio** / **Get Health Ratio** / **Get Pain State** — legacy health-based degradation

---

