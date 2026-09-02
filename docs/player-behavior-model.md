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
| `Player Crouch Speed Threshold` | 120 cm/s | Below this counts as crouching — *fallback only*, see below |
| `Player Sprint Speed Threshold` | 500 cm/s | Above this counts as sprinting |

The model updates automatically. There is nothing to call.

!!! note "Posture is observed, not guessed from speed"
    The two speed thresholds are a **fallback**. When the AI can see the target's
    posture — a `Character`'s crouch state, an **APS Target Component**'s stance,
    or your own [stance adapter](adapters.md) — that posture decides the tally and
    speed is ignored.

    This matters because speed alone gets it wrong in both directions: a player
    walking carefully reads as crouching, and so does a player standing perfectly
    still. Only targets that expose no posture at all fall through to the
    thresholds above.

---

## Reading it

**Get Player Behavior Model** (`Target`) → `bool` + struct.

| Field | What it actually measures |
|---|---|
| `Crouch Ratio` | Fraction of observed ticks the target was **crouched or prone**, as reported by its posture. Only when nothing reports a posture does speed decide, and then anything slower than `Player Crouch Speed Threshold`, including standing still, lands here. |
| `Sprint Ratio` | Fraction of ticks above `Player Sprint Speed Threshold` |
| `Walk Ratio` | Everything else: upright and below the sprint threshold |
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

## The model lives for the session, and no longer

There is no save file. A freshly spawned AI is a fresh mind: it has met nobody
and has learned nothing until it perceives something itself.

This is deliberate. Persisting a behaviour model keyed to a runtime actor was
both unreliable and the wrong default — an AI that "already knows" the player at
the moment it spawns is difficult to reason about, impossible to test, and
almost never what a designer actually wanted.

| Node | Use for |
|---|---|
| **Get Player Behavior Model** (`Target`) | Read the ratios for one target |
| **Reset Player Behavior Model** (`Target`) | Wipe one target's model — a "the enemy has forgotten you" story beat, a difficulty reset, or an accessibility toggle |

!!! info "Want it to survive a save?"
    Read the ratios you care about with **Get Player Behavior Model**, write them
    into your own save game alongside everything else you persist, and feed them
    back through your own logic on load. APS does not decide what is worth
    keeping, because that decision belongs to your game — see
    [Memory & Recall](memory-and-recall.md) for the same principle applied to what
    an AI remembers.

### Adaptation the player cannot see is just difficulty drift

Whatever you drive from this model, give the player a way to perceive it. A line
of dialogue — *"not this time"* — or a visibly changed patrol route makes it
land. Silent adaptation is indistinguishable from the game getting harder for no
reason.

---

