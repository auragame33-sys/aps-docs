# Migrating from AIPerception

<div class="aps-meta" markdown>

**For:** anyone with a working `AIPerception` setup to move across · **Time:** 20 to 40 minutes for a typical guard · **Risk:** low, the two systems run side by side

</div>

---

## You do not have to switch all at once

APS does not disable, replace or interfere with `AIPerception`. Both components can live on the same actor and both will fire their events. The sane migration is:

1. Add APS alongside your existing setup.
2. Move **one** behaviour across (usually sight).
3. Confirm it behaves, then unbind the Epic equivalent.
4. Repeat for hearing, damage, and so on.
5. Remove the `AIPerception` component when nothing is bound to it.

---

## Concept mapping

| Epic `AIPerception` | APS equivalent |
|---|---|
| `AIPerception` component | **APS Core** component |
| `AISenseConfig_Sight` | `Vision Sense` in the profile's `Sense Classes` + the Detection sections |
| `AISenseConfig_Hearing` | `Hearing Sense` + **Sound Type Definition** assets |
| `AISenseConfig_Damage` | `Damage Sense` (auto-wires all UE damage events) |
| `AISenseConfig_Touch` | `Sense: Touch` (auto-wires collisions) |
| `AISenseConfig_Prediction` | `b Enable Prediction` in the **Spatial** section |
| `AISenseConfig_Team` | Squad system — `Set Squad ID` + `Share Target With Squad` |
| Sight Radius | `Vision Max Range` |
| Lose Sight Radius | `Vision Loss → Grace Time` + `Default Decay Exponent` (see below) |
| Peripheral Vision Half Angle | `Vision Half Angle Deg` (plus a real peripheral cone if you want one) |
| Auto Success Range From Last Seen | No direct equivalent — use `Min Exposure To Register` and the cones |
| Detection by Affiliation | **APS Relationship** component + `Team Relationships` |
| Max Age | `Default Decay Exponent`, `Memory Expire Threshold`, `Min Time In Lost` |
| `OnPerceptionUpdated` | `On Target State Changed`, or the individual lifecycle events |
| `OnTargetPerceptionUpdated` | `On AI Detect` / `On AI Lost` |
| `GetCurrentlyPerceivedActors` | `Get Targets Sorted By Score` |
| `GetActorsPerception` | `Get Belief Data` |
| `RequestStimuliListenerUpdate` | Not needed — APS runs on its own interval |
| `UAISense_Hearing::ReportNoiseEvent` | `Emit Sound` / `Emit Sound At Location` |
| `UAISense_Damage::ReportDamageEvent` | Nothing — damage is auto-wired |
| Gameplay Debugger category | `Debug Settings → b Enabled`, 7 modes |

---

## Step-by-step port

### 1. Create a profile from your existing sight config

Content Browser → **Data Asset → PerceptionProfile** → `DA_Profile_<YourAI>`.

Copy your Epic values across:

| From `AISenseConfig_Sight` | To profile |
|---|---|
| Sight Radius | `Ranges → Vision Max Range` |
| Peripheral Vision Half Angle Degrees | `Detection → Vision Half Angle Deg` |
| Lose Sight Radius | *(see "What has no direct equivalent")* |
| Detection by Affiliation | Add an **APS Relationship** component instead |

Everything else already has a working default.

### 2. Add the components

On the AI actor:

- **APS Core** → assign the profile
- **APS Perception Listener** (optional but easiest for events)

Leave `AIPerception` in place for now.

### 3. Move sight events across

Wherever you handle `OnTargetPerceptionUpdated` and check `Stimulus.WasSuccessfullySensed()`:

```
BEFORE
  On Target Perception Updated (Actor, Stimulus)
    └─► Branch: Stimulus.Was Successfully Sensed
          True  → SetTarget(Actor)
          False → ClearTarget()

AFTER
  Event On AI Detect (Target, Threat Level, Stimulus)  →  SetTarget(Target)
  Event On AI Lost   (Target, Last Known, …)           →  begin search
  Event On AI Forget (Target)                          →  ClearTarget()
```

Note this is already an upgrade: Epic gives you one boolean flip, APS gives you *detected*, *lost with a reason and a last known position*, and *finally gave up* as three separate moments.

### 4. Move hearing across

Every `Report Noise Event` call becomes an `Emit Sound` call with a Sound Type Definition:

```
BEFORE  Report Noise Event (Location, Loudness: 1.0, Instigator, MaxRange: 800)
AFTER   Emit Sound (Source: Self, Sound Type: DA_Sound_Footstep)
```

