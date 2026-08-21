# Events Reference

APS is event-driven. You almost never need to poll — bind or override the events you care about and let the system push to you.

## Two ways to receive events

### Option A — the Listener component (recommended)

**Add Component → APS Perception Listener** on the same actor as the Perception Core.

Then in the Event Graph, right-click and search the event name — e.g. `OnAIDetect` — and add **Event On AI Detect**. Done. No binding, no `Add Dynamic`, no Begin Play wiring. Exactly like the old `OnSeePawn` from `PawnSensing`.

Unimplemented events cost nothing.

```
Event On AI Detect (Target, Threat Level, Stimulus)
   └─► your logic
```

### Option B — binding the delegate

Bind on the Perception Core component itself. Useful when the receiver is a different object — an AIController, a HUD, a manager actor.

```
Event Begin Play
  └─► Get Component By Class (Perception Core)
        └─► Bind Event to On AIDetect
              └─► Custom Event: HandleDetect
```

Delegates and listener events both fire — you can use either or both.

> **Naming note:** the "target lost" delegate on the component is exposed as **On AILost Event** (to avoid a name clash), while the listener event is **On AI Lost**. Same moment, same parameters.

---

# Sense events

These fire **every tick the sense is active** — not just once. Use them for continuous reactions (aim tracking, head look-at, meters). For one-shot reactions use lifecycle events instead.

| Event | Parameters | Fires when |
|---|---|---|
| **On AI See** | `Target` (Actor), `Confidence` (float), `Distance` (float) | Vision — or Echolocation — has an active contact |
| **On AI Hear** | `Location` (Vector), `Loudness` (float), `Sound Type Name` (Name) | A sound passed every filter and was heard. `Sound Type Name` is the `Sound Name` field on your Sound Type Definition. |
| **On AI Smell** | `Location` (Vector), `Intensity` (float), `Scent Tag` (Name) | Scent above threshold. `Scent Tag` is the target's first actor tag starting with `Scent.` |
| **On AI Feel** | `Instigator` (Actor), `Contact Type` (enum), `Strength` (float) | Physical contact. `Bump / Grab / Explosion / Collision` |
| **On AI Sense Vibration** | `Location` (Vector), `Strength` (float), `Surface` (enum) | Ground vibration. `Any / Ground / Water / Metal` |

---

# Lifecycle events

These fire **once per transition** — the workhorses of AI behaviour.

| Event | Parameters | Fires when |
|---|---|---|
| **On AI Suspect** | `Target`, `Location` (Vector), `Stimulus` (enum) | Confidence crossed `Suspect Threshold`. *"Something's over there."* Turn head, play a questioning bark, walk over. |
| **On AI Detect** | `Target`, `Threat Level` (enum), `Stimulus` (enum) | Confidence crossed `Detect Threshold`. Contact confirmed — alert, take cover, call it out. |
| **On AI Track** | `Target`, `Predicted Position` (Vector), `Confidence` (float) | Confidence crossed `Track Threshold` and `Min Track Duration` elapsed. Full engagement. |
| **On AI Lost** | `Target`, `Last Known` (Vector), `Predicted` (Vector), `Last Cover Actor` (Actor) | All senses went silent and the grace period expired. **Read `Get Loss Reason` here to decide *how* to search.** |
| **On AI Remember** | `Target`, `Location` (Vector), `Age Seconds` (float) | Belief has decayed into long-term memory. Stay alert, patrol near the location. |
| **On AI Forget** | `Target` | The target reached `Expired` — **or** stepped all the way back down to `Undetected`. Either way the AI has let go. Return to normal patrol. |

`Stimulus` (`EStimulusSource`) tells you which sense drove the transition: `Vision / Hearing / Smell / Damage / Shared Intel / Unknown`. Branch on it — an AI that *saw* you should react differently to one that only *heard* you.

---

# Brain events

