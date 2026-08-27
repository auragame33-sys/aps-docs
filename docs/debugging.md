# Debugging

APS ships a 7-mode on-screen debugger and a print node for every single event. **Everything here is compiled out of Shipping builds** — you cannot accidentally ship it.

> **▶ Video walkthrough** — *Debug overlay tour (5 min).* Coming soon.
> When it is live, delete this block and uncomment the embed below.

<!-- VIDEO EMBED — replace VIDEO_ID with your YouTube id, then delete the comment markers
<div class="video">
  <iframe src="https://www.youtube.com/embed/VIDEO_ID" title="Debug overlay tour" allowfullscreen></iframe>
</div>
-->

---

## Turning it on

Select the **APS Core** component → Details panel → **Debug Settings**.

| Setting | Meaning |
|---|---|
| `b Enabled` | Master switch. Turn this on first. |
| `b Editor Preview` | Draw the sense volumes in the **editor viewport** without pressing Play — invaluable for placing guards and checking sightlines. Independent of `b Enabled`. |

### Text

All text lives in a screen-space panel rather than floating in the world. World labels are anchored to moving actors at varying camera depths, so they drift, collide, and collapse to a single line when viewed at eye level; the panel allocates its rows in pixels, which makes overlap impossible rather than something to keep tuning away from.

| Setting | Meaning |
|---|---|
| `b Screen Panel` | The status panel, top-left. Shows the agent nearest the camera. |
| `b Show Sparkline` | Rolling confidence graph in the panel, with the three thresholds drawn behind it. Sampled at 20 Hz for a fixed ~5 s window regardless of framerate. |
| `b Show Target Text` | Compact state chip pinned over each tracked target. Chips push each other down rather than overlapping. |
| `b Show AI Text` | The AI's own posture and squad rows in the panel |
| `b Show Emotion Bars` | Top two emotion channels in the panel |
| `Debug Mode` | Which of the 7 information modes fills the panel body |
| `Text Scale` | Font size multiplier for world labels |
| `b Scale Text With Distance` | Shrink distant labels so the nearest agent reads first |
| `b Show Legend` | Corner key naming every colour on screen. Turn on for stills. |

### World geometry

Every sense volume only draws when that sense is actually in the profile's `Sense Classes`. Range values exist on every profile whether or not the matching sense is present, so drawing off the range alone would put a hearing ring around an AI that cannot hear.

| Setting | Draws |
|---|---|
| `b Vision Cone` | The vision cone with static range bands at ⅓ and ⅔, plus peripheral and rear cones when enabled |
| `b Hearing Rings` | Graduated hearing scope — hard boundary at max range, faint graduations at ½ and ¼, rim ticks — plus a dashed ring per Sound Type |
| `b Smell Range` | Scent radius and the downwind drift ring |
| `b Sense Fields` | Vibration and echolocation **domes** — ground ring plus two upright arcs. Vibration pulses travel inward (the ground carries footfalls *to* the AI); echolocation pulses travel outward (the AI is the emitter). |
| `b Sense Beams` | One beam per **active** sense, from the eye to the position *that sense* believes the target occupies, in that sense's colour. See below. |
| `b Awareness Arc` | Ground gauge whose fill shows confidence, with tick marks at your Suspect / Detect / Track thresholds |
| `b Last Known And Uncertainty` | Search marker, loss-direction arrow, tether to the AI that lost the target, and the growing uncertainty ring |
| `b Predicted Position` | Ghost capsule where the AI thinks the target went. Needs `b Enable Prediction`. |
| `b Sound Event Lines` | A line from each sound source to the AI, colour-coded by alert level, showing whether the path was clear |
| `Sound Linger Seconds` | How long those lines persist (0.5–8.0) |
| `b Environment Visuals` | Wind streamers drifting downwind, and a vertical light gauge beside the AI marked at `Darkness Min Detection` |
| `b Ground Anchor` | Contact ring at the AI's feet |

### Style

| Setting | Meaning |
|---|---|
| `Palette` | `Cinematic` (camera-safe) · `Tactical` (high contrast) · `Colorblind Safe` (deuteranopia/protanopia safe) · `Legacy`. Applies instantly, no restart. |
| `b Animated Visuals` | Turn off for a completely static frame when shooting stills |
| `b Cone Volume` | Depth ribs and a centre line inside the cone, so it reads as a volume |
| `b Secondary Cones` | Draw peripheral and rear-motion cones when the profile enables them |
| `b Draw Through Walls` | Render everything on top of world geometry |
| `Line Thickness` | Global line weight multiplier. Push to ~1.8 for 4K capture. |

### Controls

