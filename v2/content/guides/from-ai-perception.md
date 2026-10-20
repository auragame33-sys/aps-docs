---
title: Coming from AI Perception
description: Move an Unreal AI Perception setup to APS one behaviour at a time - what maps to what, a step-by-step port, what has no direct equivalent and why, and a profile that behaves like AI Perception to start from.
local: DA_Profile_YourAI, DA_Sound_Footstep
---
<div class="kicker">Guide</div>

# Coming from AI Perception

APS runs beside Unreal's AI Perception, so you can move across one behaviour at a time. A typical guard takes 20 to 40 minutes.

::: fast
![Room W1: the same thief, two guards](media/why/dark.mp4 "Room W1, In the Dark. The same thief walks the same dark path past two guards. APS: he slipped by. Unreal AI Perception: caught in the dark, because it ignores light.")
- Add an **APS Core** to the AI's **Pawn**, give it a profile, and leave AI Perception where it is.
- Move sight first: **On Target Perception Updated** becomes **On AI Detect**, **On AI Lost** and **On AI Forget**.
- **Report Noise Event** becomes **Emit Sound** with a Sound Type asset. Damage needs nothing: it's wired automatically.
:::

## One behaviour at a time

APS doesn't disable or change AI Perception; both can run and both fire their events.

1. Add APS beside your setup.
2. Move **one** behaviour (usually sight).
3. Check it, then unbind the AI Perception version.
4. Repeat for hearing, damage and the rest.
5. Remove the AI Perception component once nothing is bound to it.

::: info The APS Core goes on the Pawn
AI Perception usually lives on the AI Controller. The **APS Core** must be on the **Pawn or Character** it perceives for: it looks out from that body and feels its hits. On a controller it refuses to run and says so in the log.
:::

## What maps to what

| AI Perception | APS |
|---|---|
| AI Perception component | **APS Core** component, on the Pawn |
| Sight config | **Vision Sense** in `Sense Classes`, and the profile's Detection settings |
| Hearing config | **Hearing Sense**, and a **Sound Type Definition** per kind of noise |
| Damage config | **Damage Sense**: every Unreal damage call, no reporting needed |
| Touch config | **Touch Sense**: hits and overlaps are wired automatically |
| Prediction config | `Enable Prediction` (Spatial) |
| Team config | Squads: **Set Squad ID** and **Share Target with Squad** |
| Sight Radius | `Vision Max Range` |
| Lose Sight Radius | `Vision Loss` grace time and how belief fades (below) |
| Peripheral Vision Half Angle | `Vision Half Angle Deg`, plus a real side cone if you want one |
| Detection by Affiliation | The **APS Relationship** component |
| Max Age | How belief fades: `Default Decay Exponent`, `Memory Expire Threshold`, `Min Time in Lost` |
| On Perception Updated | **On Target State Changed**, or the separate state events |
| On Target Perception Updated | **On AI Detect**, **On AI Lost** |
| Get Currently Perceived Actors | **Get Targets Sorted by Score**, keeping the states you count as perceived (Detected and Tracked, say): it lists everyone it holds a slot for, including targets not noticed yet, Lost or Remembered |
| Get Actors Perception | **Get Belief Data** |
| Request Stimuli Listener Update | Not needed: APS updates on its own interval |
| Report Noise Event | **Emit Sound**, **Emit Sound at Location** |
| Report Damage Event | Nothing: damage is automatic |
| Gameplay Debugger's perception page | `Show Visualizer` on the APS Core ([Visualizer](../features/visualizer.md)) |

## The port, step by step

**1. A profile from your sight settings.** Content Browser › Miscellaneous › Data Asset › **Perception Profile** (DA_Profile_YourAI). Copy Sight Radius to `Vision Max Range` and Peripheral Vision Half Angle to `Vision Half Angle Deg`; replace Detection by Affiliation with an **APS Relationship** component. Everything else has a working default.

**2. Add the component.** On the AI's Pawn: **APS Core**, with the profile. Its events are on the component (select it, Details › Events, **+**); for reactions several AI share, use an **APS Perception Listener** Blueprint ([Getting started](../getting-started.md)). Leave AI Perception in place for now.

**3. Move sight across.**

```
BEFORE
  On Target Perception Updated (Actor, Stimulus)
    └─► Branch: Stimulus › Successfully Sensed
          True  → set the target
          False → clear the target

AFTER
  On AI Detect (Target, Threat Level, Stimulus) → set the target
  On AI Lost (Target, Last Known, …)            → start searching
  On AI Forget (Target)                         → clear the target
```

That is already an upgrade: one true/false flip becomes three moments: *it has you*, *it lost you (with a reason and a last known position)*, and *it gave up*.

