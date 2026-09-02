# Adapters

**How APS asks your project for facts it cannot work out for itself.**

APS has no opinion about how your game stores health or tracks posture, and it must not require a particular health component, ability system or character base class. Where it needs one of those facts, it asks through an interface you implement on whatever object already owns the answer.

Every adapter is **optional**. An actor that implements none of them still perceives normally — APS falls back to what it can observe directly.

---

## Health — `APS Health Provider`

Used by the **Pain** sense to know how hurt the AI is.

| Function | Returns |
|---|---|
| **Get APS Health Fraction** | `1.0` untouched, `0.0` dead. Clamped for you |

=== "Blueprint"

    1. Open your health component (or the actor itself)
    2. **Class Settings → Interfaces → Add** → `APS Health Provider`
    3. Implement **Get APS Health Fraction**, return `Current / Max`

=== "C++"

    ```cpp
    class UMyHealthComponent : public UActorComponent, public IAPSHealthProvider
    {
        GENERATED_BODY()
    public:
        virtual float GetAPSHealthFraction_Implementation() const override
        {
            return MaxHealth > 0.f ? Current / MaxHealth : 0.f;
        }
    };
    ```

APS checks the actor first, then each of its components.

### If you implement nothing

APS falls back to searching components for a function named `Get Health Percent`, or `Get Health` alongside `Get Max Health`. That path still works, so existing projects need no changes.

!!! warning "Why the interface is worth the five minutes"
    The name search cannot tell the difference between *your* `Get Health Percent`
    and someone else's. It now verifies the signature before calling — a getter
    that takes arguments is refused rather than called blind — but a name is still
    not a contract. The interface is the version that cannot be wrong.

    Values above `1.0` are treated as a `0–100` percentage, since that convention
    is common enough to be worth handling.

---

## Posture — `APS Stance Provider`

Used by vision (how many sample points must be exposed before a target counts as seen) and by the [Player Behavior Model](player-behavior-model.md).

| Function | Returns |
|---|---|
| **Get APS Stance** | `Standing`, `Crouched`, or `Prone` |

APS resolves posture in this order:

1. An **APS Stance Provider** on the actor
2. An **APS Stance Provider** on any of its components
3. An **[APS Target Component](core-concepts.md)**'s `Stance` — including its auto-detect of a `Character`'s crouch
4. A `Character`'s `b Is Crouched`
5. Otherwise: nothing reported it

Implement the interface when posture lives somewhere APS cannot see — a custom movement component, a state machine, an ability system tag — or when you need prone, cover or swimming distinguished.

!!! info "Reported *Standing* is not the same as *nothing reported*"
    A `Character` that is not crouched is a real observation of standing. An actor
    with no posture at all is an absence of one, and APS treats the two
    differently: only the second falls back to guessing from movement speed.

    This is why a player standing perfectly still is no longer filed as sneaking.

---

## What adapters are not

They are not a plugin dependency and not a required setup step. If your project never implements one, nothing about APS changes — you simply get the fallback behaviour, which is what earlier versions always did.

They exist so that the honest answer is *available*, not so that it is mandatory.

---

## See also

- **[Pain & Damage](pain-and-damage.md)** — what the Pain sense does with health
- **[The Senses](senses.md)** — how stance affects visibility sampling
