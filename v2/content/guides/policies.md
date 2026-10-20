---
title: Policies & adapters
description: Replace three decisions APS makes - how senses combine, how dangerous a target is, which target it commits to - with your own Blueprint, and tell APS your game's health and posture through two small interfaces.
local: BP_SummingFusion, BP_LastHitAttention, UMySummingFusion
---
<div class="kicker">Guide</div>

# Policies & adapters

APS's built-in rules are good defaults, not opinions it insists on. **Policies** replace three of its decisions; **adapters** let it ask your game for facts it can't work out itself.

::: fast
- A **policy** is a Blueprint class with one function. Assign it in the profile's **Policies** and it replaces the built-in rule; leave the slot empty and the built-in rule runs at no cost.
- **APS Fusion Policy**: how senses combine. **APS Threat Policy**: how dangerous a target is. **APS Attention Policy**: which target it commits to.
- **Adapters**: implement **APSHealth Provider** or **APSStance Provider** on whatever already knows the answer.
:::

## Policies

| Profile slot (Policies) | Blueprint parent | The function you write | It decides |
|---|---|---|---|
| `Fusion Policy` | **APS Fusion Policy** | **Fuse Confidence** (Samples, Corroboration Bonus) → 0 to 1 | How the senses' readings become one confidence |
| `Threat Policy` | **APS Threat Policy** | **Score Threat** (Record, Relationship) → 0 to 1 | How dangerous a target is |
| `Attention Policy` | **APS Attention Policy** | **Select Attention Target** (Candidates, Current, Time on Current, Stickiness Time, Switch Threshold) → an actor | Which target it commits to |

To write one: **Blueprint Class** › search for the parent (APS Fusion Policy, for example) › override its one function › pick your class in the profile's slot. Each AI gets its own instance; keep anything that must persist between updates on the AI, not in the policy.

::: info The seven states stay as they are
Undetected through Expired is not a policy. Its margins and grace times are what keep belief stable; tune it with the profile's thresholds ([How APS thinks](../how-it-works.md#3-the-seven-states)).
:::

### Fusion: how senses combine

Called for every target, every update. **Samples** has one entry per sense slot, in the profile's order: `Sense ID`, `Confidence` (before weighting), `Weight` (the profile's `Sense Weights`) and `Is Active` (false when the sense is silent; it should then add nothing). The result is clamped to 0 to 1.

The built-in rule takes the best active sense and adds `Corroboration Bonus` for each other active one ([Confidence](../features/confidence.md#read-it-in-blueprint)). That never lets a silent sense drag confidence down, but two weak senses can never beat one strong one. **Replace it** when they should: a creature that hunts by faint smell plus faint sound wants a sum, not a maximum.

```
BP_SummingFusion › Fuse Confidence (Samples, Corroboration Bonus)
  Sum = 0
  For Each Sample: Branch Is Active → Sum += Confidence × Weight
  Return Clamp (Sum, 0, 1)
```

The same in C++, as a child of UAPSFusionPolicy:

```cpp
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
```

### Threat: how dangerous

**Record** is the whole belief (confidence, damage, state, velocity...); **Relationship** is resolved from **APS Relationship**. You return the score; APS still turns it into a **level** with the profile's thresholds, still fades damage, and still keeps Friendly, Teammate and Expired targets at None whatever you return.

The built-in score weighs confidence, damage taken, how many senses agree, the relationship and contact ([the formula](../how-it-works.md#9-threat-and-emotion)). **Replace it** when danger in your game isn't about fighting: a stealth game may care only whether the target has seen the AI back; a horror game may make an unarmed civilian the most dangerous thing in the level.

### Attention: which target

**Candidates** are the actors it holds beliefs about, best first (**Get Targets Sorted by Score**: never things or places). **Current** is the present target (may be none), **Time on Current** how long it has held it. Return the target, Current to keep it, or none for "nothing worth attention".

The built-in rule keeps the best-scoring target and won't switch until `Attention Stickiness Time` has passed **and** a rival beats it by `Attention Switch Threshold`: that stops flicker. A policy replaces **all** of it, stickiness included; the two settings are passed in so you can still honour them. **Replace it** for a boss that always turns to whoever hit it last, or a dog that always chases the nearest thing. **On Attention Changed** still fires when your choice changes.

## Adapters

APS doesn't require a particular health component, ability system or character class. Where it needs a fact like that, it asks through an interface you implement on whatever already owns the answer. Both are optional: without them APS falls back to what it can see for itself.

### Health: APSHealth Provider

Used by Pain Sense: low health dulls every sense ([Emotions & pain](../features/emotions.md#low-health-dulls-every-sense)).

1. Open your health component (or the character itself) › **Class Settings** › Interfaces › **Add** › APSHealth Provider.
2. Implement **Get APSHealth Fraction**: return current health ÷ max health (1 untouched, 0 dead; APS clamps it).

```cpp
class UMyHealthComponent : public UActorComponent, public IAPSHealthProvider
{
    GENERATED_BODY()
public:
    virtual float GetAPSHealthFraction_Implementation() const override
    {
        return MaxHealth > 0.f ? Health / MaxHealth : 0.f;
    }
};
```

APS asks the actor first, then each of its components. **Without the interface** it looks, on the actor then its components, for a function named GetHealthPercent (an answer above 1 is read as 0 to 100), or GetHealth (or GetCurrentHealth) with GetMaxHealth; only functions with no inputs that return a number count. That works for most projects, but a name isn't a contract: the interface can't be wrong.

### Posture: APSStance Provider

Implement **Get APSStance** (Standing, Crouched or Prone) when posture lives where APS can't see it: a custom movement component, a state machine, an ability tag. APS resolves a target's posture in this order:

1. **APSStance Provider** on the actor;
2. **APSStance Provider** on one of its components;
3. its **APS Target Component**'s `Stance` (with `Auto Detect Stance`, a Character's crouch);
4. a **Character**'s crouch;
5. otherwise nothing was reported.

**Where it matters:**

- **Vision's stance rule** (`Min Visible Points Crouched` and the others) reads posture **only through an APS Target Component** on the target: without one, every target counts as standing. With `Auto Detect Stance` on, it asks the order above and keeps the component's own `Stance` if the answer is Standing; with it off, it uses `Stance` as your code sets it.
- **The player model** ([Memory](../features/memory.md#it-learns-how-you-play)) counts crouched time from posture. A Character standing still is a real observation of standing; an actor with no posture at all is an absence of one, and only then does it guess from speed. That's why a player standing perfectly still isn't filed as sneaking.
