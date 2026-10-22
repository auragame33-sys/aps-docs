---
title: Custom senses
description: Add your own sense - thermal, radar, psychic, a motion sensor - as a Blueprint with one function, set how it loses a target from its class defaults, go to C++ for event-driven senses, and use the stimulus bus.
local: BP_Sense_Thermal, Thermal, Heat, USenseUnit_Radar, Radar, Stimulus.Custom.Psychic, Stimulus.Vibration, Stimulus.Sound.Explosion, Stimulus.Custom, PendingPsychicEvents
---
<div class="kicker">Guide</div>

# Custom senses

Anything you can express as *how sure am I that this target is there?* can be a sense: thermal, radar, magnetism, a motion sensor, psychic awareness. A custom sense joins the same pipeline as the built-in ones: it combines with them, drives the seven states, feeds threat, and shows in the Visualizer.

::: fast
- **Blueprint Class** › All Classes › **Sense Unit** as the parent.
- Override **Get Sense ID** (a name) and **Evaluate** (fill in **Out Result** for one target).
- Add the class to the profile's `Sense Classes`. Done.
:::

## In Blueprint

**1. Make the class.** Content Browser › right-click › **Blueprint Class** › All Classes › search Sense Unit › pick it as the parent. Name it BP_Sense_Thermal.

You can also parent to a built-in sense (**Smell Sense**, **Vision Sense**...) to change its own settings in Class Defaults: that is how the Senses page's bloodhound gets a stronger nose ([Smell](../features/senses.md#smell)).

**2. Get Sense ID.** Override it and return a unique name, Thermal. It's what **Get Sense Contributions** and the Visualizer show.

**3. Evaluate.** Override it: it is called for **one target at a time**, each time the sense updates.

| Input | What it is |
|---|---|
| Context | The **Perception Context**: the AI's location, rotation, eye location and eye forward, the delta time, light and weather where it stands, the target's location and velocity, and whether the AI is off-screen |
| Profile | The AI's profile: read any setting |
| Target | The actor being evaluated |

Fill in **Out Result** (a **Perception Sense Result**): drag from the Return Node's Out Result pin and pick **Make Perception Sense Result**.

| Field | Meaning |
|---|---|
| `Is Active` | **Required.** True when the sense detects the target now; false and the rest is ignored |
| `Confidence` | 0 to 1: how sure this sense is |
| `Estimated Location` | Where it thinks the target is: a vague sense should be off by a bit |
| `Location Accuracy` | 0 to 1: how precise that is (the position of a belief comes from the most precise active sense) |
| `Raw Signal Strength` | For your own debugging |
| `Sense ID` | Your sense's name |

```
Evaluate (Context, Profile, Target)
  Distance   = Vector Distance (Context › Owner Location, Context › Target Location)
  Branch: Distance > 3000 → return (Out Result left empty)
  Heat       = the target's heat (a tag, a component, a variable: your game)
  Confidence = (1 − Distance ÷ 3000) × Heat
  Out Result: Is Active = Confidence > 0.1, Confidence, Estimated Location = Target Location,
              Location Accuracy = 0.8, Sense ID = Thermal
```

**4. Add it** to the profile's `Sense Classes` (up to 8 senses). Optionally weight it in `Sense Weights` and set how often it runs in `Sense Intervals`.

### Its class defaults: the Sense Contract

A sense made directly from **Sense Unit** declares how it behaves in its Class Defaults, **Sense Contract**:

| Setting | Default | What it does |
|---|---|---|
| `Default Interval` | 0.1 | Seconds between updates, unless the profile's `Sense Intervals` says otherwise |
| `Max Sensing Range` | 0 | How far it reaches, in cm. **Set it** if it reaches further than vision and hearing: only targets inside the largest range of the AI's senses are evaluated at all |
| `Loss Grace Time` | 0.3 | Seconds of silence before the target can be lost |
| `Allows Direct Lost Cut` | Off | On: straight to Lost when the grace ends, like vision. Off: steps down through the states |
| `Sense Loss Reason` | SensorDropout | The loss reason written when this sense is the one that lost the target |
| `Subscribed Stimulus Tags` | (none) | Stimulus bus prefixes it listens to (receiving them needs C++: below) |

A custom sense isn't in the profile's **Loss** settings, so these are its loss rules; its belief fades at the normal rate.

::: warn These do nothing on a child of a built-in sense
Vision, Hearing, Smell, Touch, Vibration, Damage, Pain and Echolocation answer these in C++ and ignore the Sense Contract. On a Blueprint child of Vision Sense, setting them changes nothing; use the profile's settings instead.
:::

### What a Blueprint sense can't do

| | Blueprint | C++ |
|---|---|---|
| Detection (**Evaluate**), **Get Sense ID**, your own settings | Yes | Yes |
| Update rate, weight, range, loss rules, stimulus tags | Yes (Sense Contract, profile) | Yes |
| React when a stimulus arrives | No | **OnStimulusReceived** |
| Event-driven ("Report X" style) senses | No | Yes |
| Senses about the AI itself (no target loop), like Pain | No | Yes |
| Fire a sense event (**On AI See**, ...) | No: the state events (**On AI Suspect** and the rest) still fire | **GetSenseDelegatePayload** |
| Beliefs about places | No | **CollectLocationObservations** |

