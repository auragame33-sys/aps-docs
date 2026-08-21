# Troubleshooting & FAQ

**Start here when something is wrong.** Symptoms first, causes second — plus the five settings that are inert in v2.0.

---

## Nothing works at all

**Check these five things first. One of them is almost always the answer.**

1. **Is `Profile` assigned on the Perception Core component?** With no profile, `Begin Play` skips sense creation entirely and the AI perceives nothing, silently.
2. **Is `Sense Classes` non-empty on the profile?** An empty array means no senses. A brand-new profile ships with Vision and Hearing, so this only happens if you cleared it.
3. **Are you testing in Play mode?** Perception does not run in the editor viewport (only the debug cone preview does).
4. **Are you on a client?** Perception is server-only. In PIE with multiple clients, test on the server window.
5. **Turn on `Debug Settings → b Enabled`** and look at the Sense debug mode. It tells you immediately whether any sense is producing a value.

---

## Detection problems

### The AI never detects me

| Cause | Fix |
|---|---|
| No profile assigned | Assign one |
| `Sense Classes` empty | Add Vision (and Hearing) |
| Target out of range | Raise `Vision Max Range` |
| Target outside the cone | Raise `Vision Half Angle Deg`, or check `Eye Direction Mode` — if it is `Socket Rotation` with a bad socket, the cone may be pointing at the sky |
| Thresholds too high | Lower `Suspect Threshold` / `Detect Threshold` |
| Confidence rises too slowly | Raise `Confidence Rise Rate` |
| Fully occluded | Turn on `b Vision Cone` debug and look at the geometry |
| Target shares the observer's controller | Targets possessed by the same controller are skipped by design |
| `Min Exposure To Register` too high | Set it back to 0 |
| `Min Visible Points` too high for the stance | Set all three to 1 |
| Pain has suppressed the sense | Check the Environment debug mode's pain readout |

### The AI detects me instantly from anywhere

| Cause | Fix |
|---|---|
| A sound type's `Max Range` is enormous | Check the emitting sound asset |
| Damage auto-confidence | Set `b Auto Confidence From Damage` to false and handle it yourself |
| Thresholds too low | Raise `Suspect` / `Detect` |
| `Confidence Rise Rate` too high | Lower it |
| Echolocation is in `Sense Classes` | It has no line-of-sight requirement — remove it or reduce `Echo Range` |
| Vibration is in `Sense Classes` | It passes through walls — raise `Vibration Min Speed` or reduce the range |

Use the **Sense** debug mode to see which sense is spiking. It is almost always Hearing or Vibration.

### My light-gem override is ignored

`Light Level Override` on the APS Target Component is only consulted when the observing AI's profile has **`b Use Per Target Light`** on. With it off, the whole per-target light path is skipped and global ambient is used.

### The AI is much worse at perceiving when wounded, and I never asked for that

The Pain sense reads health automatically. It scans the owner's components for `GetHealthPercent()`, or `GetHealth()` + `GetMaxHealth()`, or `GetCurrentHealth()` + `GetMaxHealth()`, and degrades **all** senses in proportion — non-vision senses have a floor of 0, so at 50% health they run at roughly half strength.

Either remove `Sense: Pain / Health` from `Sense Classes`, or rename your accessor functions so they are not picked up. See [Pain & Damage](pain-and-damage.md).

### The AI sees through walls

1. Add your wall's collision channel to `Vision Occlusion Channels`. Empty means `Visibility` only.
2. Confirm the walls actually block that channel in their collision settings.
3. Check `Surface Vision Transmission` — a surface mapped to `1.0` is **fully transparent**.
4. Confirm the sense doing the detecting is Vision. Vibration and Echolocation *are supposed to* pass through walls.

### The AI sees me the instant I enter its cone

That is Epic's behaviour, and APS gives you three ways to soften it:

- `Fairness → First Spot Reaction Time` = 0.3–0.5
- Lower `Confidence Rise Rate`
- Enable `b Keyhole Vision` so distance protects you

### The cone points at the sky / the ground

`Eye Direction Mode` is `Socket Rotation` and the socket's local axes are non-standard. Set `Eye Socket Alignment` to **Automatic** — it derives the correction from the skeleton's reference pose and works with a raw bone name on any rig.

### The AI sees me before it has turned to face me

`Eye Turn Rate Deg Per Sec` is `0` (instant). Set it near your mesh's real turn rate — 180–300 for a humanoid.

