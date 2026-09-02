# Behavior Trees

APS tells your AI **what it believes**. The Behavior Tree decides **what to do**. This page is the wiring between them.

There are no custom BT nodes to learn — you use standard Blackboard decorators and services, driven by APS events and queries.

---

## The pattern: events write, the BT reads

Push APS state into the Blackboard from events, and let the BT read the Blackboard. Never poll APS from a BT service every tick when an event already tells you.

### Recommended Blackboard keys

| Key | Type | Written by |
|---|---|---|
| `TargetActor` | Object (Actor) | `On Attention Changed` |
| `LastKnownPosition` | Vector | `On AI Lost` |
| `PredictedPosition` | Vector | `On AI Lost` |
| `SearchRadius` | Float | `On AI Lost` (from `Get Uncertainty Radius`) |
| `LossReason` | Enum (`ELossReason`) | `On AI Lost` |
| `LossDirection` | Vector | `On AI Lost` |
| `LastCoverActor` | Object (Actor) | `On AI Lost` |
| `AwarenessLevel` | Enum (`EAwarenessLevel`) | `On AI Awareness Changed` |
| `ThreatLevel` | Enum (`EThreatLevel`) | `On AI Detect` / `On AI Think Threat` |
| `CombatRole` | Enum (`ECombatRole`) | `On Combat Role Assigned` |
| `bHasTarget` | Bool | `On AI Detect` (true) / `On AI Forget` (false) |
| `InvestigateLocation` | Vector | `On AI Hear`, `On AI Suspect`, `On AI Squad Alert`, `On Location Belief Changed` |

---

## Wiring the events

### Attention changes → set the target

```
Event On Attention Changed (Old Target, New Target)
  └─► Get AI Controller → Get Blackboard
        ├─► Set Value as Object ("TargetActor", New Target)
        └─► Set Value as Bool   ("bHasTarget", New Target is Valid)
```

Use `On Attention Changed` rather than `On AI Detect` for the target key. Attention is sticky — it will not thrash between two equally-scored targets and force your BT to re-plan every tick.

### Losing a target → set up the search

```
Event On AI Lost (Target, Last Known, Predicted, Last Cover Actor)
  └─► Blackboard
        ├─► Set Vector ("LastKnownPosition", Last Known)
        ├─► Set Vector ("PredictedPosition", Predicted)
        ├─► Set Object ("LastCoverActor",    Last Cover Actor)
        ├─► Set Float  ("SearchRadius",      Get Uncertainty Radius (Target))
        ├─► Set Enum   ("LossReason",        Get Loss Reason (Target))
        └─► Set Vector ("LossDirection",     Get Loss Direction (Target))
```

### Hearing something → investigate

```
Event On AI Hear (Location, Loudness, Sound Type Name)
  └─► Branch: bHasTarget == false
        True → Set Vector ("InvestigateLocation", Location)
```

Guard it on `bHasTarget` so a footstep does not interrupt an active chase.

For sounds with no source actor, such as a thrown rock or an explosion, the AI holds a place belief instead of a target. Read it the same way:

```
Event On Location Belief Changed (Location, Tag, State, Confidence)
  └─► Branch: State == Suspected AND bHasTarget == false
        True → Set Vector ("InvestigateLocation", Location)
```

### Squad alerts

```
Event On AI Squad Alert (Target, Location, Threat)
  └─► Branch: bHasTarget == false
        True → Set Vector ("InvestigateLocation", Location)
```

---

## Search behaviour driven by loss reason

This is the highest-value thing in the plugin, and it is one `Switch` node.

```
Selector: Search
├── [LossReason == Occluded]
│     Sequence: MoveTo LastKnownPosition
│             → MoveTo LastCoverActor
│             → Look Around (2s)
│             → Check the far side of that cover
│
├── [LossReason == OutOfRange]
│     Sequence: MoveTo LastKnownPosition
│             → MoveTo (LastKnownPosition + LossDirection × 500)
│             → Expanding sweep using SearchRadius
│
├── [LossReason == SoundFaded]
│     Sequence: MoveTo LastKnownPosition
│             → Look Around (3s)
│             → Return to patrol      // do NOT chase — it was only a noise
│
├── [LossReason == ScentLost]
│     Sequence: MoveTo LastKnownPosition
│             → Follow LossDirection in steps    // trail the scent
│             → Sniff / circle at each step
│
├── [LossReason == SensorDropout]
│     Sequence: Look Around (1.5s) → Return to patrol
│
└── [Default]
      Sequence: EQS search inside SearchRadius around LastKnownPosition
```