| Event | Parameters | Fires when |
|---|---|---|
| **On AI Think Threat** | `Target`, `Level` (enum), `Score` (float) | Any threat level change for any target |
| **On Threat Identified** | `Target`, `Threat Level`, `Stimulus Source`, `Belief Record` | Threat **rose** to `High` or `Critical`. Fires on the increase only — not every tick while it stays there, and never on the way back down. This is your "commit to combat" signal. Delegate only. |
| **On AI All Clear** | — | Every active target is gone. Return to patrol, drop alert music. |
| **On AI Awareness Changed** | `Previous` (enum), `New` (enum) | The AI's overall awareness level changed |
| **On Target State Changed** | `Target`, `Old State`, `New State` | Every lifecycle transition, with both states. Delegate only. Use this instead of binding all six lifecycle events when you have a state machine. |
| **On Emotional State Changed** | `Old Dominant` (enum), `New Dominant` (enum) | The dominant emotion changed. Delegate only. |
| **On Attention Changed** | `Old Target` (Actor), `New Target` (Actor) | The AI committed to a different target. `Old Target` may be null on first acquisition; `New Target` is never null when it fires. **Cancel the current pursuit and re-plan here.** Delegate only. |
| **On AI Pain Reported** | `Pain Def` (asset), `Pain Level` (float) | `Report Pain From Definition` was called. **One per perception tick** — if you report several pain types in the same frame, the first is broadcast and the others are applied silently. Poll `Get Pain Level From Definition` for the rest. |
| **On AI Damaged** | `Instigator`, `Amount` (float), `Damage Type Tag` (Name), `Hit Location` (Vector) | Any damage event on the owner — `ApplyDamage`, `ApplyPointDamage`, `ApplyRadialDamage`. De-duplicated per frame. |

> The listener component's `On AI Pain Reported` has a slightly wider signature — `Pain Type` (Name), `Pain Level`, `Threshold Crossed`, `Pain Def` — because it predates the data-asset workflow. `Threshold Crossed` is `-1` when nothing was crossed.

---

# Squad events

| Event | Parameters | Fires when |
|---|---|---|
| **On AI Squad Alert** | `Target`, `Location` (Vector), `Threat` (enum) | A squadmate broadcast an alert, **or** shared intel that was actually new — shared knowledge only raises this event when the target is one the receiver had not registered (`Undetected`/`Expired`), or when the shared threat level is higher than what it already believed. Repeat shares of the same target do not spam it. |
| **On Combat Role Assigned** | `Role` (enum) | This AI was granted a combat role. Delegate only. |

---

# Fairness & replication events

| Event | Parameters | Fires when |
|---|---|---|
| **On AI Telegraph** | `Target`, `Confidence` (float) | Confidence crossed `Telegraph Threshold` — **before** the AI commits to full alert. Fires **once per target** and only re-arms once that target falls back to `Undetected` or `Expired`, so a momentary confidence dip does not retrigger the bark. Hook a "huh?" line or head-turn here. |
| **On Replicated State Changed** | — | Fires on **clients** when the replicated perception summary updates. Refresh your detection meter here instead of polling on Tick. |

---

## Choosing the right event

| You want to… | Use |
|---|---|
| Play a "what was that?" bark | `On AI Suspect` |
| Warn the player they are about to be spotted | `On AI Telegraph` |
| Enter combat | `On AI Detect` or `On Threat Identified` |
| Start shooting | `On AI Track` |
| Start searching | `On AI Lost` + `Get Loss Reason` |
| Give up and go back to patrol | `On AI Forget` or `On AI All Clear` |
| Drive a whole state machine | `On Target State Changed` |
| Cancel a chase because a better target appeared | `On Attention Changed` |
| React to being shot from an unknown direction | `On AI Damaged` |
| Update a HUD detection meter | `On AI See` (server) or `On Replicated State Changed` (client) |
| Swap alert music | `On AI Awareness Changed` |

---

## Print-everything debug nodes

Every event has a matching one-node print function in `APS | Debug`. Bind the event, drop in the matching node, wire the pins straight through — instant colour-coded screen and log output.

`Print_OnAISee`, `Print_OnAIHear`, `Print_OnAISmell`, `Print_OnAIFeel`, `Print_OnAISenseVibration`, `Print_OnAISuspect`, `Print_OnAIDetect`, `Print_OnAITrack`, `Print_OnAILost`, `Print_OnAIRemember`, `Print_OnAIForget`, `Print_OnAIThinkThreat`, `Print_OnThreatIdentified`, `Print_OnAIAllClear`, `Print_OnAIAwarenessChanged`, `Print_OnAIPainReported`, `Print_OnAIDamaged`, `Print_OnAISquadAlert`, `Print_OnTargetStateChanged`, `Print_OnEmotionalStateChanged`, `Print_OnCombatRoleAssigned`.

Colour coding: **cyan** senses · **green** lifecycle · **yellow** brain/threat · **orange** pain/emotion · **purple** squad · **white** state changes.

---