---

## Hearing problems

### The AI hears nothing

**Hearing is event-driven. You must call `Emit Sound`.** There is no passive hearing.

Then check:
- `Hearing Sense` is in `Sense Classes`
- The sound type's `Max Range` covers the distance
- A `Sound Filter Profile` is not rejecting the category or alert level
- **`Accepted Categories` is not empty** — empty means *deaf*, not *hears everything*
- The AI's LOD tier is not above the sound's `Max LOD Tier`

### Distant AI ignore explosions

Raise that sound asset's `Max LOD Tier` to 4. Explosions should reach everyone.

### Explosions don't reach my vibration-based AI

Two requirements, both easy to miss:

1. The sound asset's **`Sound Name` must be exactly `Explosion`** — the stimulus tag is built as `Stimulus.Sound.<Sound Name>`, and Vibration subscribes to `Stimulus.Sound.Explosion`.
2. You must use **`Emit Sound`** with a source actor. `Emit Sound At Location` does not emit a stimulus at all.

### Smell ignores my wind direction

`Set Wind State` on the subsystem controls wind *speed* (which dampens scent globally) but not the direction used for the upwind/downwind bonus. That comes from the `Wind Direction` property on the sense itself — set it as a class default on a Blueprint subclass of `SenseUnit_Smell`. See [The Senses](senses.md).

### The AI reacts to every footstep instantly

Raise `Hearing Base Threshold`, lower `Sound Accumulation Rate`, or give the archetype a filter with a higher `Min Alert Level`.

---

## Memory and search problems

### The AI forgets me instantly

Raise `Vision Loss → Grace Time` (try 0.8–1.5), lower `Default Decay Exponent`, and raise `Min Time In Lost`.

### The AI never forgets me

Raise `Default Decay Exponent`, raise `Memory Expire Threshold`, and lower `Min Time In Lost`.

### The AI searches in a stupid circle

You are not reading `Get Loss Reason`. See [Behavior Trees](behavior-trees.md) — that one branch is the whole difference.

### `Predicted Position` is always the same as `Last Known Position`

`b Enable Prediction` is off. It is off by default because on a slow patrolling guard, prediction reads as psychic.

### `Uncertainty Radius` is always 0

`b Enable Spatial Model` is off, or the target has not been lost yet — the radius only grows while lost.

### AI walk straight into my safe room

Never-search zones are **advisory**. Registering one does not stop anything by itself — you must call `Is Location In Never Search Zone` in your Behavior Tree and skip the search. See [Environment & Fairness](environment-and-fairness.md).

---

## Settings that appear to do nothing

Five profile properties are not read by any code path in v2.0. They are visible in the editor but changing them has no effect:

| Setting | Use instead |
|---|---|
| `Hearing Base Threshold` | `Suspect Threshold`, or the sound filter's `Min Alert Level` |
| `b Sound Event Only Mode` | Nothing needed — hearing is always event-only |
| `Touch Confidence` | The `Strength` argument on `Report Touch Contact`, or `Contact Type Strength Multiplier` on the sense |
| `Confidence Decay Smoothing` | The per-sense `Confidence Decay Multiplier` in the **Loss** section |
| `Confidence Reduce Delay` | Per-sense `Grace Time` in the **Loss** section |

Two more behave differently than their names suggest:

- **`Vision Sample Count`** only limits the built-in fallback sample set. Targets with an APS Target Component always use that component's samples — five by default. See [Performance](performance.md).
- **`b Respect Never Search Zones`** gates the query, not the behaviour. See above.

---

## Event problems

### My event never fires

1. Debug Mode → **Delegates**. Did the event fire at all?
2. **It fired** → your binding is wrong, or you bound to a different component instance. If you are using the Listener component, confirm it is on the **same actor** as the Perception Core.
3. **It did not fire** → the transition never happened. Go to **Sense** mode and check confidence.

### `On AI Lost` fires immediately after `On AI Detect`

Confidence is hovering right at a threshold. Raise the gap between `Detect Threshold` and `Suspect Threshold`, raise `Vision Loss → Grace Time`, or raise `Confidence Reduce Delay`.

### `On AI Detect` fires repeatedly for the same target

It should not — lifecycle events fire once per transition. If you see repeats, the target is oscillating across a threshold. Widen the gap between thresholds and raise `Confidence Reduce Delay`.

### I can't find `On AI Lost` when binding