| Setting | Effect |
|---|---|
| `Agent Scope` | How much of a squad draws at once — see below |
| `b Nearest AI Only` | Legacy alias for `Agent Scope = Focus Only`. When true it overrides `Agent Scope`. |
| `b Freeze Snapshot` | Freeze the overlay so you can read it while the game runs |
| `b Pause Perception` | Stop evaluating senses. Memory still decays — useful for watching decay in isolation. |

---

## Reading a squad — `Agent Scope`

Full detail on every agent is unreadable past about three of them: the range rings alone overlap into one mesh of circles and no individual agent can be picked out.

| Value | Behaviour |
|---|---|
| `Focus Only` | Only the agent nearest the camera draws anything |
| **`Focus + Outlines`** | **Default.** Nearest agent in full; every other agent as a ground ring, a facing wedge, and a state dot that grows with confidence |
| `All Agents` | Every agent in full detail. Honest, and unreadable past a few. |

Facing is most of what you need to read a squad — whether you can cross behind them. The outline gives you that plus alert level, and you pull the details by pointing the camera at one.

---

## Sense beams — what each sense actually believes

The clearest read on a multi-sense agent. Each **active** sense draws a beam from the AI's eye to the position *that sense* believes the target occupies — not the fused position.

The payoff is the spread. Vision lands on the target; smell lands somewhere downwind of it; hearing lands wherever the last noise was. **The gap between the beam ends is the disagreement fusion is resolving.** Each beam ends in a ring sized by that sense's own `Location Accuracy` — tight for touch, wide and vague for smell.

Every sense has one colour, used by its beam, its range volume, its panel swatch and its panel row alike. A custom sense gets a stable colour hashed from its own Sense ID, outside the bands the built-ins occupy.

---

## The status panel

```
┌────────────────────────────────┐
│ ▌ TRACKED                  72% │   ← state chip: colour = lifecycle state
│ BP_GUARD              [SENSE]  │   ← agent name · current debug mode
│ > THIRDPERSONCHARACTER         │   ← attention target
│ ▁▂▃▅▆▇█▇▆▅▃▂▁▂▃▅▆▇█            │   ← confidence history, thresholds behind
│ SENSES                         │
│ ■ VISION    ████████░░    82%  │
│ ■ HEARING   ███░░░░░░░    31%  │
│ ■ SMELL     ░░░░░░░░░░     0%  │   ← owned but silent: still listed
│ ────────────────────────────── │
│ FUSED 0.92   SMOOTH 0.87       │   ← mode body
│ ────────────────────────────── │
│ CURIOUS   THREAT LOW   LOD0    │
│ LIGHT ████░░ 40%               │
│ WIND 120 cm/s   OUTDOORS       │
└────────────────────────────────┘
```

A sense the agent owns but which is reporting nothing still gets a row. A silent sense is a finding — dropping it from the list would hide exactly the case you are trying to diagnose.

---

## The 7 modes

Switch with `Debug Mode`, or call **Debug Cycle Display Mode** at runtime (bind it to a key).

### Sense — *"what is each sense contributing?"*

```
[TRACKED] 87%  3.2s
Vision:82% Hearing:31% Smell:0%
Fused:0.92 Smooth:0.87
```

Lifecycle state, smoothed confidence, time in state, per-sense breakdown, and fused vs smoothed values. **Start here for every detection problem.** If a sense reads 0% it is not contributing, and you know exactly where to look.

### Memory — *"what does it remember and how sure is it?"*

```
[LOST] TimeInState:4.1s
SinceSensed:4.4s  LTM:0.38
Uncert:220cm  Dist:180cm
```

Time in state, time since any sense was active, long-term memory strength, uncertainty radius, and the distance between last known and predicted position. Use it to tune decay curves and search radii.

### Brain — *"how does it feel about this target?"*

```
[TRACKED] Threat:High 0.71
Via:Vision  Rel:Enemy
DmgRecv:45.0  Enc:3  Known:YES
```

Threat level and score, the dominant stimulus source, resolved relationship, damage received, encounter count, and whether this is a known threat.

### Squad — *"is squad coordination wired up?"*

```
Squad:Patrol_A
Role:Suppressor
ShareRange:3000  MinThreat:Low
```

Squad ID, current role, share range and minimum share threat. For deeper squad debugging use the dedicated nodes below.

### Delegates — *"did the event actually fire?"*

```
Last Event:
OnAIDetect
@ 12.4s
```

The last delegate fired for each target and when. The fastest way to answer *"is my Blueprint not bound, or did the event never fire?"*

### Player Model — *"what has it learned about me?"*

Crouch / sprint / walk ratios, stealth and aggression ratios, engagement count, whether the model has enough data, a plain-language style assessment, and recent hide locations.

### Environment — *"is my weather system actually reaching the AI?"*

Light level, rain intensity, wind speed and direction, indoors flag, time of day, and total pain level. If your day/night cycle is not affecting AI, this is where you find out.

---

## Print nodes

