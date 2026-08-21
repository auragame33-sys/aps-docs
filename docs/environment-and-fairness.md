# Environment & Fairness

**For:** wiring your world into perception — light, weather, wind — and making detection feel fair to the player.

---

# Environment

The **APS Subsystem** holds world-wide state that every AI reads. Get it once with **Get APS Subsystem** (static node, works from any Blueprint).

## Light

| Node | Purpose |
|---|---|
| **Set Ambient Light** (`Level` 0–1) | Global light level. Drive it from your day/night cycle. |
| **Set Sun Direction** (`Direction`) | Pass your directional light's **forward vector**. Required for per-target shadow tracing. |

Global ambient light models day and night. It does **not** model a dark corner of a lit room — for that, turn on `b Use Per Target Light` in the profile, which traces from the target toward the sun and applies `Shadow Light Level` when the target is occluded from it. Shadow can only darken, never brighten: the result is `min(ambient, ShadowLightLevel)`.

The resulting vision multiplier is `Lerp(Darkness Min Detection, 1.0, lightLevel)`, so `Darkness Min Detection` is both the floor and the amount of the effect.

**Best accuracy** comes from your own light-gem system: set `Light Level Override` on the target's APS Target Component and it wins over both the shadow trace and global ambient. `-1` (the default) means "let the AI work it out".

> ⚠ `Light Level Override` is only consulted when the observing AI's profile has **`b Use Per Target Light` on**. With it off, the whole per-target path is skipped and global ambient is used — your override is silently ignored.

## Weather & wind

| Node | Purpose |
|---|---|
| **Set Weather Modifier** (`Mod` 0–1) | Global visibility modifier. Multiplies Vision, Hearing and Smell confidence. |
| **Set Wind State** (`Direction`, `Speed`) | Wind **speed** dampens scent globally (1.0× → 0.25× as speed reaches 800). ⚠ The **direction** stored here does *not* drive Smell's upwind/downwind bonus — see [The Senses → Smell](senses.md). |
| **Set Indoors** (`b Indoors`) | Indoors **boosts** scent (×1.2) — it does not disperse |
| **Set Time Of Day** (`Hour` 0–24) | For your own logic and the debug overlay |
| **Set Environment State** (`New State`) | Set everything in one call |
| **Get Environment State** | Read the current struct |

Built-in environmental effects:

| Condition | Effect |
|---|---|
| Darkness | Vision down to 0.35× |
| Rain | Hearing down to 0.55× at full intensity |
| Wind | Smell down to 0.25× at 800 cm/s and above |
| Indoors | Smell up to 1.2× |

### Wiring a weather system

```
Weather actor, on state change:
  Get APS Subsystem
    ├─► Set Ambient Light    (0.2 at night, 1.0 at noon)
    ├─► Set Weather Modifier (1.0 clear, 0.4 heavy rain)
    ├─► Set Wind State       (wind direction, wind speed)
    └─► Set Sun Direction    (Directional Light → Get Forward Vector)
```

A storm now genuinely makes AI harder to sneak past by sight but easier to sneak past by sound — with no AI-specific code at all.

## The perceivable registry

**Pawns are found automatically.** Every `Pawn` in the world within maximum sense range is a candidate target, with no registration needed. Targets sharing the observer's controller are skipped.

For **non-Pawn actors** — turrets, vehicles, security cameras, interactive props, a dropped weapon that should draw attention:

| Node | Purpose |
|---|---|
| **Register Perceivable Actor** (`Actor`) | Call on Begin Play |
| **Unregister Perceivable Actor** (`Actor`) | Call on End Play |

Or just add an **APS Target Component** with `b Auto Register As Perceivable` ticked (the default) and it registers itself.

---

# Fairness

Every shipped stealth game has these rules. None of them exist in the engine. They are what separates an AI that feels *sharp* from one that feels *cheap*.

**All of them are opt-in and default to off**, so they never change behaviour until you ask for them.

## First-spot reaction time

`Fairness → First Spot Reaction Time` (default `0.0`)

On **first acquisition only**, the AI must hold the target for this long before confidence starts accumulating at all. This is reaction time — it gives the player a beat to step back out of view after blundering into the open.

- `0.0` — instant, machine-like. Correct for turrets and cameras.
- `0.3` — sharp but human.
- `0.5` — noticeably forgiving. Good for the first level, or an easy difficulty.
- `1.0` — very generous. Good for accessibility options.

**The gate applies only until the AI has detected that target once.** It is keyed on `b Was Ever Detected` in the belief record, so once you have been spotted, every later re-acquisition of that target is instant — which is the right behaviour, but means the grace is a *first impression*, not a per-encounter allowance. It comes back only after the record expires entirely and is reallocated.

