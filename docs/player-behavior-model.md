# Player Behavior Model

An AI that notices you always crouch, always flank from the left, and always hide behind the same crate — and eventually starts checking there first.

## The rule that makes it fair

**The model only records what the AI could legitimately perceive.** It does not read player input. It does not query the player's state directly. It observes movement speed and stance *while the AI has vision*, and it records positions *where the AI lost you*. Nothing else.

That constraint is what stops it feeling like cheating. If the AI never saw you crouch, it does not know you crouch.

---

## Setup

**Profile → Brain | Player Model:**

| Setting | Default | Meaning |
|---|---|---|
| `b Enable Player Behavior Model` | true | Observe player behaviour |
| `Min Engagements Required` | 3 | Engagements before the model is considered usable |
| `Player Crouch Speed Threshold` | 120 cm/s | Below this counts as crouching |
| `Player Sprint Speed Threshold` | 500 cm/s | Above this counts as sprinting |
| `b Enable Cross Session Memory` | false | Persist between play sessions |

The model updates automatically. There is nothing to call.

---

## Reading it

**Get Player Behavior Model** (`Target`) → `bool` + struct.

| Field | What it actually measures |
|---|---|
| `Crouch Ratio` | Fraction of observed ticks the target moved **slower than `Player Crouch Speed Threshold`**. Classification is purely speed-based — a player standing still counts here too. Read it as "moves slowly / holds still", not literally "is crouching". |
| `Sprint Ratio` | Fraction of ticks above `Player Sprint Speed Threshold` |
| `Walk Ratio` | Fraction of ticks between the two thresholds |
| `Stealth Ratio` | Fraction of engagements that ended with the target **behind the AI** (more than ~107° off its facing) when contact was lost |
| `Aggression Ratio` | The complement of the above — engagements that ended with the target in front. **`Stealth Ratio + Aggression Ratio` always equals 1.** They are two readings of one measurement, not independent signals. |
| `Recent Hide Locations` | Up to 5 **distinct** positions where contact was lost. A new entry is only stored if it is more than 200 cm from every existing one, so this is a list of separate hiding spots, not the last five losses. |
| `Custom Behavior Ratios` | Your own named ratios |
| `Engagement Count` | Distinct engagements observed |
| `b Has Enough Data` | True once `Engagement Count >= Min Engagements Required` |

**Always check `b Has Enough Data` before adapting.** That gate is the whole point of `Min Engagements Required` — it stops the AI drawing conclusions from a single encounter.

### When observations are recorded

- **Movement ticks** accumulate while the target is `Detected` or `Tracked`.
- **An engagement closes, and all ratios recompute, only on `Tracked → Lost`.** An encounter that peaks at `Detected` and then fades does not close the engagement — its observations roll into the next one. So `Engagement Count` counts *committed* engagements, which is usually what you want, but it means a cautious player who never lets the AI reach `Tracked` produces no model at all.

Because ratios only refresh at the end of a tracked engagement, the values you read mid-fight are from the *previous* engagement. That is fine for adaptation — you want to act on established history, not the encounter in progress.

---

## What to do with it

The plugin gives you the observation. What the AI *does* with it is your design. Some patterns that work:

### Check the favourite hiding spot first

```
Event On AI Lost (Target, Last Known, Predicted, Last Cover Actor)
  └─► Get Player Behavior Model (Target)
        └─► Branch: b Has Enough Data
              True → Recent Hide Locations : Last
                       → is it within 1500 cm of Last Known?
                          True → search THERE first, then Last Known
              False → search Last Known normally
```

### Adapt search speed to play style

```
Get Player Behavior Model (Target) → break
  ├─ Sprint Ratio > 0.6  → this player runs. Search wide and fast, cut off exits.
  ├─ Crouch Ratio > 0.6  → this player moves slowly. Search slow, check cover, listen more.
  └─ Stealth Ratio > 0.5 → this player breaks away behind me. Patrol facing outward, check your back.
```

### Adjust posture, not numbers

The tempting move is to secretly raise the AI's detection thresholds against a sneaky player. **Don't.** Players feel that as cheating even if they cannot name it.

Change *behaviour* instead: patrol routes, facing direction, search order, how long they linger, whether they double back. The AI gets harder to beat because it is looking in better places — not because its eyes got better.

### Custom behaviours

`Custom Behavior Ratios` is a free-form map you populate yourself. Define any key you like — `"UsedCover"`, `"FiredFromDistance"`, `"AlwaysFlankLeft"`, `"ThrowsDistractions"` — record observations from your own game logic, and read the resulting ratio back the same way as the built-in ones. No recompile, no engine changes.

---

## Cross-session memory

Turn on `b Enable Cross Session Memory` and the model persists between play sessions.

- **Saved to:** `YourProject/Saved/APS/PlayerModel/`
- **Filenames:** `<AIClassName>_<TargetID>.json`
- **Saved:** automatically on End Play (and manually via **Save Cross Session Memory**)
- **Loaded:** automatically on Begin Play (and manually via **Load Cross Session Memory**)
- **Only models with `b Has Enough Data` are written** — no noise from brief encounters
- **Never runs on clients** — server only

Manual control:

| Node | Use for |
|---|---|
| **Save Cross Session Memory** | Checkpoint saves, chapter transitions |
| **Load Cross Session Memory** | Loading a save game |
| **Clear Cross Session Memory** | New game, difficulty reset, or a "the enemy has forgotten you" story beat |
| **Reset Player Behavior Model** (`Target`) | Wipe one target's in-memory model without touching disk |

### What this unlocks

A boss you have fought three times already knows you dodge left. A stealth level replayed on a second run has guards who check the vent you used last time. A horror antagonist that learns your route through the house over a whole playthrough.

Two things to keep in mind:

- **Give the player a way to see it.** Adaptation the player cannot perceive is indistinguishable from difficulty drift. A line of dialogue — *"not this time"* — or a visibly changed patrol route makes it land.
- **Offer a reset.** Ship `Clear Cross Session Memory` on a "new game" or an accessibility toggle. Some players want a fresh start; some do not want the AI learning at all.

Because the format is plain JSON in `Saved/`, it is trivial to inspect during development and equally trivial for players to delete.

---

