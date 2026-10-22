---
title: FAQ
description: Short answers - running beside AI Perception, C++, Blueprint-only projects, Behavior Trees, changing perception at runtime, how many AI, multiplayer, saving, turning a sense off, GAS and other systems, the source.
---
<div class="kicker">Help</div>

# FAQ

**Can I use APS beside Unreal's AI Perception?**
Yes. APS doesn't touch or disable it; run both while you move across. [Coming from AI Perception](../guides/from-ai-perception.md)

**Do I need C++?**
No. Everything in these docs is Blueprint, including your own senses and policies. C++ is needed only for a custom sense that reacts to the stimulus bus, fires a sense event, is event-driven or about the AI itself, or reports beliefs about places. [Custom senses](../guides/custom-senses.md)

**Does it work in a Blueprint-only project?**
Yes. Installed from Fab it is ready to enable; installed by hand, accept when the editor offers to build the module. [Getting started](../getting-started.md)

**Does it need a Behavior Tree?**
No. APS reports what the AI believes; use it from a Behavior Tree, a state machine or plain event graphs. [Behavior Trees](../guides/behavior-trees.md)

**Can I change how an AI perceives while playing?**
Yes. **Set Profile** swaps the whole setup and keeps what it knows when the senses match; **Set Profile Number** changes one value for one AI; a **Quality Profile** changes only the cost. [Profiles](../guides/profiles.md)

**Can I turn one sense off while playing?**
Not on its own. Swap to a profile without it (**Set Profile**), or report a pain type that dulls only that sense to nothing: often what you actually want. [Emotions & pain](../features/emotions.md#pain-senses-that-stop-working)

**Can one AI have several vision cones?**
Three: focal, side and rear-motion, plus keyhole vision. [Senses](../features/senses.md#cones-and-keyhole-vision)

**How many AI can it handle?**
Comfortably about 30 on defaults; several hundred with tuning, a far Quality Profile and the crowd tier. Measure your own level. [Performance & crowds](../guides/performance.md)

**Does perception run on clients?**
No, on the server only. An optional replicated summary feeds client UI. [Multiplayer](../guides/multiplayer.md)

**Is anything saved to disk?**
No. APS writes no files: the player model and the memory store last for the session, and a newly spawned AI knows nothing. To keep them, read what you need and write it into your own save game. [Memory](../features/memory.md)

**Does it work with GAS, Lyra, ALS or my health system?**
There is no tie to any of them. APS reads positions and traces geometry; where it needs your game's health or posture it asks through two optional interfaces. [Policies & adapters](../guides/policies.md#adapters)

**Can it perceive things that aren't Pawns?**
Yes: **Register Perceivable Actor**, or an **APS Target Component**. Pawns are found by themselves. [How APS thinks](../how-it-works.md#13-who-it-can-perceive)

**What does Get Active Target Count count?**
The actors it is Suspected, Detected, Tracked or Lost about: not places, not things, not Remembered ones. When it falls to 0, **On AI All Clear** fires.

**Why does my guard notice its own squadmates?**
Every Pawn in range is a candidate. Allies take target slots only after everyone else, are never a threat, and your logic can ignore them by relationship ([Squads & teams](../features/squads.md#teams-and-relationships)). Once noticed, they can be its top or attention target, so check the relationship before acting on attention. They do count toward fear's "more than 2 targets" ([Emotions & pain](../features/emotions.md#the-rules)).

**Is the source included?**
Yes, the full C++ source ships with the plugin.

**Something here doesn't match what I see.**
These docs were checked against the APS 3.0 source: every node, setting and default name, and every behaviour described. If you find a difference, report it on the [issue tracker](https://github.com/auragame33-sys/aps-docs/issues).
