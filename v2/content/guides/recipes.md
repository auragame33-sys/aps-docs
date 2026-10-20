---
title: Recipes
description: Short, tested answers to the things people most often want - footsteps, sprinting, see-through cover, crouching, dark corners, a reaction window, a warning bark, safe rooms, searching, a detection meter, reacting to how it knows, squads, a disguise, live tuning.
local: DA_Sound_Footstep, DA_Sound_Sprint, DA_Sound_Crouch, Footstep, HasTarget, InvestigateLocation, LastKnownPosition, LastCoverActor, LossReason, LossDirection, SearchRadius, DA_Profile_Guard_Alerted, SurfaceType_Glass, SurfaceType_Foliage, SurfaceType_Smoke
---
<div class="kicker">Guide</div>

# Recipes

Each recipe is a few steps and a reason. They link to the page that explains the feature in full.

## Detection

### Hear footsteps

1. Make a **Sound Type Definition** data asset, DA_Sound_Footstep: `Base Loudness` 1, `Max Range` 800.
2. Add an anim notify named Footstep to your walk and run animations.
3. In the player Blueprint: **AnimNotify_Footstep** → **Emit Sound** (Source: Self, Sound Type: DA_Sound_Footstep).
4. The AI's profile needs **Hearing Sense** in `Sense Classes` (it's there by default).

**Why:** APS never makes sounds from movement. The AI hears exactly what your game emits, nothing else. [Hearing](../features/hearing.md)

### Make sprinting louder than walking

A second asset, DA_Sound_Sprint (`Base Loudness` 1.8, `Max Range` 1600, `Alert Level` Loud), and branch in the same notify:

```
AnimNotify_Footstep
  └─► Get Velocity → Vector Length → Branch: > 450
        True  → Emit Sound (DA_Sound_Sprint)
        False → Emit Sound (DA_Sound_Footstep)
```

Add a quiet DA_Sound_Crouch (`Base Loudness` 0.3, `Max Range` 300, `Alert Level` Whisper) for crouched steps and you have three tiers of movement stealth.

### Stop it seeing through doors, vehicles and other pawns

1. Profile › **Detection › Occlusion** › `Vision Occlusion Channels`: list every channel that should block sight. **The list replaces Visibility**, so add Visibility too if your walls block that. Empty means Visibility only.
2. Bodies blocking sight: tick `Pawns Block Sight`.
3. Check the geometry really blocks that channel in its collision settings.

**Why:** Unreal's perception tests one channel, so props on a custom channel are see-through to it. Each extra channel is one more trace per point: add only what you need. [Senses](../features/senses.md#what-blocks-sight)

### Let foliage and smoke hide you partly

Profile › **Detection › Occlusion** › `Surface Vision Transmission`: SurfaceType_Glass 1, SurfaceType_Foliage 0.4, SurfaceType_Smoke 0.15 (your own physical surfaces).

