# Cheat Sheet

*Everything you use daily, on one page. Bookmark this one.*

---

## Minimum setup

```
1.  Data Asset → PerceptionProfile        →  DA_Profile_MyAI
2.  AI Character → Add Component          →  APS Core     (assign the profile)
3.  AI Character → Add Component          →  APS Perception Listener
4.  Player       → Add Component          →  APS Target Component
5.  Footstep notify → Emit Sound (Self, DA_Sound_Footstep)
```

---

## Ten words you will see everywhere

| Term | Meaning |
|---|---|
| **Confidence** | A 0 to 1 belief that a target is where a sense says it is. Every sense produces one per target on every tick it runs. |
| **Fused** and **Smoothed** | Fused is this tick's raw combination of the senses. Smoothed is the version that drives everything: it rises while a sense is active, holds, and decays only once every sense is silent. |
| **Lifecycle state** | Undetected → Suspected → Detected → Tracked → Lost → Remembered → Expired, per target, with an event on every transition. |
| **Awareness** | The AI's overall alert level, derived from its top target: Unaware, Peripheral, Suspicious, Alerted, Fully Aware. |
| **Attention target** | The one target the AI is committed to. Sticky, so it does not flicker between two similar contacts. |
| **Loss reason** | Why contact broke: Occluded, Out Of Range, Sound Faded, Scent Lost, Sensor Dropout. It decides how the AI should search. |
| **Belief record** | Everything the AI holds about one target, in one struct. `Get Belief Data` returns it. |
| **Profile** | The data asset holding every perception setting for one archetype. Swap it to change how an AI perceives. |
| **Evidence** | A scripted floor, ceiling, reduction or reset on belief about a target. A disguise, an alibi, a cutscene. |
| **Place belief** | A belief about a location rather than an actor: a gunshot with no known shooter, a body, a forced lock. |

---

## The 10 nodes you will actually use

| Node | Returns | For |
|---|---|---|
| **Get Attention Target** | Actor | The target to chase. Use this, not `Get Top Target`. |
| **Get Last Known Position** | Vector | Where to search |
| **Get Loss Reason** | enum | **How** to search — branch on it |
| **Get Uncertainty Radius** | float | Search radius, grows over time |
| **Get Awareness Level** | enum | Alert music, weapon poses, HUD |
| **Get Belief Data** | struct | Everything about one target |
| **Get Sense Contributions** | map | Did it *see* me or only *hear* me? |
| **Emit Sound** | — | Make a noise the AI can hear |
| **Set Target Confidence** | — | Force a detection (raises only) |
| **Set Profile** | — | Hot-swap the whole perception setup |

## The 8 events you will actually use

| Event | Fires when | Typical response |
|---|---|---|
| **On AI Telegraph** | About to be noticed | "Huh?" bark, head turn |
| **On AI Suspect** | Something's there | Look, walk over |
| **On AI Detect** | Confirmed | Alert, take cover, call out |
| **On AI Track** | Locked on | Chase, shoot |
| **On AI Lost** | Contact broken | **Read `Get Loss Reason`**, then search |
| **On AI Forget** | Given up | Back to patrol |
| **On Attention Changed** | New focus target | Cancel pursuit, re-plan |
| **On AI Damaged** | Took a hit | React to unseen attacker |

---

## Loss reason → what the BT should do

| Loss Reason | Meaning | Action |
|---|---|---|
| `Occluded` | Broke line of sight | Go to last known, search **that cover object** |
| `OutOfRange` | Walked out of range | Move to last known, expand along `Get Loss Direction` |
| `SoundFaded` | Noise stopped | Investigate the area — **don't chase** |
| `ScentLost` | Scent dissipated | Follow `Get Loss Direction` as a trail |
| `SensorDropout` | Signal just stopped | Short look, resume patrol |
| `TargetDestroyed` | Actor gone | Clear the target |

---

## Sense → what feeds it

| Sense | Needs from you | Passes walls? |
|---|---|---|
| **Vision** | Nothing | No |
| **Hearing** | `Emit Sound` — **required** | No |
| **Smell** | Nothing | Partly |
| **Touch** | Nothing (auto-wired) | n/a |
| **Vibration** | Nothing for movement | **Yes** |
| **Damage** | Nothing (auto-wired) | **Yes** |
| **Pain** | `Report Pain From Definition` | n/a |
| **Echolocation** | Nothing | **Yes** |

---

## Default thresholds

<div class="aps-figure">
<svg viewBox="0 0 680 150" role="img" aria-labelledby="fig-thresholds">
  <title id="fig-thresholds">Default confidence thresholds and the states they open</title>
  <g class="band">
    <rect class="band0" x="40" y="70" width="90" height="16"/>
    <rect class="band1" x="130" y="70" width="120" height="16"/>
    <rect class="band2" x="250" y="70" width="150" height="16"/>
    <rect class="band3" x="400" y="70" width="240" height="16"/>
  </g>
  <line class="ln" x1="40" y1="78" x2="640" y2="78"/>
  <g class="tick">
    <line x1="130" y1="60" x2="130" y2="96"/><line x1="190" y1="60" x2="190" y2="96"/><line x1="250" y1="60" x2="250" y2="96"/><line x1="400" y1="60" x2="400" y2="96"/><line x1="550" y1="60" x2="550" y2="96"/>
  </g>
  <g class="lbl b" text-anchor="middle">
    <text x="130" y="48">SUSPECT</text><text x="190" y="30">TELEGRAPH</text><text x="250" y="48">DETECT</text><text x="400" y="48">TRACK</text><text x="550" y="48">FULLY AWARE</text>
  </g>
  <g class="sub" text-anchor="middle">
    <text x="130" y="116">0.15</text><text x="190" y="116">0.25</text><text x="250" y="116">0.35</text><text x="400" y="116">0.60</text><text x="550" y="116">0.85</text>
    <text x="40" y="116">0</text><text x="640" y="116">1.0</text>
  </g>
  <g class="sub" text-anchor="middle">
    <text x="85" y="140">Undetected</text><text x="190" y="140">Suspected</text><text x="325" y="140">Detected</text><text x="520" y="140">Tracked</text>
  </g>