**4. Move hearing across.**

```
BEFORE  Report Noise Event (Location, Loudness 1, Instigator, Max Range 800)
AFTER   Emit Sound (Source: Self, Sound Type: DA_Sound_Footstep)
```

Loudness, range and how alarming it is live on the **asset**, not the call: tune every footstep in the game from one place. [Hearing](../features/hearing.md)

**5. Remove the old component** once nothing is bound to it. Nothing in APS depends on it.

## What has no direct equivalent

![Room W2: a head over a wall](media/why/head.mp4 "Room W2, Head Above the Wall. The thief hides with his head showing over a wall. APS saw his head (one of five points). Unreal AI Perception, tracing to the body's centre, never saw him.")

**Lose Sight Radius.** AI Perception sees you inside one radius and loses you outside a larger one. APS isn't true/false, so it has no second radius. Losing you is governed by:

| Setting | Default | Role |
|---|---|---|
| `Vision Loss` › Grace Time | 0.3 | Seconds with no sight before it drops you |
| `Vision Loss` › Confidence Decay Multiplier | 3 | How fast belief falls after that |
| `Default Decay Exponent` | 0.3 | The base fade |
| `Min Time in Lost` | 0 | The least time it searches before giving up |

If your Lose Sight Radius was much bigger than Sight Radius ("keep tracking after they've gone"), raise the grace time to 1 to 1.5 s and `Min Time in Lost` to 5 to 10.

**Auto Success Range from Last Seen Location.** A workaround for AI Perception's single trace. APS doesn't need it: partial cover gives partial confidence, all the time.

**Max Age.** AI Perception ages stimuli out on a timer; APS fades belief and frees the slot when confidence drops below `Memory Expire Threshold`. For a hard timer, use `Min Time in Lost` with a steep `Default Decay Exponent`.

**Dominant Sense.** AI Perception lets one sense override another's location. APS combines them: the strongest sense sets the confidence, and the **position** comes from whichever active sense places the target most precisely. A gunshot beats a vague scent with no configuration.

![Room W3: he hid](media/why/hid.mp4 "Room W3, He Hid. The thief ducks behind a crate. The APS guard remembers where and why it lost him and searches that cover: found him. The Unreal guard goes back to its post: he got away.")

## What feels different

| You'll notice | Because | To change it |
|---|---|---|
| Detection isn't instant | Confidence builds | Raise `Confidence Rise Rate` |
| It keeps looking where you were | The vision grace time | Lower `Vision Loss` grace to 0.1 |
| Partial cover matters | Five points per target | See the parity profile below |
| It no longer sees through doors | If you set occlusion channels | The fix most people came for |
| The cone lags the body | Only with `Eye Turn Rate Deg Per Sec` above 0 | 0 snaps instantly |
| Sense events fire a lot | **On AI See** and the other sense events fire each time a sense reports | Use the state events (**On AI Detect** and the rest) for one-off reactions |

### A profile that behaves like AI Perception

For a strict baseline before tuning, start close to AI Perception, check parity, then turn features on one at a time, so any change in behaviour traces to one setting:

| Setting | Value |
|---|---|
| `Sense Classes` | Vision Sense and Hearing Sense only |
| `Vision Sample Count` | 1 |
| `Eye Direction Mode` | Control Rotation |
| `Eye Turn Rate Deg Per Sec` | 0 |
| `Confidence Rise Rate` | 10 |
| `Suspect Threshold`, `Detect Threshold`, `Track Threshold` | 0.05, 0.10, 0.15 |
| `Telegraph Threshold` | 0.08 (keep it between Suspect and Detect) |
| `Vision Loss` › Grace Time | 0 |
| `Use Per Target Light` | Off |
| `Corroboration Bonus` | 0 |
| `Enable Prediction` | Off |
| `Max Fear`, `Max Aggression`, `Max Curiosity`, `Max Alertness`, `Max Panic` | 0 |

::: warn A Target Component overrides Vision Sample Count
With an **APS Target Component** on the target, its own `Visibility Samples` are used and `Vision Sample Count` is ignored. Trim that list to one entry, or leave the component off, while you check parity.
:::

## Checklist

- A profile, with `Vision Max Range` and `Vision Half Angle Deg` copied over
- **APS Core** on the Pawn, profile assigned
- Sight moved to **On AI Detect**, **On AI Lost**, **On AI Forget**
- **Report Noise Event** replaced with **Emit Sound**, a Sound Type for each kind of noise
- Affiliation replaced with **APS Relationship**
- `Show Visualizer` used to check the cones and confidence
- Occlusion channels set: the reason most people move
- AI Perception removed