A custom sense's **Stimulus** on **On AI Suspect** and **On AI Detect** reads Unknown: tell it apart with **Get Sense Contributions**.

## In C++

Make a child of USenseUnit and override what you need:

```cpp
UCLASS(BlueprintType, Blueprintable, DisplayName = "Radar Sense")
class MYGAME_API USenseUnit_Radar : public USenseUnit
{
    GENERATED_BODY()
public:
    virtual FName GetSenseID_Implementation() const override { return FName("Radar"); }
    virtual float GetDefaultInterval()        const override { return 0.5f; }
    virtual float GetMaxSensingRange()        const override { return 8000.f; }
    virtual float GetLossGraceTime()          const override { return 1.0f; }
    virtual bool  AllowsDirectLostCut()       const override { return true; }

    virtual void Evaluate_Implementation(const FPerceptionContext& Context,
        const UPerceptionProfile* Profile, const AActor* Target,
        FPerceptionSenseResult& OutResult) override;
};
```

Each update, in this order:

| Function | When | For |
|---|---|---|
| PreTick (DeltaTime, Profile) | Once per AI, before the targets | Build-up, held state, reading the AI itself |
| CollectLocationObservations | Once per AI | Things perceived with nobody behind them: they become beliefs about places |
| Evaluate | Once per target | The detection |
| GetSenseDelegatePayload | When it's active for a target | Which sense event to fire (a payload with no type fires none) |
| PostTickFlush | After all targets | Clear per-update caches |

The APS Core never casts to a particular sense: everything sense-specific lives in the sense class, so adding one changes nothing else. Other overrides:

| Override | For |
|---|---|
| IsEventDriven, HasPendingEvent, ConsumePendingEvent | Senses fed by reports instead of polling |
| ConsumePendingEventFor (Target, OutResult) | Hand a pending event only to the target that caused it (Damage and Touch do) |
| HasPendingStimulusFrom (Actor) | Give that actor a target slot ahead of a crowd, so its stimulus isn't lost |
| GetLossReasonFor (LastResult) | A loss reason per target, from the sense's last answer (vision uses what blocked it) |
| IsOwnerInternal, ConsumePendingOwnerPayload | A sense about the AI itself, like Pain |
| GetStimulusTags, OnStimulusReceived | The stimulus bus |
| TickFatigue, GetFatigueMultiplier | A sense that tires with use |
| CountWallsBetween | A helper: solid things between two points, each counted once |

::: tip Read Smell Sense
SenseUnit_Smell.h and its .cpp are commented as a worked example of a complete custom sense.
:::

## The stimulus bus

A broadcast channel for your own signals: **Emit Stimulus** (callable from any Blueprint, no target needed) with an **APSStimulus Event**, and every sense that listens for a matching tag **prefix** receives it.

| Field | Default | Meaning |
|---|---|---|
| `Stimulus Tag` | | A dotted name; a sense listening for Stimulus.Custom gets Stimulus.Custom.Psychic |
| `Location` | | Where it happened |
| `Source` | | Who caused it (may be none) |
| `Strength` | 1 | 0 to 1 |
| `Radius` | 1500 | AI further than this are skipped |
| `Max LODTier` | 2 | AI at a higher (cheaper) detail tier are skipped |
| `Requires Clear Path` | Off | Trace from it to each AI and skip blocked ones: costly, for things walls should stop |
| `Team Filter` | Off | Skip AI on the source's team |

Delivery runs cheapest first: radius, detail tier, team, then the wall trace.

**Who listens:** only **Vibration Sense** among the built-in senses (Stimulus.Vibration, and Stimulus.Sound.Explosion: blasts shake the ground), and it turns them into beliefs about the **place**. **Hearing doesn't listen to the bus**: it hears only **Emit Sound** and **Emit Sound at Location** ([Hearing](../features/hearing.md)). Your own C++ sense subscribes like this:

```cpp
virtual TArray<FName> GetStimulusTags() const override
{
    return { FName(TEXT("Stimulus.Custom.Psychic")) };
}

virtual void OnStimulusReceived(const FAPSStimulusEvent& Event) override
{
    PendingPsychicEvents.Add(Event);   // use it in the next PreTick or Evaluate
}
```

A Blueprint sense can list tags in `Subscribed Stimulus Tags`, but receiving is C++ only, so nothing happens when one arrives. For a Blueprint reaction to your own signal, call **Set Target Confidence** or **Report Location Belief** on the AI you want to affect.

## Ideas

| Sense | How |
|---|---|
| Thermal | Distance falloff × a heat value on the target; ignores light |
| Motion sensor | Only targets above a speed (Context › Target Velocity). Freeze and you vanish |
| Mana sight | Reads a mana value off the target: a spellcaster glows, a rogue doesn't |
| Psychic | Ignores range and walls, but with a very low `Location Accuracy`: it knows you exist, not where |
| Radar | Long range, low confidence, poor accuracy: an early warning for a squad |
| Blood scent | Confidence grows with the target's missing health |
| Footprints | Footprint actors with **APS Target Component**s and a short-range sense: the AI follows a real trail |
