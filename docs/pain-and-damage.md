# Pain & Damage

Two separate systems that work well together:

- **Damage sense** — being hurt makes the AI aware of who hurt it.
- **Pain sense** — being hurt makes the AI *worse at perceiving*.

Neither manages health. Your health system stays yours.

---

## Damage

### Setup

Add **Damage Sense** to your profile's `Sense Classes`. That is the entire setup.

Every UE5 damage path is wired automatically on Begin Play:

- `Apply Damage`
- `Apply Point Damage`
- `Apply Radial Damage`

Events are de-duplicated per frame, so the engine's habit of firing both `OnTakeAnyDamage` and `OnTakePointDamage` for one hit does not double-count.

### Two modes

**Profile → Ranges → `b Auto Confidence From Damage`**

#### True (default) — automatic

Confidence toward the instigator is set to:

```
Confidence = clamp(DamageAmount / 100, 0, 1)
```

**100 points in one hit means instant full detection.** Several hits from the same instigator inside one perception tick are summed before the division. Calibrate against your own damage numbers — if a rifle round does 25, one shot buys 0.25 confidence: enough to cross `Suspect Threshold` (0.15) but not `Detect Threshold` (0.35). Two shots and the guard has you.

The instigator is added to the target list **regardless of range**, so a sniper far outside vision and hearing range still becomes a tracked target the moment they connect. The hit is reported with a `Location Accuracy` of 0.95.

#### False — you decide

Damage fires **On AI Damaged** and nothing else. This is the mode you want for hardcore stealth, where a silenced hit should not reveal the shooter.

```
Event On AI Damaged (Instigator, Amount, Damage Type Tag, Hit Location)
  └─► Branch: Damage Type Tag == "Silenced"?
        True  → Report Pain From Definition (DA_Pain_Bleeding, 0.3)     // hurt, but blind
        False → Set Target Confidence (Instigator, 0.9)                 // knows exactly who
```

`Damage Type Tag` is derived from the `UDamageType` class name — create `DamageType_Fire`, `DamageType_Silenced`, `DamageType_Explosive` subclasses and you get free routing.

### Threat weighting

Damage received from a target feeds the threat score at `Threat Weight Damage Received` (default 0.30 — the second-largest term). The record also tracks `Damage Received From Target`, `Damage Dealt To Target`, `b Is Known Threat` and `Encounter Count`.

`Threat Damage Decay Rate` controls how fast that contribution fades while the target is unsensed. Set it to `0` and the AI never forgets who shot it.

### Loss behaviour

Grace **8 s**, no direct cut, decay ×0.5. An AI stays aware of a damage source for a long time — because a real one would.

---

## Pain

**Pain is perception impairment, not health.** Flashbang a guard and it should be temporarily near-blind. Set it on fire and it should be too distracted to hear well. Deafen it and it should still see fine.

The Pain sense is **owner-internal** — it evaluates the AI itself, once per tick, and never participates in the target loop.

### Setup

1. Add **Sense: Pain / Health** to `Sense Classes`.
2. Create one **Pain Type Definition** data asset per kind of pain.
3. Call **Report Pain From Definition** from your own damage/status code.

There is no array to register pain types in — you pass the asset directly to the node.

### Pain Type Definition

Content Browser → **Data Asset → PainTypeDefinition**.

| Field | Meaning |
|---|---|
| `Display Name` | Shown in the debug overlay |
| `Debug Color` | Overlay colour |
| `Decay Rate` | Level lost per second. `0.05` = bleeding lingers · `0.2` = burning fades · `1.0` = stun wears off fast · `0` = never decays (manual clear only) |
| `Sense Effects` | Array of *sense class → effect [0–1]*. At full pain, effect `1.0` drops that sense to its floor. |
| `Max Level` | Cap for this type. `0.5` caps at 50% no matter how many reports land. |
| `Amount Override` | If > 0, every report adds this fixed amount instead of the caller's value. Useful for binary pain types like `Stunned`. |

#### A useful set

**`DA_Pain_Flashbang`** — Decay `0.8` · Max `1.0` · Amount Override `1.0`
Sense Effects: `Vision Sense → 1.0`, `Hearing Sense → 0.7`
Total blindness for ~1.2 s, degrading back over the next second.

**`DA_Pain_Burning`** — Decay `0.2` · Max `1.0`
Sense Effects: `Vision Sense → 0.4`, `Hearing Sense → 0.3`
Distracted and unfocused while on fire.

**`DA_Pain_Bleeding`** — Decay `0.05` · Max `0.7`
Sense Effects: `Vision Sense → 0.3`
A long, slow degradation that persists through a whole fight.

**`DA_Pain_Deafened`** — Decay `0.3` · Max `1.0`
Sense Effects: `Hearing Sense → 1.0`
Stood next to an explosion. Sees fine, hears nothing.

