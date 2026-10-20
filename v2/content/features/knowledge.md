---
title: Knowledge & witnesses
description: What a whole faction knows and how it found out - descriptions that witnesses can give, radio reports that arrive late and vague, a faction-wide alert level, and disguises that work because descriptions stop matching.
local: Police, ShirtColour, Vehicle, Height, Red, WhiteVan, Tall, Coat
---
<div class="kicker">Brain</div>

# Knowledge & witnesses

Knowledge that outlives the guard who saw you: descriptions a witness can give, reports that arrive late and vague over the radio, and a faction that hunts for whoever fits.

<div class="meta"><span>The <b>APS Knowledge</b> module (part of APS)</span><span><b>APS Signature</b> and <b>APS Observer</b> components</span><span>Demo: room <b>Q6</b></span></div>

::: fast
![Room Q6: a lookout radios a description](media/knowledge/wanted.mp4 "Room Q6. A lookout sees you and radios a description: WANTED, ORANGE SUIT. The checkpoint stops anyone who fits it.")
- Give the player an **APS Signature**: traits a witness could describe (an orange suit, a white van).
- Give guards an **APS Observer**: they report what they see to their **faction**, as a description.
- The faction's knowledge outlives the guard, and **Match Descriptor** asks who fits it. Change your coat and you stop fitting.
:::

::: info Why it is its own module
The APS core is genre-blind: confidence, senses, belief. It doesn't know your game has police, a hive or a militia. **APS Knowledge** is built on top of the core and the core never depends on it (the build enforces that). Use the core alone and none of this exists: nothing here is required.
:::

## Descriptions: knowing *of* someone

A **descriptor** is a set of traits, what a witness could describe:

| Field | Meaning |
|---|---|
| `Key` | What kind of trait: ShirtColour, Vehicle, Height |
| `Value` | What it is: Red, WhiteVan, Tall |
| `Observability` | How easy it is to notice, 0 to 1 (0.8 by default) |

Put an **APS Signature** component on anything that can be described and fill its `Signature`; it comes with a starter set so it does something the moment it's added. A player who changes coat calls **Set Trait** again; one who ditches the car calls **Remove Trait**.

### A better look sees more

**Get Observed Subset** (Observation Quality) returns only the traits a witness could make out with a look that good: a trait is noticed when its `Observability` is at least 1 minus the quality. A close, clear look gets everything; a glimpse in the dark gets only the obvious. That is what makes a disguise a mechanic rather than a flag: change the loud trait and descriptions stop matching, though nobody checked a "disguised" box.

### Does this person fit?

**Match Descriptor** (Faction, Descriptor, Min Match) asks the faction *does anyone we know of look like this?* and returns the best match and how well it fits:

- Only keys in **both** descriptions are compared: a witness who never saw the car doesn't weaken the match.
- Agreement is weighted by `Observability`: matching on something unmissable counts for more than on a detail nobody could reliably see.
- **Each contradiction halves what is left** (same key, a different value). Someone in a red shirt isn't a partial match for a blue-shirt suspect: they're actively less likely to be them.

