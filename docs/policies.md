# Policies

**Three decisions APS makes for you, that you can take back.**

The shipped rules are good defaults, not opinions APS insists on. Each of the three is a Blueprintable class you can subclass and assign on the profile.

Leave a slot empty and the original built-in rule runs. There is no cost to ignoring this page.

| Slot | Answers |
|---|---|
| **Fusion Policy** | How several senses combine into one confidence |
| **Threat Policy** | How dangerous a target is |
| **Attention Policy** | Which target the AI commits to |

!!! info "The lifecycle stays in C++"
    The seven-state belief lifecycle — Undetected → Suspected → Detected →
    Tracked → Lost → Remembered → Expired — is not a policy slot. Its hysteresis
    and grace timing are what make belief stable, and making them overridable
    would mostly produce AI that flickers. Tune it through the profile's
    thresholds instead.

---

## Fusion Policy

**Fuse Confidence** (`Samples`, `Corroboration Bonus`) → confidence `0–1`

`Samples` has one entry per sense slot in profile order, each carrying `Sense ID`, `Confidence`, `Weight` and whether it is active.

The shipped rule takes the strongest sense and adds a bonus per additional sense that agrees. That is right for most games and wrong for some.

**When to replace it:** when you want *two weak senses to beat one strong one* — a rule the default cannot express, because it starts from the strongest and treats the rest as corroboration. A creature that hunts by combining faint smell and faint sound wants a sum, not a maximum.

## Threat Policy

**Score Threat** (`Record`, `Relationship`) → score `0–1`

The shipped rule weighs confidence, damage taken, how many senses agree, the relationship, and whether the target is closing.

The threat **level** is still derived from the profile's thresholds afterwards, so a policy only answers the interesting half.

**When to replace it:** when danger in your game is not about combat. A stealth game might care only whether the target has seen the AI back. A horror game might make an unarmed civilian the most threatening thing in the level.

## Attention Policy

**Select Attention Target** (`Candidates`, `Current`, `Time On Current`, `Stickiness Time`, `Switch Threshold`) → actor, or null

The shipped rule keeps the highest-scoring target and refuses to switch until the stickiness window has passed *and* a challenger beats it by a margin. That stops flicker, which is usually what you want.

**When to replace it:** when commitment should follow a rule of your own. A boss that always turns to whoever last hurt it. A guard dog that always chases the nearest thing regardless of threat. Return null for "nothing worth attending to".

---

## Writing one

=== "Blueprint"

    1. **Blueprint Class** → search for `APS Fusion Policy` (or Threat / Attention)
    2. Override the one function
    3. Assign it in the profile's **Policies** section

=== "C++"

    ```cpp
    UCLASS()
    class UMySummingFusion : public UAPSFusionPolicy
    {
        GENERATED_BODY()
    public:
        virtual float FuseConfidence_Implementation(
            const TArray<FAPSSenseSample>& Samples, float CorroborationBonus) const override
        {
            float Sum = 0.f;
            for (const FAPSSenseSample& S : Samples)
            {
                if (S.bIsActive) { Sum += S.Confidence * S.Weight; }
            }
            return FMath::Clamp(Sum, 0.f, 1.f);
        }
    };
    ```

Policies are stateless by design — they are asked a question and return an answer. Keep per-agent state on the component, not the policy.

---

## Beliefs about places

Not a policy, but the same era of change and worth knowing: a belief no longer has to be about an actor. APS tracks beliefs about **locations** too.

| Node | Does |
|---|---|
| **Report Location Belief** (`Location`, `Tag`, `Confidence`, `Accuracy`) | File a belief about a place |
| **Get Location Beliefs** | All of them |
| **Get Strongest Location Belief** | The one the AI is most sure of |
| **Clear Location Belief** (`Location`, `Tag`) | Drop one |

An unattributed noise — an explosion, a gunshot, a door — produces a belief about *where it came from*, not about whichever actor happened to be under evaluation at the time.

!!! note "This fixed a real bug"
    Anonymous sounds used to be scored against whatever target was being
    evaluated when they arrived, so one explosion made every bystander in earshot
    a suspect. Place beliefs are the structural fix.

    They are also kept out of the attention and all-clear paths, so a noise
    cannot steal an AI's focus from a person or stop **On AI All Clear** from
    firing.

---

## See also

- **[Core Concepts](core-concepts.md)** — what confidence and the lifecycle are
- **[Custom Senses](custom-senses.md)** — adding a sense rather than changing how they combine
- **[Profile Composition](profile-composition.md)** — where the policy slots live
