# Install & Your First AI

<div class="aps-meta" markdown>

**For:** first-time users · **Time:** about 15 minutes · **Outcome:** an AI that detects you and fires Blueprint events

</div>

> **▶ Video walkthrough** — *Install and first detection (6 min).* Coming soon.
> When it is live, delete this block and uncomment the embed below.

<!-- VIDEO EMBED — replace VIDEO_ID with your YouTube id, then delete the comment markers
<div class="video">
  <iframe src="https://www.youtube.com/embed/VIDEO_ID" title="Install and first detection" allowfullscreen></iframe>
</div>
-->

## Installation

### From Fab / Epic Games Launcher

1. In the Epic Games Launcher, open **Library → Fab Library**, find **APS — Advanced Perception System**, and click **Install to Engine**. Pick your 5.2 engine.
2. Open your project.
3. **Edit → Plugins**, search `APS`, tick **Enabled**.
4. Restart the editor when prompted.

### Manual install (into one project)

1. Close the editor.
2. Copy the `APS` folder into `YourProject/Plugins/APS/`. The `APS.uplugin` file must sit directly inside that folder.
3. Reopen the project. If you are on a Blueprint-only project the editor will offer to build the module — accept.
4. **Edit → Plugins → APS → Enabled**, restart.

### Verify it is working

Right-click in the Content Browser. You should see **Miscellaneous → Data Asset** offering `PerceptionProfile`, `SoundTypeDefinition`, `SoundFilterProfile` and `PainTypeDefinition` in the class picker.

Open any Blueprint, right-click in the graph and type `APS`. You should get a long list of nodes.

---

## Your first AI in 10 minutes

This gets you a guard that spots the player, builds confidence over time, and prints when it detects them. No C++, no Behavior Tree yet.

### Step 1 — Create a Perception Profile

Content Browser → right-click → **Miscellaneous → Data Asset** → choose **PerceptionProfile** → name it `DA_Profile_Guard`.

Open it. It already has **Vision** and **Hearing** in the `Sense Classes` array, and every other setting has a working default. **You do not have to change anything yet.**

!!! info "Why it works before you touch anything"
    A brand-new profile is deliberately functional. An empty sense list would make the AI silently perceive nothing, which is the single most common first-run failure, so the two senses almost every game wants are already there.

### Step 2 — Add the component to your AI

Open your AI character Blueprint (a `Character` or `Pawn` — for example `BP_Guard`).

**Add Component → APS Core.**

Select it, and in the Details panel set:

- **Profile** → `DA_Profile_Guard`
- **Debug Settings → b Enabled** → ✅ (turn this off before shipping; it is compiled out of Shipping builds anyway)

!!! tip "Put it on the Pawn, not the AIController"
    It works on either, but AIControllers never replicate, so putting it on the Pawn keeps multiplayer simple. See [Multiplayer](multiplayer.md).

### Step 3 — Add the Listener component

**Add Component → APS Perception Listener.**

That is the whole setup. This component gives you every perception event as an overridable Blueprint event with **no delegate binding**, exactly like the old `OnSeePawn` from `PawnSensing`.

### Step 4 — Handle an event

In `BP_Guard`'s Event Graph, right-click and search **`OnAIDetect`**. Add the **Event On AI Detect** node.

Drag off it and add a **Print String**. Wire `Target` into the string via **Get Display Name**.

Do the same for **Event On AI Lost** so you can see both sides.

### Step 5 — Make the player perceivable (optional but recommended)

Open your player character and **Add Component → APS Target Component**.

You do not strictly need this — APS automatically considers every `Pawn` in the world as a candidate target. The Target Component adds:

- proper multi-point visibility sampling from *your* skeleton's sockets,
- stance awareness (crouching actually hides you),
- a `Visibility Multiplier` for camouflage or cloaking,
- a `Light Level Override` if you have your own light-gem system.

Leave every setting at default for now.

### Step 6 — Play

Drop `BP_Guard` in the level, possess your player, walk into its vision cone.

You should see:

- a **vision cone** drawn from the guard's eyes,
- a **status panel** in the top-left corner: lifecycle state, a confidence graph, and one row per sense,
- a **state chip** floating above your own character,
- your **Print String** firing when confidence crosses the Detect threshold.

Walk behind a wall. Watch the state go `Detected → Lost`, then decay to `Remembered` and finally `Expired`.

---

## Adding hearing (the step everybody misses)

**Hearing does not work automatically.** APS never guesses that a footstep happened — you tell it. This is deliberate: it means your AI hears exactly what your game decides is audible, and nothing else.

### Step 1 — Create a sound type

Content Browser → **Data Asset → SoundTypeDefinition** → name it `DA_Sound_Footstep`.

| Setting | Value |
|---|---|
| Sound Name | `Footstep` |
| Category | `Enemy` |
| Alert Level | `Normal` |
| Base Loudness | `1.0` |
| Max Range | `800` |
| Max LOD Tier | `1` |

Make a second one, `DA_Sound_Gunshot`: Alert Level `Loud`, Base Loudness `3.0`, Max Range `4000`, Priority `9`, Max LOD Tier `3`.

### Step 2 — Emit it

In your **player character**, open the walk/run animation montage or the locomotion animation, add a **Footstep** anim notify, and in the character's `AnimNotify_Footstep` event:

```
Event AnimNotify_Footstep
  → Emit Sound
      World Context : Self
      Source        : Self
      Sound Type    : DA_Sound_Footstep
```

That is it. Every AI within `Max Range` that passes its own sound filter now hears it, attenuated by distance and muffled by any walls in between.

For a location-based sound with no source actor (explosion, trap, falling crate) use **Emit Sound At Location** instead.

!!! note
    Play your actual audio however you normally would. `Emit Sound` only feeds the perception system.

---

## Setup checklist

Copy this into your project notes.

**On the AI:**
- [ ] `APS Core` component added
- [ ] `Profile` assigned (not None)
- [ ] `APS Perception Listener` added (only if you want no-binding events)
- [ ] `APS Relationship` added (only if you use teams — [Squad & Relationships](squad-and-relationships.md))
- [ ] Squad ID set from Begin Play (only if you use squads)

**On the player / targets:**
- [ ] `APS Target Component` added (recommended)
- [ ] Non-Pawn actors call `Register Perceivable Actor` on Begin Play

**In the world:**
- [ ] Sound types created and `Emit Sound` called from footsteps / weapons
- [ ] `Set Sun Direction` called once from your level Blueprint if you use per-target lighting
- [ ] `Set Ambient Light` driven by your day/night cycle if you have one

---

## Where things live in the editor

**Every component is prefixed `APS`, so typing `aps` into Add Component lists all of them at once.**

| Thing | Where to find it |
|---|---|
| APS Core · APS Perception Listener · APS Target Component · APS Relationship · APS Environment | Add Component → search `aps` |
| APS Observer · APS Signature · APS Evidence · APS Search *(Knowledge module)* | Add Component → search `aps` |
| Perception Profile | Content Browser → Data Asset → `PerceptionProfile` |
| Quality Profile | Content Browser → Data Asset → `APSQualityProfile` |
| Sound Type / Filter | Content Browser → Data Asset → `SoundTypeDefinition` / `SoundFilterProfile` |
| Pain Type | Content Browser → Data Asset → `PainTypeDefinition` |
| Blueprint nodes | Right-click in any graph → type `APS` |
| World settings (light, wind, zones) | `Get APS Subsystem` → drag off it |
| Faction knowledge | `Get APS Knowledge` → drag off it |

---