Put loudness, range, category, alert level, priority and LOD tier on the **asset**, not the call site. You then tune every footstep in the game from one place.

### 5. Delete the old component

Once nothing is bound to `AIPerception`, remove it. Nothing in APS depends on it.

---

## What has no direct equivalent (and why)

### Lose Sight Radius

Epic uses a second, larger radius: you're seen inside `Sight Radius` and unseen outside `Lose Sight Radius`. APS has no such concept because it does not model detection as a boolean.

Instead, losing a target is governed by:

| Setting | Role |
|---|---|
| `Vision Loss → Grace Time` (0.3) | Seconds of no signal before the AI drops you |
| `Vision Loss → Confidence Decay Multiplier` (3.0) | How fast belief falls once it does |
| `Default Decay Exponent` (0.3) | Base decay rate |
| `Min Time In Lost` (0.0) | Minimum search time before giving up |

**Practical translation:** if your `Lose Sight Radius` was much larger than `Sight Radius` — meaning "keep tracking well after they've left" — raise `Vision Loss → Grace Time` to 1.0–1.5 and set `Min Time In Lost` to 5–10.

### Auto Success Range From Last Seen Location

Epic's "always succeed within this range of where I last saw them" is a workaround for its single-trace visibility. APS does not need it: partial exposure produces partial confidence, so a target half behind cover is already handled continuously.

### Max Age

Epic ages stimuli out on a fixed timer. APS decays belief on a curve and expires the slot when confidence falls below `Memory Expire Threshold`. If you want a hard timer, `Min Time In Lost` plus a steep `Default Decay Exponent` approximates it.

### Dominant Sense

Epic lets one sense override another's location. APS fuses instead: the strongest active sense sets the confidence floor, and `Last Known Position` comes from whichever active sense has the highest **Location Accuracy**. A precise gunshot beats a vague scent automatically, with no configuration.

---

## What changes behaviourally

Expect these differences the first time you play:

| You will notice | Because |
|---|---|
| Detection is no longer instant | Confidence accumulates. Raise `Confidence Rise Rate` if you want Epic's snap. |
| The AI keeps looking where you were | `Vision Loss → Grace Time`. Lower it to 0.1 for Epic-like instant loss. |
| Partial cover now matters | Multi-point visibility. Set `Vision Sample Count` to 1 for Epic-equivalent binary sight. |
| The AI no longer sees through doors | If you added occlusion channels. This is the fix people want most. |
| The cone lags the body | Only if you set `Eye Turn Rate Deg Per Sec`. `0` restores Epic's instant snapping. |
| Events fire more often | Sense events fire every tick a sense is active. Use lifecycle events for one-shot reactions. |

### Making APS behave exactly like Epic

If you want a strict baseline before tuning, this profile is close to `AIPerception`:

| Setting | Value |
|---|---|
| `Sense Classes` | Vision, Hearing only |
| `Vision Sample Count` | `1` |
| `Eye Direction Mode` | `Control Rotation` |
| `Eye Turn Rate Deg Per Sec` | `0` |
| `Confidence Rise Rate` | `10.0` |
| `Suspect / Detect / Track` | `0.05 / 0.10 / 0.15` |
| `Vision Loss → Grace Time` | `0.0` |
| `b Use Per Target Light` | ❌ |
| `Corroboration Bonus` | `0.0` |
| `b Enable Prediction` | ❌ |
| All emotion `Max` values | `0.0` |

Start there, confirm parity, then turn features on one at a time. That way any behaviour change is traceable to a single setting.

!!! warning
    With an APS Target Component on the target, `Vision Sample Count` is ignored. Trim that component's `Visibility Samples` to one entry instead, or leave the component off while establishing parity.

---

## Migration checklist

- [ ] Profile created, `Vision Max Range` and `Vision Half Angle Deg` copied over
- [ ] **APS Core** added and profile assigned
- [ ] **APS Perception Listener** added
- [ ] Sight events moved to `On AI Detect` / `On AI Lost` / `On AI Forget`
- [ ] `Report Noise Event` calls replaced with `Emit Sound`
- [ ] Sound Type Definition assets created for each noise kind
- [ ] Affiliation replaced with an **APS Relationship** component
- [ ] `AIPerception` component removed
- [ ] `Debug Settings → b Enabled` used to confirm cones and confidence look right
- [ ] Occlusion channels added — the reason most people migrate in the first place

---