The component delegate is exposed as **On AILost Event** to avoid a name clash. The Listener component's version is **On AI Lost**. Same moment, same parameters.

---

## Squad problems

### Squad sharing does nothing

Run **Debug Trace Squad Share Path** (`Sender`, `Target`). It checks every gate in order and prints the exact failure point.

Common causes: `Set Squad ID` never called · IDs do not match exactly (they are case-sensitive `Name`s) · squadmates beyond `Squad Share Range` · threat below `Min Threat To Share` · both auto-share flags off.

### The whole squad detects me the instant one does

That is `b Auto Share On Detect` working as designed. For tactical AI, turn both auto-share flags off and share manually after a call-out animation. Also branch on `Stimulus == Shared Intel` so receivers behave cautiously.

### `Request Combat Role` always returns false

A squadmate already holds it, or the role is not in the profile's `Eligible Roles`. Also make sure you call `Release Combat Role` when an AI dies or loses its target — otherwise dead AI hold roles forever.

---

## Multiplayer problems

### Clients see nothing

- `b Replicate Perception State` is off
- You are reading `Replicated Targets` directly instead of **Get Replicated Perception State**
- The component is on an AIController — use `Get Replicated Perception State`, which resolves the relay automatically

### `Emit Sound` does nothing in multiplayer

It was called on a client. Sound emission must run on the server — gate it with `Has Authority` or route it through a server RPC.

---

## Performance problems

### The frame rate drops with many AI

In order: raise `Base Update Interval` · lower `Vision Sample Count` to 3 · lower `Max Tracked Targets` · reduce `Vision Occlusion Channels` to one · turn off `b Use Per Target Light` on background AI · adopt the two-profile near/far swap from [Performance](performance.md).

### Is it actually APS?

Set `Debug Settings → b Pause Perception` on every AI. If the frame rate does not improve, the bottleneck is elsewhere.

---

## Editor / build problems

### The plugin does not appear

- The `APS` folder must be at `YourProject/Plugins/APS/`, with `APS.uplugin` directly inside it
- Enable it in **Edit → Plugins** and restart
- On a Blueprint-only project, accept the prompt to build the module

### Compile errors after copying the plugin

Delete `Binaries/` and `Intermediate/` from both the project and the plugin folder, then regenerate project files and rebuild.

### Debug drawing does not appear in a packaged build

Correct and by design. All debug rendering is compiled out of Shipping builds. Use a Development build to see it.

---

# FAQ

**Can I use APS alongside Epic's AIPerception?**
Yes. APS does not touch or disable it. Run both while you migrate.

**Do I need C++?**
No. Everything in this documentation is Blueprint. C++ is only needed for advanced custom senses that must override loss behaviour, sensing range, or the stimulus bus.

**Does it work on a Blueprint-only project?**
Yes — the plugin ships its own compiled module.

**Does it need a Behavior Tree?**
No. APS reports belief; you can consume it from a Blueprint state machine, a BT, or plain event graphs.

**Can I change perception at runtime?**
Yes — **Set Profile** swaps everything instantly. Use it for alert states, difficulty, buffs, or transformations.

**Can one AI have two vision cones?**
Yes, three: focal, peripheral and rear-motion. For something more exotic, add two Vision-derived Blueprint senses with different defaults.

**How many AI can it handle?**
See [Performance](performance.md). Defaults are comfortable to ~30; with tuning and the near/far profile swap, several hundred.

**Does perception run on clients?**
No — server only. An opt-in replicated summary exists for client UI.

**Where is the player behaviour data saved?**
`YourProject/Saved/APS/PlayerModel/` as plain JSON, one file per AI class per target.

**Can I disable a sense at runtime?**
Not individually. Swap to a profile without that sense using **Set Profile**, or use the Pain system to suppress it to zero — which is often what you actually want.

**Does it support GAS / Lyra / ALS?**
There is no coupling to any of them. APS is a perception component that reads actor positions and traces geometry, so it composes with anything.

**Why does `Get Active Target Count` differ from what I expect?**
It counts targets the AI is currently *aware of*. The internal ledger's occupancy can briefly be higher between maintenance passes, but the Blueprint-facing count is the meaningful one.

**Can AI perceive non-Pawn actors?**
Yes — call **Register Perceivable Actor**, or add an **APS Target Component** with auto-register on. Pawns are found automatically.

**Is the source included?**
Yes — full C++ source ships with the plugin.

---

