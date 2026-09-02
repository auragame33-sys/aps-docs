# Blueprint API

Every node APS adds, grouped the way it appears in the right-click menu. Nodes marked **⚡** are pure (no execution pin — just drag the return value).

Unless stated otherwise, these are called **on the APS Core component**. Get a reference with `Get Component By Class → APS Core`, or drag from the component in the My Blueprint panel.

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

**Perception Episode fields:** `How Lost`, `State When Lost`, `Location When Lost`, `AI Camera Direction`, `Target Flee Direciton` *(sic — the field name is misspelled in v3.0)*, `Engagement Duration`, `Peak Threat Level`, `World Time Stamp`.

An episode is written whenever `Detected` **or** `Tracked` transitions to `Lost`. `Engagement Duration` records the target's *cumulative* tracked time, not the length of that single engagement, so it only ever increases across a target's episodes.

---

## APS | Memory Store

A tagged store per agent. You decide what goes in and when it comes out — see **[Memory & Recall](memory-and-recall.md)**.

| Node | Returns | Description |
|---|---|---|
| **Make Actor Subject** (`Actor`) | `Memory Subject` | Something to remember *about* |
| **Make Place Subject** (`Location`, `Place Tag`) | `Memory Subject` | A place, with no actor involved |
| **Remember** (`Subject`, `Tag`, `Number`, `Place`, `Related Actor`) | — | File a tagged memory. Writing the same tag again updates it and increments `Count` |
| **Recall** (`Subject`) | `bool` + `array<Memory>` | Everything held about a subject, newest first |
| **Recall Tag** (`Subject`, `Tag`) | `bool` + `Memory` | One specific memory |
| **Has Memory Of** (`Subject`) | `bool` | Whether anything at all is held |
| **Get Remembered Subject Count** | `int` | Distinct subjects this agent holds |
| **Forget** (`Subject`, `Tag`) | `bool` | Drop one tag |
| **Forget Subject** (`Subject`) | — | Drop everything about one subject |
| **Forget Everything** | — | Wipe this agent's store |

**Memory fields:** `Tag` · `Number` · `Place` · `Related Actor` · `Count` · `Age`.
`Count` and `Age` are maintained for you and are usually what makes the behaviour interesting.

There is deliberately **no recall event**. APS never tells you when to remember something — call **Recall** where your own logic wants to know.

---

## APS | Evidence

| Node | Description |
|---|---|
| **Add Target Evidence** (`Target`, `Evidence Tag`, `Operation`, `Value`, `Lifetime`, `Source`) | Apply an external belief modifier: a floor, a ceiling, a relative reduction, or a forced zero. Re-adding the same tag replaces the entry rather than stacking. `Lifetime` 0 holds until removed. |
| **Remove Target Evidence** (`Target`, `Evidence Tag`) | Drop one modifier |
| **Clear Target Evidence** (`Target`) | Drop all of them |
| **Get Target Evidence** (`Target`) → `array<Evidence>` | What is currently applied |

See [`EAPSEvidenceOp`](enum-reference.md) for what each operation means.

---

## APS | Beliefs about places

| Node | Description |
|---|---|
| **Report Location Belief** (`Location`, `Tag`, `Confidence`, `Accuracy`) | File a belief about a place rather than an actor |
| **Get Location Beliefs** → `array<Belief Record>` | All of them |
| **Get Strongest Location Belief** | `bool` + `Belief Record` |
| **Clear Location Belief** (`Location`, `Tag`) | `bool` |

