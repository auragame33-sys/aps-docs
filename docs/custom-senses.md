# Custom Senses

Radar, thermal vision, magnetic detection, psychic awareness, motion sensors, electrical field detection — anything you can express as *"how confident am I that this target is there?"* can be a sense.

Custom senses plug into the same pipeline as the built-in ones. Fusion, memory, lifecycle, threat and debug all work automatically.

---

## The Blueprint path

### Step 1 — Create the class

Content Browser → right-click → **Blueprint Class** → expand **All Classes** → search `SenseUnit` → pick it as the parent.

Name it `BP_Sense_Thermal`.

!!! tip
    You can also parent to an existing sense such as `SenseUnit_Vision` or `SenseUnit_Smell` to inherit its behaviour and change only its default values, or add extra logic on top.

### Step 2 — Override Get Sense ID

In the Class Defaults / Functions panel, **Override → Get Sense ID**. Return a unique name:

```
Get Sense ID → Return Value = "Thermal"
```

This name appears in `Get Sense Contributions` and in the debug overlay, so make it readable.

### Step 3 — Override Evaluate

**Override → Evaluate.** You receive:

| Input | What it is |
|---|---|
| `Context` | `Perception Context` — owner actor, location, rotation, eye location, **eye forward**, world, delta time, ambient light, weather modifier, target location, target velocity, off-screen flag, and the full environment state |
| `Profile` | The active Perception Profile — read any setting from it |
| `Target` | The actor being evaluated (one call per target) |
| `Out Result` | The `Perception Sense Result` you fill in |

Fill in `Out Result`:

| Field | Meaning |
|---|---|
| `b Is Active` | **Required.** True if this sense is detecting the target right now. False and the rest is ignored. |
| `Confidence` | 0–1 — how strongly this sense believes |
| `Raw Signal Strength` | Pre-falloff signal, for your own debugging |
| `Estimated Location` | Where this sense thinks the target is — imprecise senses should offset this |
| `Location Accuracy` | 0–1 — how precise that position is |
| `Sense ID` | Your sense name |

#### A working thermal sense

```
Event Evaluate (Context, Profile, Target, Out Result)
│
├─ Is Valid (Target)? ── No ──► return (leave Out Result reset)
│
├─ Distance = Vector Distance (Context.Owner Location, Target Location)
│
├─ Branch: Distance > 3000 ── True ──► return
│
├─ Heat = Get Actor Tag Value ("Heat") or default 1.0
│
├─ Falloff = 1.0 - (Distance / 3000)
│
├─ Confidence = Falloff × Heat
│
└─ Set Out Result:
     b Is Active       = Confidence > 0.1
     Confidence        = Confidence
     Estimated Location= Target Location
     Location Accuracy = 0.8
     Sense ID          = "Thermal"
```

### Step 4 — Add it to a profile

Open your Perception Profile → `Sense Classes` → add `BP_Sense_Thermal`.

Optionally set its weight in `Sense Weights` and its tick rate in `Sense Intervals`.

**Done.** It now fuses with every other sense, drives the lifecycle, feeds threat assessment, appears in `Get Sense Contributions`, and shows up in the Sense debug mode.

---

### What Blueprint can and cannot override

| Feature | Blueprint | C++ |
|---|---|---|
| `Evaluate` — the detection logic | ✅ | ✅ |
| `Get Sense ID` | ✅ | ✅ |
| Custom `EditAnywhere` properties on the sense | ✅ | ✅ |
| Tick rate | ✅ `Default Interval` in class defaults, or the profile's `Sense Intervals` map | ✅ |
| Confidence weight | ✅ *via the profile's `Sense Weights` map* | ✅ |
| Loss grace time / direct cut / loss reason | ✅ `Sense Contract` class defaults | ✅ |
| Max sensing range (extends target gathering) | ✅ `Max Sensing Range` class default | ✅ |
| Listing the stimulus tags to receive | ✅ `Subscribed Stimulus Tags` | ✅ |
| Reacting when a stimulus arrives | ❌ | ✅ `OnStimulusReceived` |
| Event-driven mode (`Report X` style APIs) | ❌ | ✅ |
| Owner-internal senses (no target loop) | ❌ | ✅ |
| Firing a built-in sense event (`On AI See` etc.) | ❌ | ✅ |
| Reporting beliefs about places from a sense | ❌ | ✅ `CollectLocationObservations` |