![The demo's checkpoint Blueprint](media/cards/squad_radio.webp "How the demo does it (BP_Q6_Radio › Fits Description): Get APS Knowledge, then Match Descriptor with what the guard sees of you (Get Signature on your APS Signature). Fits above 0.5: stopped.")

| Node (any Blueprint) | What it does |
|---|---|
| **Set Descriptor Trait** (Descriptor, Key, Value, Observability) | Add a trait, or change one already there |
| **Remove Descriptor Trait** (Descriptor, Key) | Drop a trait |
| **Get Descriptor Trait** (Descriptor, Key) | What it says about a key; false when nothing |
| **Match Against** (Description, Known) | The 0 to 1 fit between any two descriptions |
| **Shared Key Count** (Descriptor, Other) | How many keys both have: a confident match on one trait is not a confident match on five |

## What a faction knows

The **APS Knowledge** subsystem keeps a store per faction: entries about people, each saying who reported it. Get it from any Blueprint with **Get APS Knowledge**.

| Node | What it does |
|---|---|
| **Report Observation** (Faction, Subject, Descriptor, Location, Confidence, Provenance) | Tell a faction something, at once. Merges with an entry about the same person, so ten sightings stay one manhunt. Returns the entry's id. |
| **Report Via Channel** (… Channel) | The same, sent along a channel: it arrives late, vaguer and missing details |
| **Get Entry for Subject** (Faction, Subject) | What the faction knows about one actor |
| **Get Entries** (Faction) | Everything it believes, strongest first |
| **Match Descriptor** | Who fits this description? |
| **Cancel Pending From** (Provenance) | Drop everything a sender has in flight: silence the witness before the message lands |
| **Forget Entry**, **Forget Faction** | Drop one entry, or everything a faction knows |

Every entry fades unless refreshed (`Entry Decay Per Second`) and is dropped below `Entry Forget Threshold`. **On Knowledge Updated** (Faction, Entry Id) fires when a report arrives.

**Provenance is the point:** every entry records who said so. That is what makes **Cancel Pending From** meaningful: take out a radio operator mid-transmission and the alert genuinely never arrives.

### Channels: being told isn't seeing

| Channel | Delay | Position error | Detail lost | Confidence |
|---|---|---|---|---|
| **Direct** (seen first-hand) | 0 s | 0 cm | none | × 1.00 |
| **Shout** | 0.5 s | up to 3 m | 25% | × 0.85 |
| **Radio** | 2 s | up to 6 m | 35% | × 0.75 |
| **Report** (in person) | 8 s | up to 15 m | 55% | × 0.60 |

Read a row: a report carried back on foot arrives eight seconds late, 15 m out, missing over half its detail, and believed a good deal less. **That gap is where the drama is.** A guard who got a clear look but could only shout passes on a description with a quarter of it missing, so the dragnet looks for the wrong coat, and the player gets away with something a working radio wouldn't have allowed. The channel specs are data on the subsystem: adjust them per project.

### The faction's alert level

Each faction has an alert, 0 to 1: a generalised wanted level. Reports raise it (`Alert Per Report` on the Observer); it decays over time. **Get Faction Alert**, **Raise Faction Alert**, **Set Faction Alert**, and **On Faction Alert Changed** (Faction, Alert).

## The Observer: a guard that reports

![Room Q6: change clothes and walk through](media/knowledge/changed.mp4 "Room Q6, again. In different clothes you no longer fit the description the lookout radioed, so the checkpoint waves you through.")

Add an **APS Observer** next to a guard's APS Core and it reports what that guard perceives to its faction, by itself:

| Setting | Default | What it does |
|---|---|---|
| `Faction` | Police | Which faction it reports to |
| `Report Channel` | Radio | How its reports travel: Direct is instant and complete; the others cost time and detail, and can be cut off |
| `Min Confidence to Report` | 0.45 | Below this, not worth telling anyone |
| `Report Interval` | 2 | Seconds between reports |
| `Ideal Observation Range` | 600 | Closer than this is a perfect look |
| `Max Observation Range` | 4000 | Further than this, nothing useful is made out |
| `Alert Per Report` | 0.15 | How much each report raises the faction's alert |
| `Discover Evidence` | On | Also find [evidence](search.md) near it |
| `Report Evidence to Faction` | On | File what it finds with the faction too (off keeps it to itself) |

**Get Observation Quality** (Target) is how good a look it has right now: exactly what **Get Observed Subset** wants. **Report Now** files at once, ignoring the interval and confidence gates (an alarm pull, a phone call).

A report **names** the person only when the look is good (quality 0.75 or more). Below that, the faction gets a description and no actor: what a manhunt really starts from. The position reported is where the guard **believes** the person is, not where they really are, so a guard that only heard someone can't cheat for the faction.

## Worked example: a description that degrades

1. The player, in a red coat, is seen at 35 m, near the edge of useful range: a poor look.
2. **Get Observed Subset** at that quality keeps only the loud traits: the coat makes it, the watch doesn't.
3. The guard has no radio, so your logic sends it with **Report Via Channel**, Shout: a quarter of the traits lost, the position up to 3 m out, confidence × 0.85.
4. The faction now believes *someone in a red coat, roughly there*.
5. The player takes off the coat (**Remove Trait**). **Match Descriptor** now contradicts on the one key that mattered: the score halves, and they walk past the dragnet.

Nothing there is a disguise system: it's look quality, channel loss and trait matching doing their ordinary jobs.

## APS and Unreal's AI Perception

| | Unreal AI Perception | APS Knowledge |
|---|---|---|
| Knowledge beyond one AI | None | Per faction, outliving the witness |
| Describing someone | None | Traits, noticed according to the look |
| Passing it on | n/a | Channels with delay, error and loss, that can be cut off |
| Recognising someone | Only by seeing them | By description: disguises work |

::: try Q6
In the demo, the **Squad** wing's Q6: walk through the checkpoint in the orange suit (stopped), then change into the blue one and try again.
:::