</svg>
</div>

| Confidence | Lifecycle state | Awareness level |
|---|---|---|
| ≥ 0.85 | Tracked | **Fully Aware** |
| ≥ 0.60 | **Tracked** | Alerted |
| ≥ 0.35 | **Detected** | Suspicious |
| ≥ 0.15 | **Suspected** | Peripheral |
| < 0.15 | Undetected | Unaware |

Step-downs need a **0.04** margin below the threshold (hysteresis).

---

## Difficulty dial

| Setting | Easy | Normal | Hard |
|---|---|---|---|
| Suspect / Detect / Track | 0.25 / 0.50 / 0.75 | 0.15 / 0.35 / 0.60 | 0.10 / 0.25 / 0.45 |
| Confidence Rise Rate | 3.0 | 5.0 | 7.0 |
| First Spot Reaction Time | 0.8 | 0.4 | 0.1 |
| Min Time In Lost | 3 | 8 | 15 |

Leave cone angles and occlusion **identical** across difficulties — the player's mental model of what a guard can see shouldn't change.

---

## Performance dial

| Lever | Effect |
|---|---|
| `Base Update Interval` 0.1 → 0.2 | **Halves** perception cost |
| Trim APS Target Component samples 5 → 3 | −40% vision traces |
| `Max Tracked Targets` 16 → 4 | Less memory, faster sorting |
| One occlusion channel instead of three | −66% trace count |
| Assign an `APS Quality Profile` | Scales tick rate and trims vision samples without resetting what the AI believes |
| `b Enable Statistical Tier` | Distant agents stop tracing entirely |
| LOD tier 4 | Suspended automatically. Roughly beyond 225 m for an idle agent |

---

## Debug in 4 keys

```
APS Core → Debug Settings → b Enabled  ✅
                          → Agent Scope = Focus + Outlines  (default)

F1 → Debug Cycle Display Mode     F3 → Debug Toggle Pause
F2 → Debug Toggle Freeze Snapshot F4 → Debug Print Belief State
```

**Sense** mode answers 90% of "why isn't it detecting me" questions — and the **sense beams** answer it without reading anything: each active sense draws a beam to where *it* thinks you are.

A sense volume only appears when that sense is in the profile's `Sense Classes`. If you see no scent ring, the AI has no Smell sense — that is the visualisation being honest, not broken.

---

## Fast fixes

| Symptom | Fix |
|---|---|
| Detects nothing at all | Profile not assigned, or `Sense Classes` empty |
| Hears nothing | You never called `Emit Sound` |
| Sees through doors | Add the channel to `Vision Occlusion Channels` |
| Sees you the instant you enter the cone | Set `First Spot Reaction Time` 0.3–0.5 |
| Sees you before it turns | Set `Eye Turn Rate Deg Per Sec` ≈ 200 |
| Forgets instantly | Raise `Vision Loss → Grace Time` to 0.8–1.5 |
| Never forgets | Raise `Default Decay Exponent` |
| Searches in a dumb circle | You're not branching on `Get Loss Reason` |
| Whole squad detects at once | Turn off `b Auto Share On Detect` |
| Client sees nothing | Use `Get Replicated Perception State` |
| Cone points at the sky | `Eye Socket Alignment` → **Automatic** |
| Crouch-walk is not hiding me | Set `Min Visible Points Crouched` to 2 |
| "Why can't it see me?" | Print `Explain Perception` (Target) |
| A thrown-rock sound is ignored | Sourceless sounds arrive on `On Location Belief Changed`, not `On AI Hear` |
| A setting seems to do nothing | Check the ⚠ list in [Troubleshooting](troubleshooting.md) — five are inert in v3.0 |

---

## Things that surprise people

- **Confidence never falls while a sense is active.** It rises or holds. Decay starts only when every sense goes silent.
- **`Vision Sample Count` is ignored** for any target carrying an APS Target Component — that component brings its own 5 samples.
- **Never-search zones are advisory.** You must call `Is Location In Never Search Zone` in your BT; nothing is blocked automatically.
- **The Pain sense reads your health automatically.** It asks for an `APS Health Provider` interface first, then falls back to a function named `GetHealthPercent`, or `GetHealth` with `GetMaxHealth`, and degrades *all* senses.
- **Sourceless sounds never fire `On AI Hear`.** `Emit Sound At Location` creates a belief about a place. Read it with `On Location Belief Changed`.
- **Idle AI tick at half rate.** An agent that is not at least Suspicious can never reach LOD tier 0, whatever the distance.
- **A sound asset's `Sound Name` becomes a stimulus tag** — an explosion only shakes the ground for vibration senses if that field reads exactly `Explosion`.
- **100 damage in one hit = full confidence.** Scale to your damage numbers.
- **`Set Target Confidence` only raises.** It cannot clear a detection.

---