While the window is counting, a contact gap longer than `max(0.5 s, BaseUpdateInterval × 4)` resets it — so genuinely breaking away before the AI reacts costs it the whole timer, while a sense running on a slower interval missing a tick does not.

## Telegraphing

`Fairness → Telegraph Threshold` (default `0.25`)

Fires **On AI Telegraph** (`Target`, `Confidence`) once per target when confidence crosses this value — **before** the AI commits to full alert.

This is where a "huh?" bark, a head turn, a squint, or a detection-meter flicker goes. It is the single highest-value fairness feature in the plugin: it converts *"the AI spotted me out of nowhere"* into *"I saw it start to notice me and I chose wrong"*.

Put the threshold between `Suspect Threshold` and `Detect Threshold` so the warning genuinely precedes the commitment.

```
Event On AI Telegraph (Target, Confidence)
  ├─► Play Sound ("Hmm?")
  ├─► Set Focal Point (Target)          // head turns toward you
  └─► Show detection pip on HUD
```

## Off-screen hearing penalty

`Fairness → b Offscreen Hearing Penalty` + `Offscreen Hearing Multiplier` (0.75)

While an AI is off-screen, its hearing confidence is multiplied by `Offscreen Hearing Multiplier`.

The problem this solves: an AI the player has never seen reacting to a noise the player never saw it hear reads as the game cheating. Damping unseen AI keeps the causal chain visible.

**How "off-screen" is decided:** a dot-product test against player camera 0's forward vector — anything more than about **75°** off centre counts as off-screen. It is a cheap cone test, not a real frustum: it ignores distance, occlusion and aspect ratio, and only ever consults the first local player. On a dedicated server with no camera, nothing is treated as off-screen and the penalty never applies.

That is the right trade for a fairness softening rather than a visibility guarantee — but do not use it as a general "is this AI visible" signal.

## Never-search zones — guaranteed safe rooms

| Node | Purpose |
|---|---|
| **Register Never Search Zone** (`Center`, `Radius`) | Register a sphere as off-limits for searching |
| **Unregister Never Search Zone** (`Center`, `Tolerance`) | Remove the nearest zone within tolerance |
| **Clear Never Search Zones** | Remove all |
| **Is In Never Search Zone** (`Location`) *(subsystem)* | Test a location against all zones |
| **Is Location In Never Search Zone** (`Location`) *(component)* | Same test, but returns false when this AI's profile has `b Respect Never Search Zones` off |

> ⚠ **Zones are advisory — APS does not enforce them for you.** Registering a zone does not suppress perception, and nothing in the perception pipeline stops an AI walking into one. The plugin gives you the **query**; your Behavior Tree does the honouring. `b Respect Never Search Zones` only decides whether the per-AI query reports anything, so a profile with it switched off makes that AI ignore every zone.

This is the guarantee *Alien: Isolation* was built on: the player needs somewhere they are **certainly** safe, or the tension never releases and the game becomes exhausting instead of frightening.

**Register the zone:**

```
Safe room volume, Event Begin Play
  └─► Get APS Subsystem
        └─► Register Never Search Zone
              Center = Get Actor Location
              Radius = 600
```

**Then honour it in the search branch — this part is required:**

```
Event On AI Lost (Target, Last Known, Predicted, Last Cover Actor)
  └─► Is Location In Never Search Zone (Last Known)
        ├─ True  → do NOT set LastKnownPosition. Give up, return to patrol.
        └─ False → set the blackboard keys and search normally
```

Add the same check to any BT task that picks a search point, so an expanding sweep cannot wander in either.

Use it for: save rooms, lockers, vents, shops, hub areas, tutorial spaces, and anywhere a cutscene plays.

## Putting it together

A well-tuned stealth guard:

| Setting | Value | Effect |
|---|---|---|
| `First Spot Reaction Time` | 0.4 | You get a beat to duck back |
| `Telegraph Threshold` | 0.22 | You hear "hm?" before you are caught |
| `Suspect Threshold` | 0.18 | It starts investigating |
| `Detect Threshold` | 0.40 | Full alert |
| `Eye Turn Rate Deg Per Sec` | 180 | It cannot see you before it has turned |
| `b Offscreen Hearing Penalty` | ✅ | Unseen AI do not act on unseen information |
| `b Keyhole Vision` | ✅ | Distance protects you; proximity does not |

Every one of those makes the AI *weaker* on paper. Together they make it feel far more intelligent, because every detection is legible — the player can trace exactly what gave them away.

---

