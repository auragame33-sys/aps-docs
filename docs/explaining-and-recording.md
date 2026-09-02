# Explaining & Recording

**Two answers to the same question: *why did it do that?***

Perception bugs are temporal. The frame that explains the problem is always the one that just went past, and by the time you have noticed something is wrong the AI has moved on. These are the tools for that.

---

## Why can't it see me?

**Explain Perception** (`Target`) returns a written account of what this AI currently believes about a target and what is standing in the way.

```
Print String (Explain Perception (Player))
```

Bind it to a debug key and you have an answer in one keypress instead of an afternoon.

### Blocker reasons

**Get Sense Blocker** (`Target`, `Sense ID`) returns the specific reason one sense is not contributing.

| Reason | Means |
|---|---|
| **None** | Nothing is blocking it |
| **Out Of Range** | Beyond that sense's reach |
| **Outside Cone** | Within range, but not within the cone |
| **Occluded** | Line of sight is blocked by geometry |
| **Below Min Exposure** | Visible, but not enough of the target is exposed |
| **Too Few Visible Points** | Not enough sample points cleared for this stance |
| **Target Opted Out** | The target excluded itself from this sense |
| **Suppressed By Pain** | The AI is too hurt to use this sense right now |
| **Fairness Reaction Hold** | The telegraph window is still running — deliberate, not a fault |
| **Not Evaluated This Tick** | This sense did not run on this tick |
| **No Context** | The sense had nothing to evaluate against |

!!! tip "Two of these are not problems"
    **Fairness Reaction Hold** is the AI deliberately giving the player their
    reaction window — see [Environment & Fairness](environment-and-fairness.md).
    **Not Evaluated This Tick** just means that sense runs on a slower interval
    than the tick you sampled; check again next frame.

---

## What did it believe *then*?

A recording keeps a rolling window of belief so you can read a moment after it has passed.

```
Start Recording (30.0)

...later, once something has visibly gone wrong...

Print String (Explain Recorded At (Suspect, When It Happened))
```

| Node | Does |
|---|---|
| **Start Recording** (`Seconds`) | Begin capturing, keeping the last N seconds |
| **Stop Recording** | Stop. What was captured stays available |
| **Is Recording** | Whether one is running |
| **Get Recorded Frames** | Everything captured, oldest first |
| **Get Recorded Frames For** (`Target`) | Just the frames about one target |
| **Get Recorded Frame At** (`Target`, `World Seconds`) | The frame nearest that moment |
| **Explain Recorded At** (`Target`, `World Seconds`) | That frame, described in words |
| **Clear Recording** | Discard what was captured |

### What a frame holds

| Field | Meaning |
|---|---|
| `Time Seconds` | World time when captured |
| `Target` | Who the belief was about |
| `Confidence` | Confidence as acted on, after smoothing |
| `Raw Confidence` | As the senses reported it, before smoothing |
| `State` | Lifecycle state at that moment |
| `Awareness` | Awareness level at that moment |
| `Last Known Position` | Where the AI believed the target was |
| `Time Since Last Sensed` | Seconds since any sense had it |
| `Active Sense Count` | How many senses were contributing |

`Confidence` against `Raw Confidence` is often the whole diagnosis: a large gap means smoothing is holding a belief the senses have already let go of.

### Cost and bounds

Recording is **off until you ask for it**. While running it costs one small frame per tracked target per tick. Frames older than the window are dropped rather than accumulated, so a long session does not grow without limit.

Set the window to comfortably cover the gap between a problem happening and you noticing it — 30 seconds is usually generous.

---

## Which to reach for

| Situation | Use |
|---|---|
| "It cannot see me *right now*" | **Explain Perception** |
| "One specific sense is silent" | **Get Sense Blocker** |
| "It did something odd ten seconds ago" | **Start Recording** + **Explain Recorded At** |
| "It behaves wrongly but I cannot catch it" | Record, reproduce, then read the window back |

---

## See also

- **[Debugging](debugging.md)** — the on-screen debug modes
- **[Troubleshooting & FAQ](troubleshooting.md)** — symptoms and their usual causes
