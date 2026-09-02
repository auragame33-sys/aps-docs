# Sound System

APS never guesses that a sound happened. **You emit sounds explicitly**, using data assets that describe what kind of sound it is. This means your AI hears exactly what your game decides is audible — no phantom detections from a character's velocity, no surprises.

---

## The workflow

```
1. Create a Sound Type Definition asset per kind of sound
2. Call Emit Sound / Emit Sound At Location wherever that sound happens
3. (Optional) Give an archetype a Sound Filter Profile so it only hears some of them
```

---

## Step 1 — Sound Type Definitions

Content Browser → **Data Asset → SoundTypeDefinition**.

| Field | Meaning |
|---|---|
| `Sound Name` | Identifier passed to the `On AI Hear` event as `Sound Type Name`. **Also becomes part of the stimulus tag** — see below. Branch on it. |
| `Category` | `Enemy / Friendly / Animal / Environment / Custom` — used by sound filters |
| `Alert Level` | `Whisper / Normal / Loud / Explosive` — used by sound filters |
| `Base Loudness` | 1.0 = normal footstep, 3.0 = gunshot, 0.3 = whisper |
| `Max Range` | Detection range in cm. Nothing beyond this is even considered. |
| `b Is Directional` | True = the AI knows the exact direction. False = a vague heading only. |
| `Location Accuracy Override` | 0–1. `0` = use the default distance-based formula. `0.9` = very precise (gunshot). `0.2` = vague. |
| `Priority` | 0–10. Higher wins when the sound budget is full. Explosion 10, footstep 1. |
| `Max LOD Tier` | 0–4. Which distance tiers of AI process this sound. Footstep 1, gunshot 3, explosion 4. |
| `Max Pending Per Tick` | 1–10. Caps how many sounds of this type queue per AI per tick. |

### A starter set

| Asset | Category | Alert | Loudness | Range | Priority | LOD |
|---|---|---|---|---|---|---|
| `DA_Sound_Footstep` | Enemy | Normal | 1.0 | 800 | 1 | 1 |
| `DA_Sound_Sprint` | Enemy | Loud | 1.8 | 1600 | 3 | 2 |
| `DA_Sound_Crouch_Step` | Enemy | Whisper | 0.3 | 300 | 1 | 0 |
| `DA_Sound_Reload` | Enemy | Normal | 1.2 | 1000 | 4 | 1 |
| `DA_Sound_Gunshot` | Enemy | Loud | 3.0 | 4000 | 9 | 3 |
| `DA_Sound_Suppressed` | Enemy | Whisper | 0.6 | 900 | 5 | 1 |
| `DA_Sound_Explosion` | Environment | Explosive | 5.0 | 10000 | 10 | 4 |
| `DA_Sound_Glass_Break` | Environment | Loud | 2.0 | 2500 | 8 | 3 |
| `DA_Sound_Door` | Environment | Normal | 1.0 | 1200 | 4 | 2 |
| `DA_Sound_Thrown_Rock` | Environment | Normal | 1.4 | 1800 | 6 | 2 |
| `DA_Sound_Animal_Call` | Animal | Normal | 1.5 | 2000 | 3 | 2 |
| `DA_Sound_Radio_Chatter` | Friendly | Normal | 1.0 | 1500 | 2 | 1 |

---

## Step 2 — Emitting

Both nodes are static — no component reference required. Find them under `Perception | Sound`.

### Emit Sound

```
Emit Sound
  World Context : Self
  Source        : Self          (or any actor)
  Sound Type    : DA_Sound_Footstep
```

Use for anything attached to an actor. The sound originates at the actor's location, and the actor becomes the *target* the AI builds confidence toward.

### Emit Sound At Location

```
Emit Sound At Location
  World Context  : Self
  Sound Location : Hit Location
  Sound Type     : DA_Sound_Explosion
```

Use for sourceless sounds — explosions, traps, environmental triggers, thrown distractions. There is no target actor, so the AI investigates the *place*, not a person.

### ⚠ Two differences between the two nodes

**1. `Sound Name` doubles as a stimulus tag.** `Emit Sound` also broadcasts a stimulus event tagged `Stimulus.Sound.<Sound Name>`, which is how other senses intercept loud noises. The Vibration sense subscribes to `Stimulus.Sound.Explosion` — so **an explosion only shakes the ground for vibration-hunting AI if that asset's `Sound Name` field is literally `Explosion`.** Name the field carefully; it is not just a label.

**2. `Emit Sound At Location` does not emit a stimulus at all.** Only `Emit Sound` does. If you want an explosion to reach vibration senses, emit it from an actor — spawn a short-lived actor at the blast point if you have to — or call **Emit Stimulus** yourself alongside `Emit Sound At Location`.

Sourceless sounds also do not accumulate (accumulation is keyed on the source actor) and are evaluated against every candidate target rather than one specific actor.

### Where to call it

| Sound | Where |
|---|---|
| Footsteps | Anim Notify on the walk/run animation → `AnimNotify_Footstep` |
| Sprint footsteps | Same notify, branch on speed and pick the louder asset |
| Crouched steps | Same notify, branch on `Is Crouched` |
| Weapon fire | Your fire function, right after spawning the muzzle effect |
| Reload | Reload montage notify |
| Doors | The door's open/close event |
| Thrown objects | The projectile's `OnHit` — with `Emit Sound At Location` |
| Explosions | Wherever you call `Apply Radial Damage` |

> `Emit Sound` only feeds perception. Keep playing your actual audio however you normally do.

### A thrown-rock distraction in three nodes

