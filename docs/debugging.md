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

Select the **Perception Core** component → Details panel → **Debug Settings**.

| Setting | Meaning |
|---|---|
| `b Enabled` | Master switch. Turn this on first. |
| `b Editor Preview` | Draw the vision cone in the **editor viewport** without pressing Play — invaluable for placing guards and checking sightlines |
| `Debug Mode` | Which of the 7 information modes to display |
| `b Show Target Text` | Text block above each tracked target |
| `b Show AI Text` | Status line above the AI itself |
| `b Near est AI Only` | Only draw for the AI closest to the camera. **Turn this on the moment you have more than three AI.** |

### World geometry toggles

| Setting | Draws |
|---|---|
| `b Vision Cone` | The vision cone, including peripheral and rear cones when enabled |
| `b Hearing Rings` | Range rings for hearing and other radial senses |
| `b Awareness Arc` | A ground arc whose fill shows current awareness |
| `b Last Known And Uncertainty` | Last known position plus the growing uncertainty sphere |
| `b Predicted Position` | Where the AI thinks the target went |
| `b Sound Event Lines` | A line from each sound source to the AI, colour-coded by alert level, showing whether the path was clear |
| `Sound Linger Seconds` | How long those lines persist (0.5–8.0) |

### Controls

| Setting | Effect |
|---|---|
| `b Freeze Snapshot` | Freeze the overlay so you can read it while the game runs |
| `b Pause Perception` | Stop evaluating senses. Memory still decays — useful for watching decay in isolation. |

---

## The AI status line

Always drawn above the AI when `b Show AI Text` is on:

```
LOD:0 | Alert | High | Squad:Patrol_A | Role:Flanker
```

LOD tier · dominant emotion · highest threat level · squad ID · combat role.

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

