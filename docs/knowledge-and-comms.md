# Knowledge & Comms

**What a faction collectively knows, how it found out, and what got lost on the way.**

Everything on this page lives in **APS Knowledge** — a second module inside the same plugin, and an entirely optional one.

!!! info "Why it is a separate module"
    APS Core is genre-blind. It knows about confidence, senses and belief; it does
    not know your game has police, or a hive, or a militia. The knowledge fabric
    is built *on top of* the core and the core never depends on it — that
    one-way dependency is enforced by the build system, not by convention.

    Use the core alone and none of this exists. Nothing here is a required step.

---

## Descriptors: knowing *of* someone

A **descriptor** is a bag of traits — what a witness could describe.

| Field | Meaning |
|---|---|
| `Key` | What kind of trait — `"ShirtColour"`, `"Vehicle"`, `"Height"` |
| `Value` | The observation — `"Red"`, `"WhiteVan"`, `"Tall"` |
| `Observability` | How easy it is to notice, `0–1`. Default `0.8` |

Put an **APS Signature Component** on anything that can be described, and call **Set Trait** to fill it in. A player who changes coat calls **Set Trait** again; one who ditches the car calls **Remove Trait**.

### Observation quality gates what is seen

**Get Observed Subset** (`Observation Quality`) returns only the traits a witness at that quality could actually have made out. A trait survives when `Observability >= 1 - Quality` — so a good look gets you everything, and a glimpse in the dark gets you only the obvious.

This is what makes a disguise work as a mechanic rather than a flag: change the loud trait and the descriptions stop matching, even though nobody checked a "disguised" boolean.

### Matching

**Match Descriptor** (`Faction`, `Descriptor`, `Min Match`) asks *does this person fit anything we are looking for?*

Only keys present in **both** descriptors are compared, so a witness who never saw the vehicle does not weaken the match.

Agreement is weighted by `Observability`: a trait that is hard to notice is also weaker evidence when it agrees. Matching on something unmissable counts for more than matching on a detail nobody could reliably have seen.

**Each** contradiction — same key, different value — halves what is left. One mismatch halves the score, two quarter it. Someone in a red shirt is not a partial match for a blue-shirt suspect; they are actively less likely to be them.

**Shared Key Count** (`Other`) tells a confident match on one trait from a confident match on five, which is usually the difference between "worth a look" and "that is them".

---

## The fabric: what a faction knows

A faction-wide store of entries, each carrying where the information came from.

| Node | Does |
|---|---|
| **Report Observation** | Files what one AI saw, immediately. Returns an entry ID |
| **Report Via Channel** | Files it through a comms channel, with delay and fidelity loss |
| **Get Entry For Subject** | What the faction knows about one actor |
| **Get Entries** (`Faction`) | Everything the faction holds |
| **Match Descriptor** | Does this person fit anything on file |
| **Cancel Pending From** (`Provenance`) | Discard what a sender has in flight but undelivered |
| **Forget Entry** | Drop one entry |

### Provenance is the point

Every entry records *who said so*. That is what makes **Cancel Pending From** meaningful: silence the witness before their message lands and the faction never learns it. A radio operator taken out mid-transmission genuinely stops the alert.

---

## Comms channels

Information does not arrive instantly or intact. **Report Via Channel** models the difference between seeing something and being told about it.

| Channel | Delay | Position error | Trait loss | Confidence |
|---|---|---|---|---|
| **Direct** (witnessed) | 0 s | 0 cm | 0% | ×1.00 |
| **Shout** | 0.5 s | 300 cm | 25% | ×0.85 |
| **Radio** | 2 s | 600 cm | 35% | ×0.75 |
| **Report** (in person) | 8 s | 1500 cm | 55% | ×0.60 |

Read across a row: a report carried back on foot arrives eight seconds late, fifteen metres out, having lost over half its detail, and is believed a good deal less than something seen first-hand.

!!! tip "This is where the drama is"
    The gap between what one AI *saw* and what the faction *believes* is the
    interesting part. A guard who got a clear look but only managed to shout is
    passing on a description with a quarter of its detail missing — so the
    dragnet looks for the wrong coat, and the player gets away with something
    they would not have if the radio had worked.

Channel specs are data, not hardcoded. Adjust them per project.

---

## The Observer Component

The bridge that connects an agent's own perception to the fabric. Add it beside a **Perception Core** and it reports what that AI sees, automatically.

| Setting | Default | Meaning |
|---|---|---|
| `Faction` | `Police` | Which faction's store this reports to |
| `Report Channel` | `Radio` | How reports travel. `Direct` is instant and complete; anything else costs time and detail and can be cut off before it lands |
| `Min Confidence To Report` | 0.45 | Below this, not worth telling anyone |
| `Report Interval` | 2.0 s | How often it may file |
| `Ideal Observation Range` | 600 cm | Closer than this is a perfect look |
| `Max Observation Range` | 4000 cm | Beyond this, nothing useful is made out |
| `Alert Per Report` | 0.15 | How much each report raises faction alert |
| `b Discover Evidence` | true | Also find [evidence](evidence-and-search.md) in range |
| `b Report Evidence To Faction` | true | Also file discovered evidence with the faction. Off keeps the discovery private to the AI that found it |

**Get Observation Quality** (`Target`) returns how good a look this observer currently has — which is exactly the value **Get Observed Subset** wants. **Report Now** files immediately, ignoring the interval.

A report only *names* the subject when observation quality reaches 0.75. Below that the faction receives a description and no actor, which is what a manhunt actually starts from. The position reported is the AI's believed position, not the actor's real one, so an AI that only heard someone cannot cheat on the faction's behalf.

---

## Worked example: a description that degrades

1. The player, wearing a red coat, is seen by a guard at 3500 cm — near the edge of useful range, so observation quality is poor.
2. **Get Observed Subset** at that quality returns only the loud traits. The coat makes it; the watch does not.
3. The guard has no radio, so your logic calls **Report Via Channel** with **Shout**. A quarter of the remaining traits are lost, position lands up to 3 m out, confidence drops to 85%.
4. The faction now believes *someone in a red coat, roughly there*.
5. The player removes the coat and calls **Remove Trait**. **Match Descriptor** against the file now contradicts on the one key that mattered, halving the score — they walk past the dragnet.

Nothing in that sequence is a disguise system. It is observation quality, channel fidelity and trait matching doing their ordinary jobs.

---

## See also

- **[Evidence & Search](evidence-and-search.md)** — what an observer finds when nobody is there to see
- **[Memory & Recall](memory-and-recall.md)** — what one AI holds privately, as opposed to what the faction knows
- **[Squad & Relationships](squad-and-relationships.md)** — the simpler, core-only intel sharing