Place beliefs are kept out of the attention and all-clear paths, so an unattributed noise cannot steal focus from a person. **On Location Belief Changed** fires on every state change. See [Core Concepts](core-concepts.md#11-beliefs-about-places).

---

## APS | Explain & Record

| Node | Description |
|---|---|
| **Explain Perception** (`Target`) → `String` | Why the AI does or does not believe in this target right now |
| **Get Sense Blocker** (`Target`, `Sense ID`) → `EAPS Perception Blocker` | The specific reason one sense is silent |
| **Start Recording** (`Seconds`) | Begin capturing belief, keeping the last N seconds |
| **Stop Recording** / **Is Recording** | Control and query |
| **Get Recorded Frames** → `array<Perception Frame>` | Everything captured, oldest first |
| **Get Recorded Frames For** (`Target`) | Just one target's frames |
| **Get Recorded Frame At** (`Target`, `World Seconds`) | `bool` + `Perception Frame` |
| **Explain Recorded At** (`Target`, `World Seconds`) → `String` | A past moment, described in words |
| **Clear Recording** | Discard what was captured |

See **[Explaining & Recording](explaining-and-recording.md)**.

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

---

## APS | Config & Replication

| Node | Description |
|---|---|
| **Set Profile** (`New Profile`) | Hot-swap the entire perception profile at runtime. Use for alert states, difficulty changes, or transformations. |
| **Set Quality Profile** (`New Quality`) | Cost controls on top of the profile. Never resets anything |
| **Get Source Profile** → `Perception Profile` | The asset as assigned, before inheritance and overrides resolve |
| **Set Profile Number** (`Property`, `Value`) → `bool` | Change one numeric profile setting for this agent alone. Returns false and logs if the name does not resolve |
| **Set Profile Flag** (`Property`, `Value`) → `bool` | As above, for a checkbox |
| **Get Profile Number** (`Property`, `Fallback`) → `float` | Read one back |
| **Clear Profile Overrides** | Drop this agent's overrides and return to the asset as authored |
| **Get Replicated Perception State** → `array<Replicated Target State>`, `EAwareness Level` | Read the replicated summary on clients. Always use this rather than the raw array — it resolves the relay automatically. See [Multiplayer](multiplayer.md). |

!!! info "A profile swap does not necessarily reset anything"
    When the new profile runs the **same senses in the same order** and wants the
    same ledger capacity, the swap keeps everything the agent knows — ledger,
    emotions, attention. Only a structurally different profile rebuilds.

    This is what makes swapping profiles a safe way to scale an agent's cost up
    and down mid-encounter. It used to wipe the ledger every time, so an AI
    throttled mid-chase forgot who it was chasing.

    Per-agent overrides survive a swap, because they belong to the agent rather
    than the asset. See [Profile Composition](profile-composition.md).

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
| `Profile Overrides` | array | Per-agent changes stamped on a private copy of the profile. See [Profile Composition](profile-composition.md) |
| `Quality Profile` | APS Quality Profile | Optional cost controls. Swap with **Set Quality Profile** |

---

## Global nodes — no component needed

### Sound (`Perception | Sound`)

| Node | Description |
|---|---|
| **Emit Sound** (`Source`, `Sound Type`) | Emit a sound from an actor. Only agents within the sound type's `Max Range` are notified. |
| **Emit Sound At Location** (`Sound Location`, `Sound Type`) | Emit from a world position with no source actor |

### APS Subsystem

Get it with **Get APS Subsystem** (static, world context), then drag off the return.

#### Environment

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
| **Get Environment At** (`Location`) ⚡ | Conditions at a point, with any APS Environment volume covering it applied over the global state |
| **Get Sense Range Scale At** (`Location`, `Sense ID`) ⚡ | Range multiplier at a point for `Vision`, `Hearing` or `Smell`. Anything else returns 1 |

#### Registry

| Node | Description |
|---|---|
| **Register Perceivable Actor** (`Actor`) | Make a non-Pawn actor perceivable — turrets, vehicles, interactive props. Pawns are found automatically. |
| **Unregister Perceivable Actor** (`Actor`) | Stop it being perceivable |
| **Get Agent Count** | How many APS agents exist in the world |
| **Get Agent Significance** (`Agent`) ⚡ | The agent's latest significance score, 0 to 1. See [Scale & Crowds](scale-and-crowds.md) |

Two properties also live on the subsystem and are set from Blueprint: `Max Perception Updates Per Frame` (0 = unlimited) and `Significance Policy`.

#### Fairness

| Node | Description |
|---|---|
| **Register Never Search Zone** (`Center`, `Radius`) | A sphere AI will never search or pursue into. Guarantees the player a safe room. |
| **Unregister Never Search Zone** (`Center`, `Tolerance`) | Remove the closest zone within tolerance |
| **Clear Never Search Zones** | Remove all of them |
| **Is In Never Search Zone** (`Location`) ⚡ | Test a location |

#### Stimulus bus

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
- **Report Contact**, **Report Contact With Impulse**, **End Touch Contact** — the APS Core wrappers are usually easier

**Pain Sense**
- **Set Health Ratio** / **Get Health Ratio** / **Get Pain State** — legacy health-based degradation

---

