# Evidence & Search

**Things left in the world that an AI can find, and a search that gets colder as it goes.**

Two systems that work together and are useful apart. Both live in the optional **APS Knowledge** module — see [Knowledge & Comms](knowledge-and-comms.md) for what that module is and why it is separate.

---

## Evidence

An **APS Evidence Component** turns any actor into something an AI can discover and draw a conclusion from: a body, a forced door, a dropped weapon, blood, a footprint, a parked getaway car.

Add it to the actor. That is the setup.

| Setting | Default | Meaning |
|---|---|---|
| `Evidence Tag` | `Evidence` | What kind of thing this is — `"Body"`, `"ForcedLock"`, `"Blood"` |
| `Conspicuousness` | 0.6 | How hard it is to miss, `0–1`. Scales how close an AI must be |
| `Belief Strength` | 0.8 | How much finding it should convince the AI, `0–1` |
| `Lifetime Seconds` | 0 | Auto-removal after this long. `0` means it stays |
| `Instigator` | none | Who is responsible, if the evidence implicates someone |
| `Implied Direction` | zero | Which way it suggests they went — drag marks, a blood trail |
| `b Auto Register As Perceivable` | true | Registers itself so senses can find it |

**Get Age** returns how long it has existed; **Remove Evidence** takes it away — for a body that gets dragged off, or a stain someone mops up.

### Discovery

An **[APS Observer Component](knowledge-and-comms.md)** with `b Discover Evidence` on finds evidence in range and fires **On Evidence Discovered**. From there it is your logic: raise an alarm, start a search, change patrol, file a [memory](memory-and-recall.md).

!!! note "Evidence is not a suspect"
    A corpse is a *thing found*, not a *person seen*. APS keeps those separate on
    purpose — an observer that filed a body as a live sighting would have the AI
    chasing a target that is lying at its feet. Discovery fires its own event and
    does not enter the sighting-reporting path.

### `Implied Direction` is the useful one

Most evidence tells you *something happened here*. Evidence with a direction tells you *and they went that way* — which is what turns a search from a sweep into a pursuit. Set it on drag marks, blood trails, a broken fence, a door left swinging.

---

## Search

An **APS Search Component** answers one question repeatedly: *given that they were last here and I have already looked in these places, where should I look next?*

```
On AI Lost (Target)
  → Begin Search (Last Known Location)

Behavior Tree tick
  → Get Best Search Point → Point
  → Move To (Point.Location)
  → on arrival: Mark Cleared (Point.Location, 400)

  → Branch: Is Search Exhausted?
      → Give up. Return to patrol.
```

| Node | Does |
|---|---|
| **Begin Search** (`Last Known Location`) | Starts a search around a point |
| **End Search** | Stops it |
| **Is Searching** | Whether one is running |
| **Get Best Search Point** | The single most promising place to look next |
| **Get Ranked Search Points** (`Count`) | The best N, for spreading a squad out |
| **Mark Cleared** (`Location`, `Radius`) | "I looked here." Removes that area from consideration |
| **Is Search Exhausted** | Nowhere promising left — time to give up |
| **Get Search Progress** | `0–1`, how much of the space has been cleared |
| **Get Search Duration** | Seconds since **Begin Search** |

### How it ranks

Probability is modelled on **reachability**, not proximity. The most likely place is not next to where you lost them — they have had time to move, so the peak sits at the frontier of how far they could plausibly have travelled, and it expands as the search goes on.

Points are gated against the navmesh, so the AI does not search inside a wall. If there is no navigation system in the level, it falls back gracefully rather than returning nothing.

!!! tip "Mark Cleared is not optional"
    The ranking only gets colder if you tell it what you have already checked.
    An AI that never calls **Mark Cleared** will keep being sent to the same
    excellent-looking spot forever, and **Is Search Exhausted** will never
    become true.

### Spreading a squad

**Get Ranked Search Points** with `Count` equal to your squad size gives each member somewhere different to be. Combine with the shared [knowledge fabric](knowledge-and-comms.md) so one member's **Mark Cleared** informs the others.

---

## Putting them together

A worked sequence, all of it your logic:

1. The player breaks a lock and leaves. The lock actor has **Evidence** — tag `"ForcedLock"`, `Implied Direction` pointing down the corridor.
2. A guard with an **Observer** walks past and **On Evidence Discovered** fires.
3. Your Blueprint calls **Begin Search** at the lock, and **Remember** on a place subject so the guard treats that corridor as suspicious for the rest of the session.
4. The Behavior Tree drives **Get Best Search Point** → move → **Mark Cleared** until **Is Search Exhausted**.
5. The guard gives up, but the memory of that corridor stays.

---

## See also

- **[Memory & Recall](memory-and-recall.md)** — filing what was found
- **[Knowledge & Comms](knowledge-and-comms.md)** — telling everyone else about it
- **[Behavior Trees](behavior-trees.md)** — wiring search into a tree
