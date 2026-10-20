---
title: Squads & teams
description: AI that share what they see within radio range, call in noises, divide combat roles, and know friend from foe - including a disguise that works because the guard takes you for one of its own.
local: Patrol_A, Role
---
<div class="kicker">Brain</div>

# Squads & teams

Guards that tell each other what they see, call in what they hear, split up the roles in a fight, and know who is on which side.

<div class="meta"><span><b>Set Squad ID</b> and the profile's <b>Brain › Squad</b></span><span>Teams: the <b>APS Relationship</b> component</span><span>Demo: the <b>Squad</b> wing, Q1 to Q4</span></div>

::: fast
![Room Q1: one guard radios what it saw](media/squads/share.mp4 "Room Q1. When one guard sees you, APS shares it with every squadmate inside its radio range (the circle): those guards come running; one outside the circle never hears.")
- Give AI the same **Squad ID** and they **share what they see**, within `Squad Share Range`.
- A guard that was **told** knows it: **Stimulus** is Shared Intel, so it can check rather than shoot.
- **Request Combat Role** splits a fight (one flanker, one suppressor) with no squad manager.
:::

## Squads

### Join a squad

A squad is just a matching name. Call **Set Squad ID** on each AI's APS Core (at Begin Play):

```
Event Begin Play
  └─► APS Core → Set Squad ID ("Patrol_A")
```

Every AI with Patrol_A is a squadmate. Change it while playing to move an AI to another squad; None takes it out of any squad, and turns every squad feature off for it.

### Sharing what it sees

| Setting (Brain › Squad) | Default | What it does |
|---|---|---|
| `Squad Share Range` | 3000 | How far, in cm, a share reaches: the squad's radio range |
| `Min Threat to Share` | Low | The least threat level before it shares |
| `Auto Share on Detect` | On | Share by itself when a target is Detected |
| `Auto Share on Track` | Off | Share at Tracked instead (only when share on detect is off) |

**Share on detect = a horde.** One zombie sees you, the pack converges: infected, wolves, insects. **Both off = discipline.** Nothing is shared until you call **Share Target with Squad**: after a radio animation, a "contact!" bark, or only once the call-out is finished. That is what makes soldiers feel disciplined rather than telepathic.

| Node | Sends | For |
|---|---|---|
| **Share Target with Squad** (Target) | Everything it believes about the target: position, confidence, threat, velocity, cover | "Confirmed contact, here's everything" |
| **Broadcast Alert to Squad** (Target, Alert Location, Threat Level) | A place and a threat level, no target needed | "I heard something over there" |

![Room Q2: a noise called in to the squad](media/squads/callin.mp4 "Room Q2. A guard hears your can land in the storeroom and calls it in: APS sends the whole squad to look at that place, and you walk past behind them.")

![The demo guard calling in a noise](media/cards/squad_callin.webp "How the demo does it (BP_DemoGuard): a noise it heard is called in with Broadcast Alert to Squad (a place, no target), then the guard goes to look.")

::: deep What a squadmate receives
**Share Target with Squad** writes into the receiver's belief:

- **Position, predicted position and velocity** are always replaced: shared intel is taken as fresher.
- **Cover** is copied if the sender saw the target take cover.
- **Confidence** is raised to the higher of the sender's confidence and the receiver's `Suspect Threshold`, **only if that is higher than what it already believes**: it never lowers direct sensing.
- **Threat** takes the higher of the two; the relationship is copied.

**On AI Squad Alert** fires on the receiver only when the news is new: the target was Undetected or Expired, or the shared threat is higher than what it had. Sharing the same target again doesn't fire it again, so auto-share is safe to leave on. Things (APS Evidence) are never shared.
:::

### It knows it was only told

Shared intel arrives with **Stimulus** = Shared Intel on **On AI Suspect** and **On AI Detect**, so the receiver knows it didn't perceive this itself:

```
On AI Detect (Target, Threat Level, Stimulus)
  └─► Branch: Stimulus is Shared Intel
        True  → move up carefully, don't shoot yet
        False → I saw this myself: engage
```

That one branch is the difference between a squad that converges sensibly and one that headshots you through a wall the instant anyone sees you.

![The demo guard reacting to shared intel](media/cards/squad_told.webp "BP_DemoGuard: a guard that was only TOLD about you (Stimulus: Shared Intel) goes to check where you were seen, instead of acting as if it saw you. A friend gets a nod.")

### Combat roles

![Room Q3: each guard takes a role](media/squads/roles.mp4 "Room Q3. When the squad sees you, each guard asks APS for a combat role: one flanks, one covers you, the rest move in.")

Each role is held by **one squad member at a time**: **Approacher**, **Flanker**, **Suppressor**, **Investigator**, **Support** (or None).