**Why:** the value is the share of sight that **gets through**; anything not listed blocks completely. A player in tall grass is partly seen, not all or nothing. [Confidence](../features/confidence.md#glass-leaves-and-smoke)

### Make crouching hide the player

1. On the player, an **APS Target Component** with `Auto Detect Stance` ticked (the default).
2. Profile › **Detection › Visibility**: `Min Visible Points Crouched` 2, `Min Visible Points Prone` 3.

**Why:** all three are 1 by default, so adding the component never makes anyone harder to see. At 2, a crouched player behind cover must show two points before it counts at all. [Confidence](../features/confidence.md#stance)

### Make its sight follow its head

Profile › **Detection › Eyes**: `Use Eye Socket` on, `Eye Socket Name` head, `Eye Direction Mode` Socket Rotation (head bone), `Eye Socket Alignment` Automatic (the default), `Eye Turn Rate Deg Per Sec` 200.

**Why:** Automatic reads the skeleton's rest pose, so a plain bone name works on any rig. The turn rate stops the cone snapping to a Move To target before the body has turned. [Senses](../features/senses.md#eyes-in-the-head)

### Make a dark corner dark

1. At Begin Play: **Get APS Subsystem** → **Set Sun Direction** (your directional light's forward vector).
2. Profile › **Detection › Light**: tick `Use Per Target Light` (`Trace Sun Shadow` is on already; `Shadow Light Level` 0.25).
3. Optional, exact: set `Light Level Override` on the player's APS Target Component from your own light gem. It wins whatever the profile says.

[World & fairness](../features/world.md#light)

## Fairness

### Give the player a beat to duck back

Profile › **Fairness** › `First Spot Reaction Time` 0.4. Until the AI first suspects a target, it must see it this long before confidence counts. [World & fairness](../features/world.md#a-beat-to-step-back)

### Warn before it commits

Profile › **Fairness** › `Telegraph Threshold` 0.22 (between Suspect and Detect), then:

```
On AI Telegraph (Target, Confidence)
  ├─► play "Hm?"
  ├─► Set Focus (Target)          // the head turns
  └─► flash a pip on the HUD
```

It fires once per target, and again only after the AI has let that target go. [World & fairness](../features/world.md#a-warning-before-it-commits)

### Give the player a safe room

1. Safe room, Begin Play: **Get APS Subsystem** → **Register Never Search Zone** (Center: Get Actor Location, Radius: 600).
2. **Then honour it, this part is required:** before sending the AI anywhere (On AI Lost, each search point), ask **Is Location in Never Search Zone** on its APS Core; true means don't go.

APS doesn't enforce zones by itself. [Search & evidence](../features/search.md#places-it-never-searches)

## Searching

### Investigate a noise without dropping a chase

```
On AI Hear (Location, Loudness, Sound Type Name)
  └─► Branch: Blackboard HasTarget is false AND Sound Type Name is not None
        True → Blackboard InvestigateLocation = Location
```

Without HasTarget, every distant footstep interrupts a pursuit. Without the None check, the updates between sounds (the build-up) move the spot to where the player is now. [Hearing](../features/hearing.md#7-reading-what-it-heard)

### Search the corner it lost you behind

```
On AI Lost (Target, Last Known, Predicted, Last Cover Actor)
  └─► Blackboard
        ├─ LastKnownPosition = Last Known
        ├─ LastCoverActor    = Last Cover Actor
        ├─ LossReason        = Get Loss Reason (Target)
        ├─ LossDirection     = Get Loss Direction (Target)
        └─ SearchRadius      = Get Uncertainty Radius (Target)
```

Then branch the tree on LossReason ([Behavior Trees](behavior-trees.md)). `Last Cover Actor` is the object it traced against when it lost you: flanking **that** is the biggest perceived-intelligence win there is. [Memory](../features/memory.md#what-it-knows-the-moment-it-loses-you)

### Search wider the longer you hide

Use **APS Search**: **Begin Search** at the last known position, then **Get Best Search Point** until **Is Search Exhausted**. It searches where you could have got to, avoids walls, and clears as it walks. [Search & evidence](../features/search.md#search)

Without it: move to **Get Random Reachable Point in Radius** around LastKnownPosition with Radius = **Get Uncertainty Radius**. The radius grows at `Uncertainty Growth Rate` while you're lost, up to `Max Uncertainty Radius`, and, with `Velocity Scaled Uncertainty` (on by default), up to 3 times faster for a target that was moving fast (1800 cm/s or more).

### Make it search longer before giving up

Profile › **Memory** › `Min Time in Lost` 8 (25 for a horror stalker). A target can't leave Lost for Remembered until it has been Lost this long, however far confidence has fallen. It is the "how stubborn" dial.

## Reactions and UI

### A detection meter

**Get Belief Data** (Player) → **Break** → `Smoothed Confidence`, 0 to 1, in a widget's tick or a 0.1 s timer.

::: warn Not the APS Core's own Smoothed Confidence variable
The APS Core has variables named Smoothed Confidence and Current State. **APS 3.0 never updates them** (0 and Unaware always). Read the belief about your target instead.
:::

In multiplayer perception runs on the server: see [Multiplayer](multiplayer.md).

### React to seeing differently from hearing

```
On AI Detect (Target, Threat Level, Stimulus)
  └─► Switch on Stimulus
        ├─ Vision       → engage
        ├─ Hearing      → go and look, weapon lowered
        ├─ Smell        → follow the trail
        ├─ Damage       → take cover first, then look
        ├─ Shared Intel → approach carefully, don't fire yet
        └─ Unknown      → touch, vibration, echolocation or a custom sense
```

**Get Sense Contributions** (Target) gives each sense's share when you need finer detail.

### React to being shot from nowhere

```
On AI Damaged (Instigator, Amount, Damage Type Tag, Hit Location)
  ├─► play a flinch montage
  ├─► Blackboard InvestigateLocation = Get Last Known Position (Instigator)
  └─► Report Pain from Definition (DA_Pain_Bleeding, Amount / 200)
```

With Damage Sense the shooter is already believed in, placed where they stood. For hardcore stealth turn `Auto Confidence from Damage` off, so a silenced hit hurts without revealing the shooter. [Emotions & pain](../features/emotions.md#damage-knowing-who-hurt-it)

## Squads

### One sees you, the others come

Each AI at Begin Play: **Set Squad ID** (Patrol_A). `Auto Share on Detect` is on by default, within `Squad Share Range` (3000). [Squads & teams](../features/squads.md)

### Converge without telepathy

1. Profile: `Auto Share on Detect` and `Auto Share on Track` both off.
2. Share after a visible call-out: **On AI Detect** → play a "Contact!" montage → on its notify, **Share Target with Squad** (Target).
3. On the receiver, branch on Stimulus = Shared Intel and approach carefully.

Without step 3, one guard spots you and four others shoot you through a wall.

### Split up combat roles

**Request Combat Role** (Flanker), else (Suppressor), else Approacher; **Release Combat Role** on **On AI Forget**. Four guards give one flanker, one suppressor and two approachers, no manager. [Squads & teams](../features/squads.md#combat-roles)

## Bigger changes

### Blind it with a flashbang

A Pain Type DA_Pain_Flashbang (`Decay Rate` 0.5, `Amount Override` 1; `Sense Effects` Vision Sense 1, Hearing Sense 0.5), and when the grenade goes off, **Report Pain from Definition** on each guard with a clear line to it. [Emotions & pain](../features/emotions.md#pain-senses-that-stop-working)

### Switch to an alert profile

```
Alarm raised
  └─► for each guard: Set Profile (DA_Profile_Guard_Alerted)
```

Make the alert profile a **child** of the base one so the swap keeps everything the AI believes. [Profiles](profiles.md)

### A disguise

**Add Target Evidence** (Player, "Disguise", Clamp (ceiling), 0.15) on each guard holds their belief at or below 0.15 even while they see you; **Remove Target Evidence** when the disguise is blown. [Confidence](../features/confidence.md#change-it-from-script) The demo's Q4 does it with relationships instead: [Squads & teams](../features/squads.md#teams-and-relationships).

### Tune one enemy without a new asset

```
Begin Play
  ├─► APS Core → Set Profile Number (VisionMaxRange, 3200)
  └─► APS Core → Set Profile Flag (bEnablePeripheralCone, true)
```

Or fill in `Profile Overrides` on the APS Core. The change lands on a private copy: the asset and every other AI are untouched, and nothing it believes is reset. Use the **override name** shown on the [profile reference](../reference/profile.md). For every AI at once while playing: `aps.Tune VisionMaxRange 3200` in the console.

### Perceive something that isn't a Pawn

Add an **APS Target Component** (it registers itself), or call **Register Perceivable Actor** at Begin Play and **Unregister Perceivable Actor** at End Play. [How APS thinks](../how-it-works.md#13-who-it-can-perceive)

### Add your own sense

A Blueprint child of **Sense Unit** that answers **Get Sense ID** and **Evaluate**, added to `Sense Classes`. It fuses with the others and shows in the Visualizer. [Custom senses](custom-senses.md)
