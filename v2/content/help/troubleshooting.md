---
title: Troubleshooting
description: Symptoms first, causes second - nothing works, it never sees me, it sees me instantly, it hears nothing, it forgets or never forgets, my event never fires, squads, multiplayer, performance, install and packaging - plus every setting that does nothing in APS 3.0.
---
<div class="kicker">Help</div>

# Troubleshooting

Symptoms first, causes second. For almost everything, the fastest tool is the **Visualizer**: tick `Show Visualizer` on the APS Core and read its **Senses** page ([Visualizer & debugging](../features/visualizer.md)).

## Nothing works at all

Check these first; one of them is almost always it.

1. **The APS Core is on the Pawn.** On an AI Controller it logs *APS Core is on the controller...* and stays off. Move it to the Pawn or Character Blueprint.
2. **A profile is assigned** to the APS Core's `Profile`. Without one, a moment into play APS logs *APS Core on '...' has no Perception Profile*.
3. **The profile has senses.** An empty `Sense Classes` logs *Profile '...' runs no senses*. A new profile starts with Vision Sense and Hearing Sense.
4. **You're playing.** Perception doesn't run in the editor viewport.
5. **You're on the server.** Perception runs on the server only: in Play with several clients, test in the server window.
6. Print **Explain Perception** (Get Player Character) on the AI: it says, per sense, what it reads or why not.

## It never detects me

| Cause | Fix |
|---|---|
| No profile, or no senses | See above |
| Out of range | Raise `Vision Max Range` |
| Outside the cone | Widen `Vision Half Angle Deg`; with `Eye Direction Mode` Socket Rotation (head bone), check the socket (a bad one points the cone at the sky: set `Eye Socket Alignment` Automatic) |
| Thresholds too high | Lower `Suspect Threshold` and `Detect Threshold` |
| Confidence builds too slowly | Raise `Confidence Rise Rate` |
| Fully hidden | The Visualizer's cones stop where sight stops; its points show which parts of you it reaches |
| The target is possessed by the AI's own controller | Skipped on purpose |
| `Min Exposure to Register` or `Min Visible Points Crouched` too high | Lower them (1 is the default for every stance) |
| `First Spot Reaction Time` is running | Reason **Fairness Reaction Hold**: on purpose, the player's beat to step back |
| Pain or low health dulled the senses | See below |
| The target's **APS Target Component** has `Visibility Multiplier` 0 | Reason **Target Opted Out** |

## It detects me instantly, from anywhere