An AI that runs straight to the corner you hid behind reads as *smart*. The same AI running a generic circle reads as *dumb*. Same code — different branch.

---

## Using uncertainty as a search radius

`SearchRadius` grows the longer you stay hidden, which naturally widens the search over time.

**With EQS:** expose `SearchRadius` as a query parameter and use it as the generator radius around `LastKnownPosition`.

**Without EQS:**

```
Task: Search Step
  └─► Get Random Reachable Point In Radius
        Origin = LastKnownPosition
        Radius = SearchRadius
  └─► MoveTo that point
  └─► Look Around (1s)
```

Loop it three or four times and the AI naturally spirals outward.

**With the Knowledge module:** an **APS Search Component** replaces the radius with a probability field that spreads at the target's speed, skips anything off the navmesh, and empties cells the AI has already walked through. See [Evidence & Search](evidence-and-search.md).

---

## Decorators worth having

| Decorator | Condition | Use |
|---|---|---|
| Blackboard: `bHasTarget` is set | — | Gate the entire combat branch |
| Blackboard: `AwarenessLevel >= Alerted` | — | Gate aggressive behaviour |
| Blackboard: `ThreatLevel >= High` | — | Gate "commit to a fight" |
| Blackboard Compare: `CombatRole == Flanker` | — | Gate the flank branch |
| Custom BP decorator → **Has Threat At Or Above** (`High`) | — | Cleanest threat check |
| Custom BP decorator → **Get Total Pain Level** > 0.5 | — | Impaired-behaviour branch |
| Custom BP decorator → **Get Attention Duration** > 15 | — | "I've been chasing too long, give up" |

---

## A complete tree skeleton

```
Root
└── Selector
    ├── [bHasTarget]  ── COMBAT
    │   └── Selector
    │       ├── [ThreatLevel >= High]  → Engage (fire / melee)
    │       ├── [CombatRole == Flanker] → Flank to TargetActor
    │       └── Default                 → Approach TargetActor
    │
    ├── [LastKnownPosition is set]  ── SEARCH
    │   └── Selector switching on LossReason   (see above)
    │
    ├── [InvestigateLocation is set]  ── INVESTIGATE
    │   └── Sequence: MoveTo InvestigateLocation
    │                → Look Around (3s)
    │                → Clear InvestigateLocation
    │
    └── PATROL
        └── Your normal patrol loop
```

Clear `LastKnownPosition` on `On AI Forget` and the AI falls through to patrol on its own.

---

## Reacting before commitment

Two events make an AI feel alive without touching the tree structure:

```
Event On AI Telegraph (Target, Confidence)
  ├─► Play Sound ("Hm?")
  └─► Set Focus (Target)          // head turns toward you

Event On AI Suspect (Target, Location, Stimulus)
  └─► Set Vector ("InvestigateLocation", Location)
```

The AI turns to look, says something, and *then* the tree drives it over to investigate. The player reads the whole chain.

---

## Multi-target logic

Most AI only need `Get Attention Target`. When you need more:

```
Get Targets Sorted By Score  → array of Belief Record (best first)
  └─► ForEach
        └─► Break Belief Record
              ├─ Threat Level
              ├─ Smoothed Confidence
              ├─ Last Known Position
              └─ Relationship
```

Use it for: picking the highest-threat target for a suppressor, counting how many enemies are visible, or deciding to retreat when three targets are `Tracked` at once.

---

## Reacting to shared intel differently

```
Event On AI Detect (Target, Threat Level, Stimulus)
  └─► Branch: Stimulus == Shared Intel
        True  → cautious approach, weapon lowered, no firing yet
        False → I perceived this myself — full engagement
```

Without this branch a squad becomes telepathic: one guard spots you and four others instantly headshot you through a wall. With it, they converge believably.

---

## Performance notes

- **Do not call APS queries in a BT service on every tick.** Push from events instead.
- If you must poll, run the service at 0.2–0.5 s. Perception itself only updates every 0.1 s by default, so faster polling reads stale data anyway.
- `Get Belief Data` copies the whole struct. Prefer the narrow queries (`Get Last Known Position`, `Get Loss Reason`) in hot paths.

---