#### The Sense Contract

Every Blueprint sense derived from `Sense Unit` has a **Sense Contract** section in its Class Defaults. Those values are what the base class reports to the core, so a Blueprint sense declares how it behaves without a line of C++:

| Property | Default | Meaning |
|---|---|---|
| `Default Interval` | 0.1 s | Seconds between evaluations, unless the profile's `Sense Intervals` overrides it |
| `Max Sensing Range` | 0 | Furthest reach in cm. Feeds the candidate-gathering radius, so a sense that reaches further than vision must say so or its targets are never handed to `Evaluate`. 0 adds nothing |
| `Loss Grace Time` | 0.3 s | Seconds of silence before the target may be considered lost |
| `b Allows Direct Lost Cut` | false | Jump straight to `Lost` when grace expires, the way vision does, instead of fading down through the states |
| `Sense Loss Reason` | `SensorDropout` | Written to the belief record when this sense is the one that lost the target |
| `Subscribed Stimulus Tags` | empty | Prefixes this sense receives from the stimulus bus |

!!! warning "The built-in senses ignore these fields"
    Vision, Hearing, Smell, Touch, Vibration, Damage, Pain and Echolocation answer these questions in C++. Setting `Sense Contract` values on a Blueprint child of `Vision Sense` does nothing; they apply to senses derived directly from `Sense Unit`.

So a thermal sense that should reach 8000 cm sets `Max Sensing Range` to 8000, and targets that far out reach `Evaluate` whatever the profile's vision range says. The remaining gaps, reacting to a stimulus and firing a built-in sense event, need the short C++ path below.

---

## The C++ path

Subclass `USenseUnit` and override what you need:

```cpp
UCLASS(BlueprintType, Blueprintable, DisplayName = "Sense: Radar")
class MYGAME_API USenseUnit_Radar : public USenseUnit
{
    GENERATED_BODY()
public:
    virtual FName GetSenseID_Implementation() const override { return FName("Radar"); }
    virtual float GetDefaultInterval()       const override { return 0.5f; }
    virtual float GetMaxSensingRange()       const override { return 8000.f; }

    virtual float       GetLossGraceTime()    const override { return 1.0f; }
    virtual bool        AllowsDirectLostCut() const override { return true; }
    virtual ELossReason GetLossReason()       const override { return ELossReason::SensorDropout; }

    virtual void Evaluate_Implementation(
        const FPerceptionContext& Context,
        const UPerceptionProfile* Profile,
        const AActor* Target,
        FPerceptionSenseResult& OutResult) override;
};
```

The pipeline contract, called in this order every tick:

| Method | When | Use for |
|---|---|---|
| `PreTick(DeltaTime, Profile)` | Once per AI, before the target loop | Accumulators, persistent state, sampling the owner |
| `Evaluate(...)` | Once per target | The detection itself |
| `GetSenseDelegatePayload(...)` | If the sense is active | Which built-in event to fire |
| `PostTickFlush()` | After all targets | Clear per-tick caches |

`PerceptionCore` **never casts to a specific sense type**. Everything sense-specific lives in the sense class, which is why adding one requires no changes anywhere else.

#### Optional overrides

| Override | Purpose |
|---|---|
| `IsEventDriven()` / `HasPendingEvent()` / `ConsumePendingEvent()` | Push-based senses that react to reported events rather than polling |
| `IsOwnerInternal()` | Runs once per AI instead of once per target — like the Pain sense |
| `ConsumePendingOwnerPayload()` | Fire an event from an owner-internal sense |
| `GetStimulusTags()` / `OnStimulusReceived()` | Subscribe to the stimulus bus |
| `TickFatigue()` / `GetFatigueMultiplier()` | Senses that tire with use |
| `CountWallsBetween()` *(inherited helper)* | Wall counting for occlusion-aware senses |
| `CollectLocationObservations()` | Report authorless observations that the core turns into beliefs about places |

#### Firing a built-in event

