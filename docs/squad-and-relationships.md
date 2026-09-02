# Squad & Relationships

Two independent systems:

- **Squad** — AI sharing what they know with each other and dividing up tactical roles.
- **Relationships** — how an AI classifies a target (enemy, teammate, feared) and how that feeds threat.

---

## Squad

### Setup

Squad membership is just a matching `Name`. Call **Set Squad ID** from Begin Play:

```
Event Begin Play
  └─► Get Component By Class (APS Core)
        └─► Set Squad ID  (New Squad ID = "Patrol_A")
```

Every AI with `Patrol_A` is now a squadmate. Change it at runtime to move an AI between squads. `None` means no squad, and disables all squad features for that AI.

### Automatic intel sharing

**Profile → Brain | Squad:**

| Setting | Default | Meaning |
|---|---|---|
| `Squad Share Range` | 3000 cm | Maximum range to share |
| `Min Threat To Share` | Low | Minimum threat level before sharing happens |
| `b Auto Share On Detect` | true | Share automatically at `Detected` |
| `b Auto Share On Track` | false | Share at `Tracked` instead (only used if share-on-detect is off) |

**Auto-share on Detect = horde behaviour.** One zombie sees you, the pack converges. Perfect for infected, wolves, insects.

**Both false = tactical behaviour.** Nothing is shared unless you explicitly call `Share Target With Squad` — from a radio animation, after a "contact!" bark, or only when the AI has actually finished a call-out. This is what makes military AI feel disciplined instead of telepathic.

### Manual sharing

| Node | What it sends | Use for |
|---|---|---|
| **Share Target With Squad** (`Target`) | The **full belief record** — position, confidence, threat, velocity, loss data | "I have confirmed contact, here is everything I know" |
| **Broadcast Alert To Squad** (`Target`, `Alert Location`, `Threat Level`) | A **position and threat level only** | "I heard something over there" — no confirmed target yet |

#### What the receiver actually gets

`Share Target With Squad` writes into the receiver's belief record:

- **Position, predicted position and velocity** are always overwritten — shared intel is assumed fresher.
- **Cover data** is copied if the sender saw the target take cover.
- **Confidence** is seeded to `max(sender's smoothed confidence, receiver's Suspect Threshold)` — but **only if that is higher than what the receiver already believes.** Direct sensing is never overridden downward.
- **Threat level and score** take the higher of the two. `b Is Known Threat` ORs in. Relationship is copied.

**On AI Squad Alert** fires on the receiver only when the intel is genuinely new — the target was `Undetected`/`Expired`, or the shared threat level exceeds what the receiver already had. Repeat shares of the same target do not re-fire it, so you can safely leave auto-share on.

Shared intel arrives with `Stimulus Source = Shared Intel`, so the receiver knows it did not perceive this itself:

```
Event On AI Detect (Target, Threat Level, Stimulus)
  └─► Branch: Stimulus == Shared Intel
        True  → move to the location cautiously, do not shoot yet
        False → I saw this myself — engage
```

That single branch is the difference between a squad that converges intelligently and one where everybody instantly headshots you through a wall.

### Combat roles

Roles are **exclusive per squad** — only one AI holds each role at a time.

`ECombatRole`: `None`, `Approacher`, `Flanker`, `Suppressor`, `Investigator`, `Support`.

| Node | Description |
|---|---|
| **Request Combat Role** (`Role`) → `bool` | Claim a role. Returns false if a squadmate holds it, or if the role is not in the profile's `Eligible Roles`. |
| **Release Combat Role** | Give it back — do this when the AI dies, retreats, or loses the target |
| **Get Combat Role** | What this AI currently holds |
| **On Combat Role Assigned** (`Role`) | Fires when a role is granted |

`Eligible Roles` on the profile restricts what an archetype may claim — a heavy gunner can be `Suppressor` or `Approacher` but never `Flanker`. An empty array means any role.

#### A working pattern

```
Event On AI Detect
  └─► Sequence
        ├─► Request Combat Role (Flanker)
        │     True  → Set Blackboard "Role" = Flanker  (BT runs the flank branch)
        │     False → Request Combat Role (Suppressor)
        │               True  → Set Blackboard "Role" = Suppressor
        │               False → Set Blackboard "Role" = Approacher
        └─► ...

Event On AI Forget
  └─► Release Combat Role
```