| Cause | Fix |
|---|---|
| A sound type with a huge `Max Range` | Check the sound asset |
| It was hit | Damage reaches any range: turn `Auto Confidence from Damage` off to decide yourself |
| Thresholds too low, or `Confidence Rise Rate` too high | Raise the thresholds, lower the rate |
| Echolocation in the profile | No line of sight needed: lower `Echo Range` or remove it |
| Vibration in the profile | Passes through walls: raise `Vibration Min Speed` or lower `Vibration Detect Range` |
| The crowd tier is on, threshold low | Statistical AI trace nothing, so they see through walls: keep `Statistical Tier Threshold` at 3 |
| A squadmate told it | **Stimulus** is Shared Intel: see [Squads & teams](../features/squads.md#it-knows-it-was-only-told) |

The Visualizer's **Senses** page shows which sense is high. It is usually Hearing or Vibration.

## It sees through walls

1. Add the wall's collision channel to `Vision Occlusion Channels`. Empty means Visibility only; a list **replaces** Visibility, so list it too if your walls block it.
2. Check the wall really blocks that channel.
3. Check `Surface Vision Transmission`: a surface at 1 is fully see-through.
4. Check which sense it is: Vibration and Echolocation are **meant** to pass through walls, and so is the crowd tier.

## It sees me the moment I step into its cone

That is Unreal's perception's behaviour; APS softens it three ways: `First Spot Reaction Time` 0.3 to 0.5, a lower `Confidence Rise Rate`, and `Keyhole Vision` so distance protects you. If it sees you **before it has turned**, set `Eye Turn Rate Deg Per Sec` (0 is instant) to about 180 to 300 for a person.

## My light gem is ignored

`Light Level Override` on the **APS Target Component** wins whenever it is 0 or more, whatever the profile says; -1 lets APS work light out. If it still seems ignored, check `Darkness Min Detection`: at light 0 the AI still sees at that strength (0.1).

## It perceives much worse when hurt

**Pain Sense** reads the AI's health by itself (the APSHealth Provider interface, or a GetHealthPercent, GetHealth or GetCurrentHealth function with GetMaxHealth) and dulls **every** sense with it: at half health, half strength. Implement **APSHealth Provider** and return 1, or take Pain Sense out of the profile. [Emotions & pain](../features/emotions.md#low-health-dulls-every-sense)

## Hearing

**It hears nothing.** Hearing hears only what you emit: something must call **Emit Sound** (or **Emit Sound at Location**). Then check:

- Hearing Sense is in `Sense Classes`;
- the sound type's `Max Range` covers the distance;
- a `Sound Filter` isn't rejecting it: an **empty `Accepted Categories` makes the AI deaf**, and `Min Alert Level` may be above the sound's `Alert Level`;
- the AI's tier isn't above the sound's `Max LODTier` (raise it to 4 for explosions everyone should hear);
- **Emit Sound** ran on the server.

**A thrown can never fires On AI Hear.** Correct: a noise nobody made is a belief about the **place**. Bind **On Location Belief Changed** or read **Get Strongest Location Belief**. [Hearing](../features/hearing.md#5-sounds-nobody-made)

**After a noise it follows me through walls.** While the noise build-up lasts (`Sound Accumulation Hold Time`, 1 s, then it fades at `Sound Accumulation Decay Rate`, 0.2 a second), hearing places you where you **really are**, and **On AI Hear** keeps firing with `Sound Type Name` None. Shorten the hold, raise the decay, and in your Blueprint ignore On AI Hear when the name is None. [Hearing](../features/hearing.md#4-noises-add-up)

**Explosions don't shake my vibration AI.** The sound type's `Sound Name` must be exactly Explosion, and the AI within its `Max Range`. **Emit Sound** and **Emit Sound at Location** both shake the ground.

**It reacts to every footstep at once.** Lower `Sound Accumulation Rate`, raise `Suspect Threshold`, give it a `Sound Filter` with a higher `Min Alert Level`, or lower the sound's `Base Loudness` or `Max Range`. (`Hearing Base Threshold` looks like the setting for this and does nothing: see below.)

**Smell ignores my wind.** **Set Wind State**'s Direction is where the air **goes**; Speed must be above 0; indoors there's no wind; and a Smell Sense child with its own `Wind Direction` uses that instead. [Smell](../features/senses.md#smell)

## Memory and search

| Symptom | Fix |
|---|---|
| It forgets me instantly | Raise the `Vision Loss` Grace Time (0.8 to 1.5), lower `Default Decay Exponent`, raise `Min Time in Lost` |
| It never forgets me | Raise `Default Decay Exponent` or `Memory Expire Threshold`, lower `Min Time in Lost` |
| It searches in a dumb circle | Branch on **Get Loss Reason** ([Behavior Trees](../guides/behavior-trees.md#search-by-why-it-lost-you)) |
| Predicted Position equals Last Known Position | `Enable Prediction` is off (the default) |
| Uncertainty Radius stays 0 | `Enable Spatial Model` is off, or the target hasn't been lost yet: it grows only while lost |
| AI walk into my safe room | Zones are advice: your search must ask **Is Location in Never Search Zone** |
| On AI Lost right after On AI Detect | Confidence hovers at a line: widen the gap between thresholds, raise the vision grace time, or lower `Vision Loss` Confidence Decay Multiplier |
| On AI Detect repeats for one target | It's crossing a line back and forth (each crossing is a real change), or a chase stepped back from Tracked to Detected, which fires On AI Detect again: widen the gaps and raise the grace time |
| The loss reason is SoundFaded, though I hid behind a wall | It could still hear your footsteps fading after you left its sight, so hearing was the last sense to have you |
| It chases a teammate, or someone it only suspects | The target came from **On Attention Changed** or **Get Attention Target**: attention can be on a target it only suspects, or on a teammate. Take the target from **On AI Detect** ([Behavior Trees](../guides/behavior-trees.md#wiring-the-events)) |
| It has me, or lost me, but doesn't move (newer engines) | Not APS: the move failed. In UE 5.8 (unlike 5.2 and 5.3) a move gives up when there is no navmesh within 50 cm of where it is going: you stand on a prop or in a Nav Area Null strip, or the last known position is against tall cover. Move to **Project Point to Navigation** (Query Extent 300, 300, 500) instead; on a Behavior Tree **Move To**, untick **Require Navigable End Location**. For a strip only some AI should avoid, mark it with a Nav Area of your own and exclude that area in the AI controller's **Default Navigation Filter Class**, instead of Nav Area Null |

## Events

**My event never fires.**

1. Visualizer, **Events** page: did it fire?
2. **It fired:** your binding is wrong, or on another component. A Listener must be on the **same actor** as the APS Core.
3. **It didn't fire:** the change never happened. Back to the Senses page.
4. **The target is a body or a forced lock:** a thing, not someone; no event names it ([Search & evidence](../features/search.md#discovering-it)).
5. **On Replicated State Changed** fires on clients only: never on a listen-server host or in single player ([Multiplayer](../guides/multiplayer.md)).
6. **On Emotional State Changed** is on the APS Core only, not on the Listener.

**I can't add the Listener's events to my AI's graph.** A component's events are overridden in a Blueprint **of that component**: make a Blueprint from **APS Perception Listener**, override them there, and add it to the AI. Or use the events on the APS Core (Details › Events, **+**). [Getting started](../getting-started.md)

**I can't find On AI Lost.** It's **On AI Lost** on the APS Core and on the Listener. Before 3.0 the core's was called On AILost Event; Blueprints saved with the old name load with the new one.

## Squads

| Symptom | Cause |
|---|---|
| Sharing does nothing | Run **Trace Squad Share Path** (Sender, Target): it names the step that fails. Usual: no **Set Squad ID**, IDs spelled differently, beyond `Squad Share Range`, below `Min Threat to Share`, both auto-shares off |
| The whole squad knows at once | `Auto Share on Detect` working as designed: turn both auto-shares off, share after a call-out, branch on Shared Intel |
| **Request Combat Role** always false | A squadmate holds it, the role isn't in `Eligible Roles`, or the AI has no squad. A destroyed AI frees its role; one that dies but stays in the world keeps it until you call **Release Combat Role** |

## Multiplayer

| Symptom | Cause |
|---|---|
| The client sees nothing | `Replicate Perception State` is off, the Pawn doesn't replicate (APS warns once), or no target passes relevance |
| **Emit Sound** does nothing | It ran on a client: call it on the server (**Has Authority**, or a server RPC) |
| Perception events never fire on clients | By design: replicate the consequences |

## Performance

**The frame rate drops with many AI.** In order: raise `Base Update Interval`; trim the **Target Component's** `Visibility Samples` (or cap them with a Quality Profile); lower `Max Tracked Targets`; one occlusion channel; `Use Per Target Light` off on background AI; a far Quality Profile. [Performance & crowds](../guides/performance.md)

**Is it APS?** Tick `Pause Perception` on every AI. If the frame rate doesn't improve, the cost is elsewhere.

**My idle AI never run at full rate.** By design: an AI reaches tier 0 only once it is Suspicious or more alert.

## Install and packaging

| Symptom | Fix |
|---|---|
| The plugin doesn't appear | Installed from Fab: **Edit › Plugins**, search Advanced Perception, tick, restart. By hand: the folder must be YourProject/Plugins/APS with APS.uplugin directly inside |
| Packaging stops with *"does not look like uproject file but no targets have been found!"*, or the packaged game says *Plugin 'APS' failed to load* | A by-hand install without `"EnabledByDefault": false` in APS.uplugin: add it and package again ([Getting started](../getting-started.md)) |
| Compile errors after copying the plugin | Delete Binaries and Intermediate in the project and the plugin, regenerate project files, rebuild |
| The Visualizer shows in a packaged game | APS doesn't strip it from any build: turn `Show Visualizer` off (or `aps.Visualizer 0`) before you ship |

## Settings that do nothing

These are visible in APS 3.0 but change nothing; the [reference](../reference/profile.md) marks each one.

| Setting | Use instead |
|---|---|
| Profile: `Hearing Base Threshold` | `Suspect Threshold`, or a `Sound Filter`'s `Min Alert Level` |
| Profile: `Sound Event Only Mode` | Nothing: hearing always hears only emitted sounds |
| Profile: `Touch Confidence` | The strength you pass to **Report Touch Contact**, and the contact type |
| Profile: `Confidence Decay Smoothing`, `Confidence Reduce Delay` | `Confidence Rise Rate`, and each sense's Grace Time and Confidence Decay Multiplier in **Loss** |
| Sound Type: `Is Directional`, `Priority` | `Location Accuracy Override` sets how precisely a sound is placed |
| Touch Sense: `Max Persistent Bonus`; `Max Impulse for Full Strength` and `Persistent Accumulation Rate` (overwritten by the profile unless it is 0) | The profile's `Touch Max Persistent Bonus`, `Touch Max Impulse for Full Strength`, `Touch Persistent Accumulation Rate` |
| APS Core variables Smoothed Confidence (always 0) and Current State (always Unaware) | **Get Belief Data** (Target) › Smoothed Confidence; **Get Awareness Level** |
| Belief Record: Damage Dealt to Target (always 0) | Count the damage your AI deals in your own code |
| Player Behavior Model: Custom Behavior Ratios (always empty) | Your own memory: **Remember** ([Memory](../features/memory.md)) |
| Pain Sense nodes **Set Health Ratio**, **Get Health Ratio**, **Get Pain State** | Not reachable from Blueprint: use the APSHealth Provider interface |
| Sense blocker **Not Evaluated This Tick** | Never reported: a sense keeps its last answer between updates |

Two more behave differently from their names:

- `Vision Sample Count` only limits the built-in point set: a target with an **APS Target Component** uses its own `Visibility Samples`.
- `Respect Never Search Zones` only changes what **Is Location in Never Search Zone** answers: nothing is enforced.