```cpp
virtual FSenseDelegatePayload GetSenseDelegatePayload(
    const FPerceptionContext& Context, const AActor* Target,
    const FPerceptionSenseResult& Result) const override
{
    FSenseDelegatePayload P;
    P.DelegateType = ESenseDelegateType::AISee;   // radar reads as "sight"
    P.Distance     = FVector::Dist(Context.OwnerLocation, Result.EstimatedLocation);
    return P;
}
```

Return a payload with `DelegateType = None` to fire nothing — that is what the Damage sense does.

!!! tip "The Smell sense is the reference implementation"
    `SenseUnit_Smell.h` and its `.cpp` are deliberately over-commented as a worked example of the full custom-sense workflow. Read them before writing your own.

---

## The stimulus bus

A general-purpose broadcast channel. Emit a tagged stimulus from anywhere and every sense that registered a matching tag prefix receives it — without touching `PerceptionCore`.

### Emitting (Blueprint or C++)

```
Make FAPS Stimulus Event
  Stimulus Tag        = "Stimulus.Custom.Psychic"
  Location            = my location
  Source              = Self
  Strength            = 0.8
  Radius              = 2500
  Max LOD Tier        = 3
  b Requires Clear Path = false
  b Team Filter       = true
    └─► Emit Stimulus (World Context = Self)
```

| Field | Meaning |
|---|---|
| `Stimulus Tag` | Dot-hierarchy name. Senses register a **prefix**, so `Stimulus.Sound` catches `Stimulus.Sound.Footstep`. |
| `Location` | World origin |
| `Source` | Causing actor. May be null for environmental stimuli. |
| `Strength` | 0–1 intensity |
| `Radius` | Agents beyond this are skipped |
| `Max LOD Tier` | 0–4. Match to importance: footstep 1, gunshot 3, explosion 4. |
| `b Requires Clear Path` | Run a wall trace before delivering. **Expensive** — only for stimuli where geometry matters (sound, heat, light). False lets it pass through walls (vibration, psychic, magnetic). |
| `b Team Filter` | Skip agents on the same team as the source |

The delivery pipeline runs cheapest-first: radius cull → LOD tier → team filter → wall trace → deliver.

### Built-in tag namespaces

| Tag | Received by |
|---|---|
| `Stimulus.Sound`, `.Footstep`, `.Gunshot`, `.Explosion`, `.Generic` | Hearing |
| `Stimulus.Vibration`, `.Footstep`, `.Blast`, `.Generic` | Vibration |
| `Stimulus.Sound.Explosion` | **Also** Vibration — explosions shake the ground |
| `Stimulus.Custom.*` | Your own C++ senses |

Your game can invent any tag it likes. There is no registration step.

### Subscribing

```cpp
virtual TArray<FName> GetStimulusTags() const override
{
    return { FName(TEXT("Stimulus.Custom.Psychic")) };
}

virtual void OnStimulusReceived(const FAPSStimulusEvent& Event) override
{
    PendingPsychicEvents.Add(Event);   // consume it in your next Evaluate / PreTick
}
```

A Blueprint sense can list the tags it wants in `Subscribed Stimulus Tags`, but the delivery callback is C++ only, so nothing happens when one arrives. If you need a Blueprint-driven reaction to a custom stimulus, emit it *and* separately call `Set Target Confidence` or `Report Location Belief` on the AI you want to affect.

---

## Ideas worth building

| Sense | Approach |
|---|---|
| **Thermal** | Distance falloff × a `Heat` value from an actor tag or component. Ignores light and most occlusion. |
| **Motion sensor** | Only registers targets above a speed threshold. Freeze and you vanish. |
| **Electrical field** | Confidence from proximity to powered devices the target is touching. |
| **Magic / mana sight** | Reads a `Mana` value off the target — a spellcaster glows to it, a rogue does not. |
| **Psychic** | Ignores range and occlusion entirely, but with very low `Location Accuracy` so the AI knows you exist without knowing where. |
| **Radar** | Long range, sweeping arc, low confidence, poor location accuracy. Great as a squad-wide early warning. |
| **Blood scent** | Confidence scales with the target's missing health. The more hurt you are, the further it tracks you. |
| **Footprint tracking** | Register footprint actors as perceivable and give the sense a short range — the AI follows a physical trail. |

Every one of these is a `Blueprint Class` and one `Evaluate` override.

---

