---
title: Get Started
description: Install APS and build your first AI in five minutes. Blueprint only, no C++, no Behavior Tree.
---
# Get started

Your first AI in five minutes. Blueprint only: no C++, no Behavior Tree.

<div class="meta"><span><b>5 minutes</b> once APS is installed</span><span><b>Blueprint</b> only</span><span>Unreal Engine <b>5.2+</b></span></div>

::: fast
![A guard's sight lines on the player, with the APS Visualizer panel and the result card](media/start/result.mp4 "What you'll have at the end: an AI that grows sure of you, with the APS Visualizer showing what it sees.")
- Add **APS Core** to your AI and give it a **Perception Profile**.
- React with one event: **On AI Detect**.
- Press Play. Tick **Show Visualizer** to see what your AI sees.
:::

## Five steps

::: steps
### Install APS
In the Epic Games Launcher, open **Library → Fab Library**, find **APS - Advanced Perception System** and click **Install to Engine**. Then, in your project: **Edit → Plugins**, search `Advanced Perception`, tick its box and restart the editor.

![The Plugins window: APS - Advanced Perception System, version 3.0, enabled](media/start/plugins.webp "Edit → Plugins, search Advanced Perception, tick the box.")

::: deep Install it into one project instead
1. Close the editor.
2. Copy the `APS` folder into `YourProject/Plugins/APS/`. The `APS.uplugin` file must sit directly in that folder.
3. Open `APS.uplugin` in a text editor and make sure it has the line `"EnabledByDefault": false,` (put it under `"CanContainContent"` if it's missing).
4. Reopen the project. On a Blueprint-only project, accept when the editor offers to build the module.
5. **Edit → Plugins → APS → Enabled**, and restart.

Why step 3 matters: without it, the packager can't tell that a Blueprint-only project needs APS built into its game. Packaging then stops with *"does not look like uproject file but no targets have been found!"*, or ships Unreal's prebuilt game, without APS, which logs *"Plugin 'APS' failed to load"*. Installs from Fab already behave the right way.
:::

### Create a Perception Profile
In the Content Browser: right-click → **Miscellaneous → Data Asset** → type `Perception` and pick **PerceptionProfile** → **Select** → name it `DA_Profile_Guard`.

![The new Perception Profile, with Vision and Hearing already in its senses](media/start/profile.webp "A new profile already sees and hears. You don't have to change anything yet.")

The profile is everything this AI perceives and how sharply. One profile per kind of AI: a guard, a dog, a camera.

::: deep Why it works before you change anything
A new profile already has **Vision Sense** and **Hearing Sense** in its `Sense Classes`, and every other setting has a working default. An empty list would make the AI perceive nothing at all, which is the most common first-run mistake, so the two senses almost every game wants are already in.
:::

### Add APS Core to your AI
Open your AI character Blueprint (a `Character` or `Pawn`, for example `BP_Guard`). No AI yet? In the Content Browser: right-click → **Blueprint Class** → **Character** → name it `BP_Guard`. In the Components panel, click **Add** and type `aps`: every APS component is listed. Pick **APS Core**.

![The Add menu with aps typed in: APS Core, Environment, Evidence, Observer, Perception Listener, Relationship, Search, Signature, Target Component](media/start/add.webp "Add, then type aps: every APS component starts with APS.")

It appears in the Components list as **PerceptionCore**. Select it and, in its Details, set **APS › Config › Profile** to `DA_Profile_Guard`. Tick **APS › View › Show Visualizer** to see what it sees while you play. Drawing it costs about 0.3 ms a frame per AI: fine for a few, but leave it off on a crowd ([Performance](guides/performance.md#expensive-on-purpose)).

![APS Core's Details: Profile set to DA_Profile_Guard and Show Visualizer ticked](media/start/core.webp "APS Core's Details: the Profile says what it perceives; Show Visualizer draws it in the game.")

::: warning It goes on the character, not the AIController
APS perceives from the body it is on: its eyes, its mesh, the hits it takes. An AIController has none of those, so APS Core on a controller logs an error and stays off. Keep your Behavior Tree on the AIController as usual; only APS Core goes on the character.
:::

### React when it spots you
Select **PerceptionCore** (the APS Core), and at the bottom of its Details, under **Events**, click **+** next to **On AI Detect**. The event appears in the graph, already connected. Add a **Print String** to it, or an **AI MoveTo** to send the guard after you. Do the same for **On AI Lost**.

![APS Core's events in the Details panel, each with a + button](media/start/events.webp "Every APS event is here. Once an event is in your graph, its + turns into a button that jumps to it.")

![A whole guard in five nodes: On AI Detect into AI MoveTo, On AI Lost into AI MoveTo](media/home/five_nodes.webp "A complete guard: when it detects you it comes for you; when it loses you it goes where it last saw you.")

### Press Play
Drop the guard in your level and walk into its view.

![A guard growing sure of the player, shown by the APS Visualizer](media/start/play.mp4 "The guard's sight lines on you, its panel (top right) and the room's live screen: confidence climbs while it can see you.")

You will see:

- its **view cone** and lines to the **points of you it can see**,
- a **panel** in the top right corner: its state, a confidence graph and one row per sense,
- its **state** floating above you,
- your **Print String** once it is sure enough to detect you.

Step behind a wall and watch it go **Detected → Lost**, then fade to **Remembered** and **Expired**.
:::

## Play the demo

The demo comes inside APS: a hub with one wing per feature, holding the rooms the feature pages point to.

1. In the Content Browser, click **Settings** and tick **Show Plugin Content**. Installed from Fab? Tick **Show Engine Content** too: APS is then an engine plugin.
2. Open **Plugins › APS - Advanced Perception System › Demo › Maps**. From Fab it is under **Engine › Plugins**; older engines add **Content** to the folder's name.
3. Double-click **L_MainMenu** and press **Play**.

The demo is lit with Lumen, the default for a new Unreal 5 project. If its rooms look washed out, or the screen shows a red line about distance fields, open **Project Settings → Rendering** and set **Dynamic Global Illumination Method** and **Reflection Method** to **Lumen** and tick **Generate Mesh Distance Fields** (the editor asks to restart).

::: deep Package the demo
Your own game doesn't carry the demo: Unreal packages a plugin's levels only when your levels use them. To package the demo by itself, set **Project Settings → Maps & Modes → Game Default Map** to `L_MainMenu` and add all 11 levels in **Demo › Maps** to **Project Settings → Packaging → List of maps to include in a packaged build**. Without that list only the menu is packaged, and its doors lead nowhere.
:::

## Next steps

::: grid
::: card Every feature, one page each | features/confidence.md
Start with Confidence: light, cover, stance and the vision cones.
:::
::: card Let it hear you | features/hearing.md
APS hears only what your game says is audible: add **Emit Sound** to your footsteps.
:::
::: card Make the player perceivable | features/senses.md#vision
Add **APS Target Component** to your player: five points on your skeleton, stance and camouflage.
:::
::: card Share reactions between AI | reference/events.md
Put your reactions in an **APS Perception Listener** and add it to every AI that should share them.
:::
:::

::: deep Setup checklist
**On the AI**

- `APS Core` added, with its `Profile` set (not None)
- Your `APS Perception Listener` Blueprint added, if AI share their reactions
- `APS Relationship` added, if you use teams

**On the player and other targets**

- `APS Target Component` added (recommended)
- Actors that aren't Pawns call `Register Perceivable Actor` on Begin Play

**In the world**

- Sound types made, and `Emit Sound` called from footsteps and weapons
- `Set Sun Direction` called once, if you use light and shadow per target
- `Set Ambient Light` driven by your day and night cycle, if you have one
:::

::: tip Can't find something?
Every component starts with **APS**: type `aps` in **Add** to see them all. Most Blueprint nodes are under **APS** too: right-click in a graph and type `APS`, or drag from an APS Core and search.
:::
