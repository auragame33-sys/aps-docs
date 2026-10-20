---
title: Confidence
description: How sure your AI is of each target, from 0 to 100%, and everything that changes it - distance, light, cover, stance, the vision cones, see-through surfaces, fog and fair spotting.
---
<div class="kicker">Pillar 1 of 4</div>

# Confidence

How sure your AI is that you're there, from 0 to 100%. Never just "seen" or "not seen".

<div class="meta"><span>Works out of the box</span><span>Every setting on the <b>Perception Profile</b></span><span>Demo: the hub's Meter, Sight wing <b>S1 to S9</b></span></div>

::: fast
![The hub's Meter: a guard growing sure of the player, then losing them](media/confidence/meter.mp4 "The hub's Meter. In the open the guard grows sure of you (89%). Step behind the wall and its belief fades back to 0%.")
- Every AI holds a **confidence from 0 to 100%** for each thing it perceives.
- It climbs while the AI can see you and fades when it can't. **Distance, light, cover, stance**, the angle and the weather all count.
- At set points your Blueprint gets an event: **Suspected** at 15%, **Detected** at 35%, **Tracked** at 60%.
:::

## Seven states, one event each

As confidence rises and falls, the AI moves through seven states. Each step fires a Blueprint event, so your AI reacts in stages instead of all at once.

<div class="states">
<div class="states-row"><div class="states-label">Confidence rises</div>
<div class="state"><i style="background:#5b6878"></i><b>Undetected</b><span>Nothing yet</span><div class="pct">below 15%</div></div>
<div class="state"><i style="background:#f4d27a"></i><b>Suspected</b><span>"What was that?"</span><div class="pct">15%</div></div>
<div class="state"><i style="background:#ffb454"></i><b>Detected</b><span>"There you are."</span><div class="pct">35%</div></div>
<div class="state"><i style="background:#ff6b5e"></i><b>Tracked</b><span>Full chase</span><div class="pct">60%, held</div></div>
</div>
<div class="states-row fall"><div class="states-label">Confidence falls: it loses you</div>
<div class="state"><i style="background:#a78bfa"></i><b>Lost</b><span>Searches, and knows why it lost you</span><div class="pct">senses silent</div></div>
<div class="state"><i style="background:#64a8ff"></i><b>Remembered</b><span>Stays alert near where you were</span><div class="pct">fading</div></div>
<div class="state"><i style="background:#3a4656"></i><b>Expired</b><span>Forgotten</span><div class="pct">memory gone</div></div>
</div>
</div>

| State | Event | A typical reaction |
|---|---|---|
| Suspected | **On AI Suspect** | Turn the head, a "Hm?" bark, walk over slowly |
| Detected | **On AI Detect** | Alert, call it out, take cover |
| Tracked | **On AI Track** | Chase, shoot, flank |
| Lost | **On AI Lost** | Search: read **Get Loss Reason** to choose how |
| Remembered | **On AI Remember** | Patrol near the last known spot |
| Expired | **On AI Forget** | Back to normal |

The 15, 35 and 60% lines are the profile's `Suspect Threshold`, `Detect Threshold` and `Track Threshold`. A jumpy civilian and a calm soldier can run the same Blueprint with different numbers.

## What changes it

Everything vision checks is multiplied together. If any one thing is zero (too far, outside the cone, fully behind cover), the AI doesn't see you at all. Each clip below is the real demo room: the result card shows what the guard was sure of.

### Distance

![Room S1: the same guard, three distances](media/confidence/distance.mp4 "Room S1. Far away the guard is only suspicious (25%); at mid range it detects you; close up it is sure fast.")

Far away is a guess; close up is certain. Confidence holds up well until about two thirds of the range, then drops away.

Setting: `Vision Max Range`, shaped by `Vision Distance Curve` if you assign one.

### Light and shadow

![Room S2: sun, shade and a lamp](media/confidence/light.mp4 "Room S2. In full sun it tracks you (68%); in the shade under the roof it only suspects you (24%); a lamp lights you up again (70%).")

APS knows how lit you are where you stand: in shade a guard sees you about four times worse than in the sun.

Settings: tick `Use Per Target Light` (`Trace Sun Shadow` under it is on already), and call **Set Sun Direction** once from your level. More on [World & fairness](world.md#light). `Darkness Min Detection` is how much it still sees in total darkness.

::: info Your own light system
If your game already measures light (a light gem), set **Light Level Override** on the player's APS Target Component. It wins over everything, as long as `Use Per Target Light` is ticked.
:::

### Cover

![Room S3: in the open, behind a chest-high wall, behind a tall wall](media/confidence/cover.mp4 "Room S3. In the open all 5 points show (67%); behind a chest-high wall only your head and shoulders do (43%); behind a tall wall it can't make you out (15%).")

APS checks 5 points on you: head, chest, pelvis and both shoulders. The more of you it can see, the surer it gets. Lean your head over cover and it starts to notice; duck fully and it can't see you at all.

### Stance

![Room S4: standing, crouched behind a low wall, crouched in the open](media/confidence/stance.mp4 "Room S4. Standing behind the low wall it detects you (55%); crouched behind it, nothing (0%); crouched in the open is no help (69%).")

Crouching helps only behind cover. Set how many of your points must show before you count, per stance: `Min Visible Points Standing`, `Min Visible Points Crouched` and `Min Visible Points Prone` (all 1 by default, so stance changes nothing until you raise them: 2 crouched and 3 prone is a good start).

### Vision cones

![Room S5: ahead, to the side, behind](media/confidence/cones.mp4 "Room S5. Straight ahead it is sure of you (91%); at the side it misses you standing still (0%); behind it, only fast movement registers.")

Three cones, checked in order:

| Cone | Angle | Strength | Range |
|---|---|---|---|
| Focal | 60° each side | full | full |
| Peripheral | 110° each side | 45% | 60% |
| Rear | 60°, from behind | 25% | 35%, moving targets only |

The focal cone is always on. The peripheral and rear cones are optional: tick `Enable Peripheral Cone` and `Enable Rear Motion Cone` on the profile. The focal angle is `Vision Half Angle Deg`.

### Eyes in the head

![Room S6: beside it, in front, behind](media/confidence/head.mp4 "Room S6. Its head glanced at you beside it (85%); it looked away though you stood in front of it (0%).")

The guard sees where its **head** looks, not where its body points. Glance-around animations really move its sight, and a turn takes time, so it can't see you before it has turned to look.

Settings: `Use Eye Socket` with `Eye Socket Name` (for example `head`), `Eye Direction Mode`, and `Eye Turn Rate Deg Per Sec`.

### Glass, leaves and smoke

![Room S7: behind glass, a hedge and smoke](media/confidence/seethrough.mp4 "Room S7. Glass hides nothing (68%); a hedge lets some sight through (49%); thick smoke hides you (0%).")

Each surface lets through its own share of sight: glass all of it, foliage and smoke part of it, walls none. Hide in tall grass and you are partly visible, not all or nothing.

Setting: `Surface Vision Transmission` maps a physical material to the share it lets through.

### Fog and weather

![Room S8: clear air, light fog, thick fog](media/confidence/fog.mp4 "Room S8. In clear air it tracks you (67%); in light fog it only suspects you (27%); in thick fog it doesn't see you at all.")

Fog shortens how far a guard can see. Put an **APS Environment** component in a smoky room, a foggy valley or a dark cellar: inside it, sense ranges and light change. **Set Weather Modifier** changes visibility everywhere at once.

### Fair spotting

![Room S9: sprinting past a doorway, then walking past it](media/confidence/fair.mp4 "Room S9. Sprint past the doorway and you make it; walk past it and you're spotted.")

A guard that has never seen you needs a moment to believe its eyes: a quick dash across its view is forgiven. Once it knows you, it re-spots you at once.

Setting: `First Spot Reaction Time`. It is 0 (off) by default; 0.3 s feels sharp but human. **On AI Telegraph** fires a moment before it commits, for a "huh?" that warns the player.

## Read it in Blueprint

| You want | Use |
|---|---|
| React at each stage | The events above, on **APS Core** (or an **APS Perception Listener**) |
| A detection meter | **Get Belief Data** (`Target`) → `Smoothed Confidence`, 0 to 1 |
| See it while you play | Tick **Show Visualizer** on APS Core |

::: deep The vision formula
Every factor multiplies, so any single zero means no detection:

```
Confidence = DistanceFalloff × AngleFalloff × ExposureRatio × LightFactor
           × MotionBonus × WeatherMod × VisibilityMultiplier × ConeScale
```

| Factor | By default |
|---|---|
| Distance falloff | `1 − (distance / range)²`: holds up until about two thirds of the range |
| Angle falloff | `cos(angle × 90°)`: full at the centre, zero at the cone's edge |
| Exposure | The weighted share of your sample points with a clear line |
| Light factor | `Lerp(Darkness Min Detection, 1.0, light level)` |
| Motion bonus | Up to 30% more for a target sprinting at 600 cm/s or faster |
| Weather | The world's weather modifier |
| Visibility multiplier | Your target's camouflage (APS Target Component) |
| Cone scale | 1.0 focal, 0.45 peripheral, 0.25 rear |

Assigning `Vision Distance Curve`, `Vision Angle Curve` or `Motion Bonus Curve` replaces the default shape. The angle is measured to your **head** (the first sample point), not your body's centre.
:::

::: deep The five points, and their weights
| Point | Weight |
|---|---|
| Head | 1.0 |
| Chest | 0.9 |
| Pelvis | 0.7 |
| Left and right shoulder | 0.6 each |

Exposure is the weighted share of points with a clear line. Head and one shoulder clear, the rest blocked: (1.0 + 0.6) ÷ 3.8 = **42%**. Unreal's own AI Perception traces only to the centre of your body, so it would report *not seen*.

The points come from the target's **APS Target Component** (5 by default, following its animation), otherwise from the profile's `Default Visibility Samples`, otherwise from a built-in set limited by `Vision Sample Count`. `Min Exposure to Register` ignores slivers. A point counts toward the stance limit only when more than half of the sight reaches it.
:::

::: deep How several senses combine
Senses don't average. The strongest one sets the level and every other active sense adds a small bonus:

```
Fused = (best active sense × its weight) + (other active senses × Corroboration Bonus)
```

Vision at 80% plus hearing and smell gives 80% + 2 × 10% = 100%: seeing you *and* hearing you makes it surer than either alone.
:::

::: deep The thresholds and timings
| Setting | Default | What it does |
|---|---|---|
| `Suspect Threshold` | 0.15 | Enter Suspected |
| `Detect Threshold` | 0.35 | Enter Detected |
| `Track Threshold` | 0.60 | Enter Tracked |
| `Min Track Duration` | 0.5 s | Time in Detected before it can track: no instant lock-on |
| `Telegraph Threshold` | 0.25 | When **On AI Telegraph** fires: keep it between Suspect and Detect |
| `First Spot Reaction Time` | 0.0 s | On first sight only, how long it must see you before confidence builds |

Vision loses you quickly: when it stops seeing you, its share drops at once rather than fading. Its loss reason says how: **Occluded** behind something, **OutOfRange** beyond its range or cone, **SensorDropout** when it was too dark, cloaked or blinded.
:::

## Change it from script

**Set Target Confidence** (Target, Confidence) raises the AI's belief once, at any range: a tip-off, an alarm, "it heard the shot". It never lowers belief, and afterwards the belief fades as usual unless a sense keeps it up.

For anything that should **hold**, or push belief **down**, use evidence: **Add Target Evidence** (Target, Evidence Tag, Operation, Value, and under the arrow Lifetime and Source).

| Operation | While it holds |
|---|---|
| **Raise (floor)** | Belief is at least Value. Gives the AI a belief about the target if it had none. |
| **Clamp (ceiling)** | Belief is at most Value, **even while it sees you**: a disguise that keeps every guard at Suspected |
| **Lower (relative reduction)** | Belief settles Value below what the senses alone say: doubt rather than a hard limit. Only while a sense reports the target; once all are silent, normal fading takes over. |
| **Invalidate (force zero)** | Belief is forced to 0 and the target steps back down: "you didn't see anything" |

- Adding the same **Evidence Tag** again replaces the entry, so re-applying a disguise refreshes it instead of stacking.
- `Lifetime` 0 holds until **Remove Target Evidence** (Target, Evidence Tag) or **Clear Target Evidence** (Target); above 0 it expires by itself.
- Several pieces resolve together: the highest floor, the lowest ceiling, the reductions added up, and a ceiling always beats a floor.
- **Get Target Evidence** (Target) lists what is applied, with its `Source`, so you can see why belief sits where it does.

```
The player puts on a guard's uniform
  └─► for each guard: Add Target Evidence (Player, "Disguise", Clamp (ceiling), 0.15)

The player is seen taking it off, or attacks
  └─► for each guard: Remove Target Evidence (Player, "Disguise")
```

## APS and Unreal's AI Perception

| | Unreal AI Perception | APS |
|---|---|---|
| The result | Seen or not seen | 0 to 100%, through seven states |
| Line of sight | One trace to the body's centre | Five points: how much of you shows |
| Cover | Head over a crate: still "not seen" | Partly visible, partly sure |
| Light | Not taken into account | Light and shadow where you stand |
| Cones | One cone | Focal, peripheral and rear, plus the head's direction |
| Surfaces | Blocks or doesn't | Glass, leaves and smoke each let some sight through |

::: try S1 to S9
In the demo, walk into the Sight wing from the hub. Each room tests one thing on this page: stand on pads 1, 2 and 3 and compare the result cards. The hub's Meter, by the entrance, shows the whole idea in ten seconds.
:::
