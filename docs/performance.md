# Performance

APS is built to run many agents at once. The main costs are **line traces** (vision), **target iteration**, and **tick frequency** — and all three have direct controls.

---

## Automatic distance LOD

The APS subsystem measures every agent's distance from the player camera and assigns a **LOD tier 0–4**. The tier scales the perception tick interval automatically. No setup.

| Tier | Distance from camera | Tick interval | Notes |
|---|---|---|---|
| **0** | < 30 m | `Base Update Interval` × 1 | Full rate |
| **1** | 30–80 m | × 2 | |
| **2** | 80–150 m | × 5 | |
| **3** | 150–300 m | × 20 | Barely evaluating |
| **4** | > 300 m | **Suspended** | Senses stop entirely; memory still decays so state stays coherent |

At tier 4 nothing is evaluated — but belief records keep decaying, so an AI that comes back into range does not resume with stale certainty. It has forgotten you, exactly as it should have.

LOD tiers also gate sounds and stimuli: a `Sound Type` with `Max LOD Tier = 1` is never even considered by AI at tier 2 or above. That is why setting sensible LOD tiers on your sound assets matters — it is a free, large saving.

---

## The levers, in order of impact

### 1. Base Update Interval

`Performance → Base Update Interval` (default 0.1 s)

The single biggest lever. Perception ticks 10× per second by default.

| Value | Feel | Use for |
|---|---|---|
| 0.05 | Extremely reactive | Bosses, single-enemy encounters |
| 0.1 | Default — reactive | Main combat AI |
| 0.2 | Slightly sluggish, rarely noticeable | Background AI, crowds |
| 0.5 | Clearly slow | Ambient NPCs, distant patrols |

**Doubling this halves your perception cost.** For most AI, 0.15–0.2 s is indistinguishable from 0.1 s in play.

### 2. Visibility sample count

Sample points are **traces per target per evaluation**, and they come from one of three places — which is what makes this lever confusing:

| Target has… | Sample points used | Controlled by |
|---|---|---|
| An **APS Target Component** | That component's `Visibility Samples` (**5 by default**) | The component |
| No component, profile has `Default Visibility Samples` | Those entries | The profile array |
| Neither | Built-in head/chest/pelvis/shoulders | `Vision Sample Count` (1–5) |

> ⚠ **`Vision Sample Count` does nothing for targets carrying an APS Target Component.** Since the component ships pre-filled with 5 samples, adding it to your player means every observing AI traces 5 rays regardless of what the profile says. This is the single most common reason a "reduce sample count" optimisation shows no improvement.

To actually cut trace cost:

- **For the player and named NPCs** — trim entries from the **APS Target Component's** `Visibility Samples` array. Head + chest + pelvis (3) keeps partial-cover behaviour almost intact.
- **For crowd/background actors** — do not give them a Target Component at all, and set `Vision Sample Count` to 1–3 on the observing profile.

| Count | Quality |
|---|---|
| 5 | Full partial-cover fidelity. Player and key NPCs. |
| 3 | Very good. The right default for most projects. |
| 1 | Epic-equivalent — binary, no partial cover. Crowds and background AI only. |

### 3. Max tracked targets

`Performance → Max Tracked Targets` (default 16)

Slots are **pre-allocated**, so this is memory as well as CPU. Most AI never need 16.

| Value | Use for |
|---|---|
| 2–4 | Single-player games — the player plus a companion or two |
| 8 | Small squad combat |
| 16 | Large battles, many factions |

### 4. Sense intervals

`Senses | Setup → Sense Intervals` — a per-sense override.

Not every sense needs the same rate. Smell changes slowly; there is no reason to evaluate it as often as vision.

```
Vision       0.15
Hearing      0.1     (event-driven, cheap)
Smell        0.4
Vibration    0.2
Echolocation 0.4
```

### 5. Occlusion channels

`Detection|Occlusion → Vision Occlusion Channels` — **every extra channel is another trace per sample point**.

One channel × 5 samples = 5 traces. Three channels × 5 samples = 15 traces. Add channels only where the gameplay actually needs them.

### 6. Target gather range

Candidates are gathered within the largest of `Vision Max Range`, `Hearing Max Range` and each sense's **declared** max range. A 20,000 cm hearing range means every AI iterates every Pawn in a 200 m sphere.

Keep ranges honest. If your sniper only needs 9,000 cm, do not set 20,000.

