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

```
0.00 ─────────────────────────────────────────────────── 1.00
     │        │           │              │         │
   0.15     0.25        0.35           0.60      0.85
  Suspect  Telegraph   Detect         Track    Fully Aware
```

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
| LOD tier 4 (>300 m) | Suspended automatically |

---

## Debug in 4 keys

```
APS Core → Debug Settings → b Enabled  ✅
                          → Agent Scope = Focus + Outlines   (the default; keeps a squad readable)

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
| A setting seems to do nothing | Check the ⚠ list in [Troubleshooting](troubleshooting.md) — five are inert in v3.0 |

---

## Things that surprise people

- **Confidence never falls while a sense is active.** It rises or holds. Decay starts only when every sense goes silent.
- **`Vision Sample Count` is ignored** for any target carrying an APS Target Component — that component brings its own 5 samples.
- **Never-search zones are advisory.** You must call `Is Location In Never Search Zone` in your BT; nothing is blocked automatically.
- **The Pain sense reads your health component automatically** (`GetHealthPercent` / `GetHealth`+`GetMaxHealth`) and degrades *all* senses.
- **A sound asset's `Sound Name` becomes a stimulus tag** — an explosion only shakes the ground for vibration senses if that field reads exactly `Explosion`.
- **100 damage in one hit = full confidence.** Scale to your damage numbers.
- **`Set Target Confidence` only raises.** It cannot clear a detection.

---