```
Projectile OnComponentHit
  ├─► Spawn Sound At Location (your audio)
  └─► Emit Sound At Location (Hit Location, DA_Sound_Thrown_Rock)
```

Every guard in 1800 cm now investigates that spot. Classic stealth distraction, no extra systems.

---

## Step 3 — Sound Filter Profiles (optional)

Content Browser → **Data Asset → SoundFilterProfile**. Assign it in the perception profile at **Detection → Sound Filter**.

| Field | Meaning |
|---|---|
| `b Enabled` | False = hear everything, filters ignored |
| `Accepted Categories` | Categories this AI reacts to. **An empty list makes the AI completely deaf.** |
| `Min Alert Level` | `Whisper` = react to everything. `Loud` = only gunshots and above. `Explosive` = only explosions. |
| `Loudness Multiplier` | 1.0 normal, 2.0 sensitive ears (dog), 0.5 hard of hearing |
| `b Filter Friendly Team` | Ignore sounds from the same team (uses `IGenericTeamAgentInterface` on the AIController) |

### Useful filters

**`DA_Filter_Dog`** — Categories: all · Min Alert: `Whisper` · Loudness ×2.0
Hears the tiniest sound, including your crouched steps.

**`DA_Filter_HeavyArmor`** — Categories: Enemy, Environment · Min Alert: `Loud` · Loudness ×0.6
Deaf to footsteps and whispers. Only reacts to gunfire and explosions. Sneak past it easily; never sneak up on the dog.

**`DA_Filter_Civilian`** — Categories: Enemy, Environment · Min Alert: `Normal` · `b Filter Friendly Team` true
Hears trouble but ignores its own faction.

**`DA_Filter_Predator`** — Categories: Animal, Enemy · Min Alert: `Whisper` · Loudness ×1.5
Hunts by sound, ignores machinery and radio chatter.

---

## How a sound reaches an AI

Every emitted sound runs this pipeline per agent, cheapest checks first — so a footstep on the far side of the map costs almost nothing:

| # | Check | Skipped if |
|---|---|---|
| 1 | **Range** | Agent is beyond `Max Range` |
| 2 | **LOD tier** | Agent's LOD tier > `Max LOD Tier` |
| 3 | **Category** | Not in the filter's `Accepted Categories` |
| 4 | **Alert level** | Below the filter's `Min Alert Level` |
| 5 | **Team** | Same team as source and `b Filter Friendly Team` is on |
| 6 | **Wall trace** | Only runs for sounds that survived everything above |

Sounds that get through are attenuated by distance and, if the path was blocked, by a single `exp(−Wall Absorption Coeff)` penalty — about 0.67× at the default. The check is **binary**: one wall and five walls attenuate identically. Loudness is multiplied by the filter's `Loudness Multiplier` before evaluation.

The occlusion trace runs on `ECC_Visibility` from the sound origin to the AI's actor location + 64 cm.

---

## Accumulation — one footstep is not a detection

Hearing builds over time. A single distant footstep produces a blip; a series in the same area builds toward `Suspected` and then `Detected`.

| Profile setting | Effect |
|---|---|
| `Sound Accumulation Rate` (0.5) | How fast repeated sounds build confidence |
| `Sound Accumulation Hold Time` (1.0 s) | Silence tolerated before decay begins |
| `Sound Accumulation Decay Rate` (0.2) | How fast it fades once decay starts |

The reported confidence is `max(instant, accumulated)`, so accumulation can only ever raise the value, never suppress a loud one-off.

**Design consequence:** a player who moves in short bursts, pausing longer than `Hold Time`, keeps the accumulator draining and stays under `Suspect Threshold`. A player who runs continuously builds past it. That is the core stealth loop and you tune it with these three numbers plus your `Awareness` thresholds.

> `Hearing Base Threshold` is not read by any code path in v3.0 — there is no noise floor. Use `Suspect Threshold` and the sound filter's `Min Alert Level` instead.

---

## Reading the result

```
Event On AI Hear (Location, Loudness, Sound Type Name)
  └─► Switch on Name (Sound Type Name)
        ├─ "Gunshot"  → Broadcast Alert To Squad, sprint to Location
        ├─ "Footstep" → walk to Location, look around
        └─ Default    → turn to face Location
```

`Location` is where the AI *thinks* the sound came from — already degraded by `Location Accuracy Override` and `b Is Directional`. A vague sound gives a vague position, which is exactly what you want.

---

## Troubleshooting

| Problem | Cause |
|---|---|
| AI hears nothing at all | `Hearing Sense` missing from `Sense Classes`, or you never call `Emit Sound` |
| AI hears nothing from one sound type | `Max Range` too small, or the filter rejects its category / alert level |
| Distant AI ignore an important sound | Raise the sound's `Max LOD Tier` — explosions should be 4 |
| AI hears through solid walls | Raise `Wall Absorption Coeff`; check your walls actually block `ECC_Visibility` |
| Walls barely muffle anything | The penalty is binary and capped at `exp(−coeff)`. At 0.4 that is only a 33% cut. Raise the coefficient to 1.5+ for a real difference. |
| AI reacts to every single footstep instantly | Lower `Sound Accumulation Rate`, raise `Suspect Threshold`, or give the archetype a filter with a higher `Min Alert Level` |
| Explosions don't reach vibration-based AI | The sound asset's `Sound Name` must be `Explosion`, and you must use `Emit Sound` (not `Emit Sound At Location`) |
| Sound filter makes AI totally deaf | `Accepted Categories` is empty — that means *nothing*, not *everything* |

---