The gather itself is throttled to `max(0.2 s, Base Update Interval)` — at most 5 Hz — and iterates all Pawns in the world plus any non-Pawn actors in the perceivable registry. On very large levels with hundreds of pawns this iteration, not the traces, can become the cost. There is no spatial hash; if you hit that ceiling, the practical fix is fewer Pawns or a longer `Base Update Interval`.

Note that Vibration and Echolocation declare **fixed** gather ranges (800 and 2000 cm) that do not follow their profile settings. Raising `Vibration Detect Range` or `Echo Range` past those needs another sense on the same profile with a long enough range, or distant targets are never handed to them.

---

## Things that cost almost nothing

- **Idle AI.** With no targets in range, a tick is a distance check and an early out.
- **Extra senses that are silent.** A sense that returns `b Is Active = false` contributes nothing to fusion and costs one function call.
- **Sound emission.** The per-agent pipeline rejects distant agents on a squared-distance check before doing anything expensive.
- **Events with no bindings.** An unbound delegate is a null check.
- **The Listener component.** Unimplemented events are no-ops.
- **LOD tier 4 agents.** Suspended.

---

## Budget guidance

Rough, on a mid-range desktop CPU. Measure your own project — geometry complexity dominates trace cost.

| Agent count | Configuration |
|---|---|
| **1–10** | Everything on, defaults everywhere. No tuning needed. |
| **10–30** | `Base Update Interval` 0.15 · `Vision Sample Count` 3 · `Max Tracked Targets` 8 |
| **30–80** | `Base Update Interval` 0.2 · `Vision Sample Count` 3 · `Max Tracked Targets` 4 · per-sense intervals tuned · one occlusion channel |
| **80–200** | Two profiles: a "near" profile at the settings above, and a "far" profile at `Base Update Interval` 0.5, `Vision Sample Count` 1, `Max Tracked Targets` 2 — swapped with **Set Profile** based on distance |
| **200+** | As above, plus disable expensive senses entirely on the far profile and rely on LOD tier 4 suspension |

---

## The profile-swap pattern

The most effective large-scale optimisation. Two profiles, same archetype:

```
DA_Profile_Guard_Near   — full fidelity
DA_Profile_Guard_Far    — 0.5s interval, 1 sample, 2 targets, no per-target light
```

```
On a 2-second timer (or a distance-change event):
  Branch: Distance to nearest player < 5000
    True  → Set Profile (DA_Profile_Guard_Near)
    False → Set Profile (DA_Profile_Guard_Far)
```

`Set Profile` rebuilds senses and resets the ledger, emotions and attention — so **do not call it every tick**, and avoid swapping while an AI is mid-engagement. Gate it on `Has Any Detection == false` if that matters to you.

---

## Profiling

Use Unreal's standard tools:

```bash
stat game
```

```bash
stat unit
```

The perception tick shows up under component ticking. For trace cost specifically, `ProfileGPU` will not help — use `stat game` and toggle `Vision Sample Count` between 5 and 1 to measure the delta on your actual level.

Quick isolation test: set `Debug Settings → b Pause Perception` on every AI. If your frame time does not improve, APS is not your bottleneck.

---

## Things that are expensive — use deliberately

| Feature | Cost | When it is worth it |
|---|---|---|
| `b Use Per Target Light` + `b Trace Sun Shadow` | One extra trace per target per evaluation | Stealth games where shadow is a mechanic |
| `Surface Vision Transmission` | Traces become complex (multi-hit) rather than simple | Foliage, smoke, glass as real cover |
| `b Pawns Block Sight` | More trace hits to process | Squad combat where body-blocking matters |
| Multiple occlusion channels | Linear multiplier on trace count | Doors and vehicles must block sight |
| `Vision Sample Count` 5 | 5 traces per target per evaluation | Partial cover is a core mechanic |
| `b Requires Clear Path` on stimuli | A trace per agent per stimulus | Rarely — prefer the sound system, which already does this efficiently |

---

## Memory

- **Belief records are pre-allocated** at `Max Tracked Targets` and reused. Zero runtime allocation during steady-state perception.
- **Sense instances** are one `UObject` per sense per AI, created once at Begin Play.
- **Episodic memory** is a fixed 5-entry ring buffer per target.
- **Player behavior models** are one small struct per observed target.

An AI with 8 senses and 16 target slots is a few kilobytes. Agent count is a CPU question, not a memory one.

---


## Beyond one agent

Everything above is per-agent cost. For level-wide scaling — significance, frame budgets, the statistical crowd tier, environment volumes and async tracing — see **[Scale & Crowds](scale-and-crowds.md)**.

To see what a profile is asking for before you fill a level with it, press **Show Budget** on the asset — see **[Profile Composition](profile-composition.md)**.