Four guards spotting you now naturally produce one flanker, one suppressor and two approachers — with no squad manager actor and no central coordinator.

---

## Relationships

### The component

Add **APS Relationship** to the AI alongside the APS Core. It is entirely optional — without it every relationship resolves to `Unknown`.

| Setting | Meaning |
|---|---|
| `Team Relationships` | Map of team ID (uint8) → relationship. Uses `IGenericTeamAgentInterface` on the target's controller. |
| `Class Relationships` | Map of actor class → relationship. **Takes priority over team.** |
| `Default Relationship` | Used when no rule matches |

| Node | Description |
|---|---|
| **Get Relationship** (`Target`) | Resolve the relationship for an actor |
| **Set Relationship Override** (`Target`, `Relationship`) | Runtime override for one specific actor |

### The values

`ETargetRelationship`: `Unknown`, `Neutral`, `Friendly`, `Teammate`, `Enemy`, `HighValue`, `Feared`.

| Value | Meaning |
|---|---|
| `Neutral` | Civilians, wildlife — perceived but not threatening |
| `Friendly` | Allied faction, not in this squad |
| `Teammate` | Same squad |
| `Enemy` | Hostile — feeds threat score upward |
| `HighValue` | Priority target — a VIP, an objective carrier. Use it to bias sorting and behaviour. |
| `Feared` | Something this AI runs *from*. Drives the Fear emotion instead of Aggression. |

### Resolution order

1. **Runtime override** (`Set Relationship Override`)
2. **Class relationship** (`Class Relationships` map)
3. **Team relationship** (`Team Relationships` map, via `IGenericTeamAgentInterface`)
4. **Default relationship**

### How it feeds threat

Relationship contributes to the threat score at `Threat Weight Relationship` (default 0.10). `Enemy` and `HighValue` push threat up; `Friendly` and `Teammate` push it down.

More importantly, it is the cleanest branch in your behaviour code:

```
Event On AI Detect (Target, Threat Level, Stimulus)
  └─► Switch on ETargetRelationship (Get Relationship (Target))
        ├─ Enemy     → engage
        ├─ Feared    → flee, Set Fear Input 1.0
        ├─ HighValue → call it in, prioritise
        ├─ Neutral   → ignore, continue patrol
        └─ Teammate  → ignore
```

### Runtime changes

`Set Relationship Override` handles the cases a static map cannot:

- The player disguises as a guard → override to `Friendly`
- The disguise is blown → override to `Enemy`
- An NPC is recruited mid-mission → override to `Teammate`
- A boss enters its enrage phase → override the player to `Feared` on nearby minions

---

## Debugging squads

The debug library has a dedicated squad toolkit under `APS | Debug | Squad`. All of it is compiled out of Shipping builds.

| Node | What it does |
|---|---|
| **Debug Print Squad State** (`Agent`) | Squad ID, every member, their distance, whether they are in share range, and their current role. Run from one AI to verify the squad is wired up. |
| **Debug Trace Squad Share Path** (`Sender`, `Target`) | Dry run: checks step by step — squad ID set? same squad? in range? above `Min Threat To Share`? — and prints a per-member verdict with the exact failure point. **Start here when sharing is not working.** |
| **Debug Print Squad Beliefs** (`Agent`, `Target`) | What every squad member currently believes about one target. Run after a share to confirm it landed. |
| **Debug Simulate Squad Share** (`Sender`, `Target`, `Receiver`) | Fire a share manually without the receiver detecting anything |
| **Debug Simulate Squad Alert** (`Receiver`, `Target`, `Location`, `Threat`) | Fire `On AI Squad Alert` on one AI in isolation, to test its response |
| **Debug Force Full Squad Share** (`Sender`, `Target`) | Share to everyone, bypassing range and threat gates. Use to test the receive side without fighting setup conditions. |
| **Debug Watch Squad** (`Agent`) | Call in Event Tick on one AI for a live fixed-key HUD panel — every member's name, awareness, top target and role, overwriting the same lines instead of spamming. |

---

