# Scale & Crowds

**Running hundreds of perceiving agents without paying for hundreds of perceiving agents.**

Everything here is opt-in. A project that changes nothing gets the same behaviour it always had — these are the levers for when the agent count grows past what full-fidelity perception can afford.

Read [Performance](performance.md) first for the per-agent settings. This page is about the level as a whole.

---

## Significance: who deserves the CPU

The subsystem scores every agent each pass and gives the important ones more attention. The default score weighs three things:

| Input | Weight |
|---|---|
| Distance to the nearest viewer | 0.60 |
| Currently engaged with a target | 0.55 |
| Awareness level | 0.25 |

That score picks the agent's LOD tier, which drives tick throttling. A guard in a firefight ten metres away stays at full rate; one asleep on the far side of the map drops back.

**Viewers** are all local players, so split-screen works without configuration.

### Writing your own

Subclass **APS Significance Policy** and override **Score Significance** (`Agent`, `Nearest Viewer Dist`, `b Is Engaged`, `Awareness`). Assign it on the subsystem.

Use this when your game has its own idea of what matters — a boss that must never throttle, an agent scripted into a cutscene, anything inside the player's current objective.

!!! warning "Setting an LOD tier directly does not stick"
    The subsystem recomputes tiers from significance every pass and overwrites
    whatever you wrote. Drive the tier *through* a policy; that is the supported
    seam.

---

## Frame budget

`Max Perception Updates Per Frame` on the subsystem caps how many agents run a full pass in any one frame. `0` — the default — means unlimited.

Agents over the cap are **deferred, not dropped**. They run next frame instead, so nothing silently stops perceiving; the cost is spread rather than avoided. Set it when a spike at spawn time or on a level transition is the problem.

---

## The crowd tier

At high agent counts the expensive part is line traces. The statistical tier removes them entirely for agents that are not close enough to matter, and rolls for detection instead.

| Setting | Default | Meaning |
|---|---|---|
| `b Enable Statistical Tier` | false | Turn the whole thing on |
| `Statistical Tier Threshold` | 3 | LOD tier at which an agent goes statistical |
| `Statistical Detection Rate` | 1.0 | Rolls per second, scaled by the factors below |
| `Statistical Detection Confidence` | 0.5 | Confidence granted on a hit |

A statistical agent still respects distance falloff, which way it is facing, light level and target motion — it simply resolves them as a probability per second rather than by tracing geometry. A crowd member behind you is still much less likely to notice you than one looking straight at you.

!!! note "It is a floor, not a ceiling"
    Going statistical does not *reduce* an existing belief. An agent that already
    had a strong contact keeps it; the tier only changes how new detection is
    acquired. Promotion back to a low tier restores full geometric perception on
    the next pass.

!!! tip "Set the threshold realistically"
    A threshold of `1` makes almost every agent statistical, including ones near
    the player. The default of `3` means only genuinely distant, unengaged agents
    take the cheap path.

---

## Environment volumes

An **APS Environment Component** on any actor declares local conditions in a radius — a lit room, a rainstorm, a windy roof, a cellar.

| Setting | Default | Meaning |
|---|---|---|
| `Radius` | 1000 cm | How far the volume reaches |
| `Priority` | 0 | Higher wins where volumes overlap; ties go to the nearer centre |
| `b Override Light` / `Light Level` | false / 1.0 | Local light |
| `b Override Rain` / `Rain Intensity` | false / 0.0 | Local rain |
| `b Override Wind` / `Wind Speed` | false / 0.0 | Local wind |
| `b Override Indoors` / `b Is Indoors` | false / false | Indoor flag |
| `Vision Range Scale` | 1.0 | Multiplies vision range inside |
| `Hearing Range Scale` | 1.0 | Multiplies hearing range inside |
| `Smell Range Scale` | 1.0 | Multiplies smell range inside |

Each override is separate, so a volume can darken a room without claiming anything about the weather.

!!! info "Range scales are sampled at the target, not the observer"
    A guard standing in daylight looking into a darkened room gets the *room's*
    reduced vision range, which is the behaviour people expect. Sampling at the
    observer would have let guards see into fog perfectly well as long as they
    were standing outside it.

---

## Async vision traces

`b Async Vision Traces` on the profile moves visibility tracing off the critical path — results arrive on a completion callback rather than blocking the tick.

Off by default. Turn it on when trace cost is the measured bottleneck; the answer is the same, it simply arrives a frame later.

!!! warning "Falls back to synchronous in two cases"
    Multi-channel setups and configured surface transmission both need results
    that async batching cannot correctly combine, so APS quietly runs those
    synchronously rather than reporting a wrong answer.

---

## Spatial index

Candidate gathering uses a uniform grid rather than testing every registered actor. It is on by default and rebuilds on a short interval.

`aps.UseSpatialIndex 0` reverts to the exhaustive path — useful only for A/B testing whether the index is implicated in a bug.

---

## Multiplayer relevance

See [Multiplayer](multiplayer.md) for the full picture. The scale-relevant settings:

| Setting | Default | Meaning |
|---|---|---|
| `b Use Replication Relevance` | true | Filter the replicated summary |
| `Replication Relevance Range` | 15000 cm | Drop targets further than this from every viewer |
| `Replication Min Confidence` | 0.1 | Drop contacts barely worth the bandwidth |
| `b Skip Unchanged Replication` | true | Do not resend an effectively identical summary |
| `Replication Confidence Delta` | 0.02 | How much confidence must move to be worth sending |

---

## Ordering your effort

1. **Measure first.** Use **Show Budget** on the profile ([Profile Composition](profile-composition.md)) to see what the asset is asking for.
2. `Vision Sample Count` multiplies directly into trace count. It is usually the first number to look at.
3. Turn on distance tick throttling before anything more exotic.
4. Reach for the crowd tier when the agent count, not the per-agent cost, is the problem.

---

## See also

- **[Performance](performance.md)** — per-agent cost and quality profiles
- **[Profile Composition](profile-composition.md)** — the budget estimator
- **[Environment & Fairness](environment-and-fairness.md)** — what light, rain and wind do to each sense
