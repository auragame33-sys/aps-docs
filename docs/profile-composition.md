# Profile Composition & Archetypes

**Change one number for one enemy without duplicating a 170-field asset.**

A perception profile carries a lot of settings. Before composition, making one guard see further meant duplicating the whole asset — and the duplicate started drifting from the original the same day.

---

## Archetypes: a starting point in one click

Set **Archetype** on the profile and press **Apply Archetype**.

| Archetype | Character |
|---|---|
| **Guard** | Alert and forward-facing. Commits to a contact quickly and keeps it |
| **Civilian** | Wide senses, high thresholds, short memory. Reacts without investigating |
| **Stalker** | A narrow, long look and a memory that does not let go |
| **Military Patrol** | Longest sight, shares contacts with the squad, holds them through cover |
| **Wildlife** | Smell and hearing over sight. Reacts long before it is certain |

These are **presets, not modes**. Applying one writes ordinary values onto ordinary fields — nothing reads the archetype at runtime, and there is no archetype branch anywhere in the plugin. Everything an archetype does, you can reach by hand and change afterwards.

!!! info "Five genres, one unchanged core"
    That the same kernel produces a skittish deer and a patient stalker without a
    line of genre-specific code is the whole claim behind APS being genre-blind.
    The archetypes exist to demonstrate it as much as to save you time.

**Apply Archetype To** (`Target`, `Archetype`) does the same from Blueprint, so you can build a profile at runtime: spawn one, apply Civilian, override two numbers, hand it to an agent.

---

## Inheritance

Set **Parent Profile** and this asset inherits everything from it. Fields you leave alone follow the parent forever; fields you change are yours.

There is no override list to maintain. A field counts as changed when it **differs from the class default** — which is exactly the set the Details panel already marks with a revert-to-default arrow. If Unreal is showing you the arrow, that field is overridden.

!!! danger "Start from a *new* profile, not a duplicate of the parent"
    Duplicating the parent copies every one of its tuned values, and every one of
    them then reads as a deliberate change. The child would inherit nothing while
    looking perfectly wired up.

    Create a new profile, set its parent, and change only what differs.
    **Validate Profile** flags this if you get it wrong.

**Show Composition** logs field by field what is inherited and what is not.

### Pinning a default value

To hold a value that happens to equal the class default — which would otherwise read as "unset, follow the parent" — put it in the **Overrides** list instead. That list is applied after inheritance and always wins.

### When it resolves

Composition resolves **once**, when an agent starts or swaps profiles, into a private copy owned by that agent. Editing a parent therefore affects agents that spawn afterwards, not ones already running.

A profile with no parent and no overrides composes to itself, so the common case allocates nothing and every agent keeps sharing one asset.

---

## Per-agent overrides

For one enemy that differs slightly, skip assets entirely.

**Profile Overrides** on the **Perception Core** component takes a list of `Property` / `Number` / `Flag`. Leave it empty and the agent shares the profile asset directly, which costs nothing.

At runtime:

| Node | Does |
|---|---|
| **Set Profile Number** (`Property`, `Value`) | Change one numeric setting for this agent |
| **Set Profile Flag** (`Property`, `Value`) | Change one checkbox |
| **Get Profile Number** (`Property`, `Fallback`) | Read one back |
| **Clear Profile Overrides** | Return to the asset as authored |
| **Get Source Profile** | The asset as assigned, before composition |

```
Set Profile Number ("VisionMaxRange", 7777.0)
```

`Property` is the exact name from the Details panel with the spaces removed. A name that does not resolve is **refused and logged**, not silently ignored.

Three things worth knowing:

- Overrides write to a **private copy**. The shared asset never moves under the other agents using it.
- They **survive a profile swap**, because they belong to the agent rather than the asset.
- Nothing the agent believes is reset. The new value is read on the next tick.

---

## Live tuning

```
aps.Tune VisionMaxRange 5000
```

Writes to every running agent's private copy. The asset on disk is untouched and the change is gone at the next launch — which is exactly what makes it safe to try anything mid-session, rather than stopping, editing and playing again by which point the situation that looked wrong has gone.

---

## Knowing what a profile costs

**Show Budget** on the profile estimates traces and sense evaluations per second for a level of agents, and names the setting that moves each number.

**Estimate Budget** (`Agent Count`, `Targets Per Agent`) returns the same as text for your own tooling.

It is an estimate from the settings, not a measurement — it tells you what the asset is *asking for*, which is the number worth knowing before a level is full of agents rather than after.

## Comparing two profiles

Set **Compare To** and press **Compare With**. Every field where the two differ is logged as `Field: theirs → mine`.

**Diff Against** (`Other`) returns the same list to Blueprint.

---

## Validation

**Validate Profile** checks for settings that are contradictory, unreachable, or simply inert — a weight keyed to a sense the profile does not run, a threshold ordering that makes a state impossible to enter, an override naming a property that does not exist.

Run it after editing a profile, and whenever an AI behaves in a way the settings do not seem to explain. It catches the class of mistake that costs an afternoon and leaves no trace in the log.

!!! tip "It catches real mistakes"
    Every one of the five shipped archetypes was written, and four of them failed
    this validator on the first pass — an unreachable Fully Aware state, a
    telegraph outside its band, a share setting made inert by another. Run it.

---

## See also

- **[Perception Profile](perception-profile.md)** — what every field actually does
- **[Archetype Cookbook](archetype-cookbook.md)** — hand-tuned recipes to build on
- **[Scale & Crowds](scale-and-crowds.md)** — what to do with the budget numbers