Every event has a one-node print function under `APS | Debug`. Bind the event, drop in the matching node, wire the pins straight through. Output goes to the screen for 5 s **and** the Output Log.

```
Event On AI Detect (Target, Threat Level, Stimulus)
  └─► Print_OnAIDetect (Target, Threat Level, Stimulus)
```

Colour coding: **cyan** senses · **green** lifecycle · **yellow** brain/threat · **orange** pain/emotion · **purple** squad · **white** state changes.

The full set: `Print_OnAISee`, `Print_OnAIHear`, `Print_OnAISmell`, `Print_OnAIFeel`, `Print_OnAISenseVibration`, `Print_OnAISuspect`, `Print_OnAIDetect`, `Print_OnAITrack`, `Print_OnAILost`, `Print_OnAIRemember`, `Print_OnAIForget`, `Print_OnAIThinkThreat`, `Print_OnThreatIdentified`, `Print_OnAIAllClear`, `Print_OnAIAwarenessChanged`, `Print_OnAIPainReported`, `Print_OnAIDamaged`, `Print_OnAISquadAlert`, `Print_OnTargetStateChanged`, `Print_OnEmotionalStateChanged`, `Print_OnCombatRoleAssigned`.

One extra, squad-specific: **`Print_OnAISquadAlert_Tagged`** (`Receiver`, `Target`, `Location`, `Threat`) — same output as `Print_OnAISquadAlert` but prefixed with the receiving agent's name, so a squad-wide alert reads as one line per recipient instead of five identical lines.

---

## Squad debugging toolkit

Under `APS | Debug | Squad`:

| Node | Use it when |
|---|---|
| **Debug Trace Squad Share Path** (`Sender`, `Target`) | **Sharing is not working.** Dry run that checks squad ID → same squad → in range → above min threat, and prints the exact failure point per member. |
| **Debug Print Squad State** (`Agent`) | Verifying the squad is wired up at all |
| **Debug Print Squad Beliefs** (`Agent`, `Target`) | Confirming a share actually landed |
| **Debug Simulate Squad Share** (`Sender`, `Target`, `Receiver`) | Testing the pipeline with a single AI pair |
| **Debug Simulate Squad Alert** (`Receiver`, …) | Testing one AI's reaction in isolation |
| **Debug Force Full Squad Share** (`Sender`, `Target`) | Testing the receive side without fighting setup conditions |
| **Debug Watch Squad** (`Agent`) | Live HUD panel — call on Event Tick from one AI |

---

## Component debug nodes

| Node | Effect |
|---|---|
| **Debug Print Belief State** | Dump the full ledger to the Output Log |
| **Debug Toggle Pause** | Freeze perception evaluation at runtime |
| **Debug Toggle Freeze Snapshot** | Freeze the overlay |
| **Debug Cycle Display Mode** | Step through the 7 modes — bind to a key |
| **Debug Reset Damage Tracking** | Clear damage bookkeeping between tests |

### A useful debug key setup

```
Input Action "F1" → Debug Cycle Display Mode
Input Action "F2" → Debug Toggle Freeze Snapshot
Input Action "F3" → Debug Toggle Pause
Input Action "F4" → Debug Print Belief State
```

Run those on whichever AI is nearest the camera and you can inspect a live encounter without leaving the game.

---

## A debugging workflow that works

**"The AI doesn't detect me."**
1. Debug Mode → **Sense**. Is any sense above 0%?
2. All zeros → the target is not in range, not in the cone, or fully occluded. Turn on `b Vision Cone` and look.
3. One sense reads a value but the state stays `Undetected` → your `Suspect`/`Detect` thresholds are too high, or `Confidence Rise Rate` is too low.

**"The AI detects me instantly from across the map."**
1. **Sense** mode → which sense is spiking? Usually Hearing.
2. Check that sound type's `Max Range` and `Base Loudness`.
3. Add a `Sound Filter Profile` with a higher `Min Alert Level`.

**"The AI sees through walls."**
1. Add your wall's collision channel to `Vision Occlusion Channels`.
2. Confirm the walls actually block that channel.
3. Check `Surface Vision Transmission` — a surface set to `1.0` is fully transparent.

**"My event never fires."**
1. Debug Mode → **Delegates**. Did the event fire at all?
2. It fired → your binding is wrong, or you are bound to a different component instance.
3. It did not fire → the state transition never happened. Go back to **Sense** mode.

**"Squad sharing does nothing."**
Run **Debug Trace Squad Share Path**. It tells you the exact step that failed.

---

## Before you ship

- [ ] `Debug Settings → b Enabled` off on every AI Blueprint
- [ ] `b Editor Preview` off
- [ ] Remove or disable `Print_*` nodes from production graphs
- [ ] Remove `Debug Watch Squad` from any Tick

Everything is stripped from Shipping builds automatically, but leaving it on in Development builds costs real frame time.

---