| Node | What it does |
|---|---|
| **Request Combat Role** (Role) | Claim it. False if a squadmate holds it, the AI is in no squad, or the role isn't in the profile's `Eligible Roles`. Claiming gives up the role it held before. |
| **Release Combat Role** | Give it back: when it dies, retreats or loses the target |
| **Get Combat Role** | What it holds |
| **On Combat Role Assigned** (Role) | Fires when a role is granted |

`Eligible Roles` on the profile limits what a kind of AI may claim: a heavy gunner can be Suppressor or Approacher, never Flanker. Empty means any role.

```
On AI Detect
  └─► Request Combat Role (Flanker)
        True  → Blackboard "Role" = Flanker       (the tree runs the flank)
        False → Request Combat Role (Suppressor)
                  True  → "Role" = Suppressor
                  False → "Role" = Approacher

On AI Forget
  └─► Release Combat Role
```

Four guards spotting you now produce one flanker, one suppressor and two approachers, with no squad manager and no central coordinator.

![The demo guard taking a role](media/cards/squad_roles.webp "BP_DemoGuard › Take Role: claim Flanker (one per squad, first come first served), else Suppressor, else move in.")

## Teams and relationships

![Room Q4: a disguise](media/squads/disguise.mp4 "Room Q4. In a guard's uniform you walk past the gate. APS still sees you, but the guard takes you for one of its own (Relationship) and can't get sure it's you (an evidence ceiling).")

Add **APS Relationship** to the AI, next to its APS Core. It's optional: without it, everyone is Unknown.

| Setting | What it does |
|---|---|
| `Team Relationships` | A team id (Unreal's Generic Team Id, from the target or its controller) → relationship |
| `Class Relationships` | An actor class → relationship. **Wins over teams.** |
| `Default Relationship` | When no rule matches |

The relationship is resolved in this order: **Set Relationship Override** (one actor, at runtime) → class → team → default. **Get Relationship** (Target) reads it.

| Relationship | Meaning | Its threat weight |
|---|---|---|
| **Enemy** | Hostile | 1 |
| **High Value** | A priority target: a VIP, an objective carrier | 1.2 |
| **Feared** | Something it should run from | 1.5 (the most) |
| **Neutral** | Civilians, wildlife: perceived, not threatening | 0.3 |
| **Friendly** | An allied faction, not this squad | 0: never a threat |
| **Teammate** | Its own side | 0: never a threat |
| **Unknown** | No rule matched | 0.5 |

Relationships feed the threat score (`Threat Weight Relationship`), and Friendly and Teammate targets are never a threat however sure the AI is. They are also the cleanest branch in your behaviour:

```
On AI Detect (Target)
  └─► Switch on Get Relationship (Target)
        ├─ Enemy      → engage
        ├─ Feared     → flee (Set Fear Input 1 makes it afraid)
        ├─ High Value → call it in, go for it first
        ├─ Neutral    → ignore, keep patrolling
        └─ Teammate   → ignore
```

**Set Relationship Override** handles what a static rule can't: the player in a guard's uniform → Friendly; the disguise blown → Enemy; an NPC recruited mid-mission → Teammate; a boss enraged → the player Feared by nearby minions.

![The demo guard checking relationships](media/cards/squad_friend.webp "BP_DemoGuard › Should React To: Teammate, Friendly and Neutral are left alone (Get Relationship).")

## Debugging a squad

The **APS › Debug › Squad** nodes return a report as text (one line per finding) and write it to the Output Log; show it with a Print String. To watch a squad live, the [Visualizer](visualizer.md)'s **Squad** page shows the squad of the AI in focus.

| Node | What it does |
|---|---|
| **Squad State Report** (Agent) | Squad id, every member, their distance, whether they're in share range, their role |
| **Trace Squad Share Path** (Sender, Target) | A dry run, step by step: squad id set, belief held, threat high enough, members registered, each in range. Nothing is shared. **Start here when sharing doesn't work.** |
| **Squad Beliefs Report** (Agent, Target) | What every member believes about one target: run it after a share |
| **Simulate Squad Share** (Sender, Target, Receiver) | Hand the sender's belief to one receiver, as a share would |
| **Simulate Squad Alert** (Receiver, Target, Location, Threat) | Fire **On AI Squad Alert** on one AI alone, to test its response |
| **Force Full Squad Share** (Sender, Target) | Share with every member, ignoring range and minimum threat |

## APS and Unreal's AI Perception

| | Unreal AI Perception | APS |
|---|---|---|
| Sharing | Each AI's eyes are its own | Squads share within radio range; noises can be called in |
| Knowing it was told | n/a | Stimulus: Shared Intel |
| Roles | None | Exclusive combat roles per squad |
| Teams | Generic Team Id: friendly, neutral, hostile | Classes, teams, per-actor overrides, seven relationships that feed threat |

::: try Q1 to Q4
In the demo, take the **Squad** door from the hub: radio range (Q1), a noise called in (Q2), combat roles (Q3) and a disguise (Q4). Q5 and Q6 are on [Search & evidence](search.md) and [Knowledge & witnesses](knowledge.md).
:::