**`DA_Pain_Smoke`** — Decay `0.5` · Max `1.0`
Sense Effects: `Vision Sense → 0.9`, `Smell Sense → 0.6`
Tear gas / smoke grenade. Hearing untouched, so sound-based stealth still matters.

### Using it

| Node | Purpose |
|---|---|
| **Report Pain From Definition** (`Pain Def`, `Pain Amount`) | Add pain. Fires `On AI Pain Reported` — but only **once per perception tick**, so if you report several types in one frame only the first raises the event. |
| **Get Pain Level From Definition** (`Pain Def`) | Current level 0–1 |
| **Get Total Pain Level** | **Sum** of all enabled types, clamped to 1. Two types at 0.6 each report 1.0. |
| **Clear Pain From Definition** (`Pain Def`) | Remove one type — a medkit, an extinguisher |
| **Clear All Pain** | Full reset |
| **Set Pain Type Enabled From Definition** (`Pain Def`, `b Enabled`) | Immunities — a fire elemental with `DA_Pain_Burning` disabled |

#### Wiring a flashbang

```
Grenade explodes
  └─► Sphere Overlap Actors (radius 800)
        └─► ForEach → Get Component By Class (APS Core)
              └─► Branch: Line Trace clear to grenade?
                    True → Report Pain From Definition (DA_Pain_Flashbang, 1.0)
```

Guards behind cover are unaffected. Guards looking at it are blind for a second. No special-case code in the AI — the perception system simply stops feeding it vision.

#### Reacting to pain

```
Event On AI Pain Reported (Pain Def, Pain Level)
  └─► Branch: Pain Level > 0.7
        True → play stagger montage, set blackboard "bImpaired" = true
```

Or poll it in a BT decorator: `Get Total Pain Level > 0.5` → run the "recover" branch.

### How degradation is calculated

```
start:          Deg = Lerp(SenseFloor, 1.0, HealthRatio)
per pain type:  Deg = max(Deg × (1 − PainLevel × Effect), SenseFloor)
applied:        SenseConfidence ×= clamp(Deg, SenseFloor, 1.0)
```

`SenseFloor` is `Pain Vision Floor` for the Vision sense and any Blueprint subclass of it, and **0 for every other sense**.

- `Pain Vision Floor` `0.0` — a fully blinded AI genuinely sees nothing. Dramatic, and correct for flashbangs.
- `Pain Vision Floor` `0.2` — the AI always retains a sliver of sight. Safer if yours would otherwise get stuck.

Pain types stack **multiplicatively**, so burning at 0.5×effect 0.4 combined with smoke at 0.8×effect 0.9 compounds rather than adding.

When pain suppresses a sense to effectively zero, APS clears that sense's active flag, so the memory system correctly starts its loss timer. A blinded AI actually *loses* you rather than freezing on a stale detection.

### Health-based degradation — and the automatic hook

The same function applies **health** degradation to *every* sense, not just vision. Because non-vision senses have a floor of 0, an AI at 50% health perceives at roughly half strength across the board.

That matters because **health is read automatically**. Every tick, the Pain sense asks the owner how hurt it is, in this order:

1. an **APS Health Provider** interface on the actor, then on any component ([Adapters](adapters.md)),
2. a function named `GetHealthPercent` returning a number,
3. `GetHealth` **and** `GetMaxHealth`,
4. `GetCurrentHealth` **and** `GetMaxHealth`.

If your health component exposes any of these, and most do, health-based sense degradation is **already running with zero setup**, and `Set Health Ratio` is overwritten each tick.

| Node | Purpose |
|---|---|
| **Set Health Ratio** (`Ratio`) | Feed a value manually. Only takes effect if nothing on the AI answers the health lookup above. |
| **Get Health Ratio** | Read the current value |
| **Get Pain State** | `Healthy` (>0.75) · `Wounded` (>0.40) · `Critical` (>0.15) · `Near Death` |

**If you do not want health affecting perception**, implement the interface and return 1, rename your accessor functions, or accept and tune the effect — it is often exactly what you want (a badly wounded guard genuinely should be worse at spotting you). Use `Get Pain State` as a cheap BT condition for "retreat when Critical".

---

## Combining the two

The natural pattern:

```
Event On AI Damaged (Instigator, Amount, Damage Type Tag, Hit Location)
  ├─► Switch on Name (Damage Type Tag)
  │     ├─ "Fire"      → Report Pain From Definition (DA_Pain_Burning, 0.6)
  │     ├─ "Explosive" → Report Pain From Definition (DA_Pain_Deafened, 0.8)
  │     └─ Default     → Report Pain From Definition (DA_Pain_Bleeding, Amount / 200)
  └─► Set Health Ratio (Current HP / Max HP)
```

Damage handles *who did it*. Pain handles *what it did to me*. Between them you get an AI that gets hurt, gets worse at its job, and remembers who is responsible.

---

