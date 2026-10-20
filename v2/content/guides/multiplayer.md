---
title: Multiplayer
description: Perception runs on the server only. Turn on a small replicated summary so clients can show detection meters, read it with one node and one event, and keep the bandwidth down.
---
<div class="kicker">Guide</div>

# Multiplayer

Perception runs **on the server only**. Clients get an optional, compact summary for their UI: a detection meter, a "being watched" indicator, a spectator view.

::: fast
- The **APS Core** goes on the **Pawn**, and the Pawn must have **Replicates** on.
- Profile › **Replication** › `Replicate Perception State` on.
- On clients: **On Replicated State Changed** → **Get Replicated Perception State** → update the widget.
:::

## How it works

On a client, APS does nothing at all: no traces, no evaluation, no cost. Clients can't be tricked into reporting a detection, and there is nothing to desync. Everything that changes perception (**Emit Sound**, **Report Pain from Definition**, **Set Target Confidence**, **Add Target Evidence**, squads) must run **on the server**: a sound emitted only on a client is heard by nobody.

Perception events (**On AI Detect** and the rest) fire on the server. Replicate their **consequences** (an animation, a state on your character), not the perception.

## The APS Core goes on the Pawn

The **APS Core** must be on the **Pawn or Character** it perceives for, never on the AI Controller:

- **It perceives from the body**: eye position and facing, mesh sockets, the collision touch listens to, the damage it feels. A controller stays where it spawned and never takes damage.
- **It replicates with the Pawn.** A component reaches clients only through an actor that replicates. Pawns do; AI Controllers never do.

On a controller it logs an error naming the controller (also in the Message Log after Play) and stays off. Your Behavior Tree and Blackboard stay on the controller: reach the core with **Get Controlled Pawn** → **Get Component by Class** (APS Core).

## Turn on the summary

Profile › **Replication**:

| Setting | Default | What it does |
|---|---|---|
| `Replicate Perception State` | Off | Send a compact summary of this AI's targets to clients |
| `Max Replicated Targets` | 3 | How many targets go in (1 to 8), the best first. Every AI with replication pays for this. |
| `Replication Interval` | 0.25 | Seconds between updates |
| `Use Replication Relevance` | On | Leave out targets nobody is near or that it barely suspects (the next two) |
| `Replication Relevance Range` | 15000 | A target whose **believed** position is further than this (cm) from every player's camera is left out; 0 turns the distance test off |
| `Replication Min Confidence` | 0.1 | Below this confidence a target is left out |
| `Skip Unchanged Replication` | On | Send nothing when nothing changed |
| `Replication Confidence Delta` | 0.02 | How much confidence must move to count as a change |

Only targets that are **Suspected, Detected, Tracked or Lost** go in. Turn **Replicates** on in the Pawn's Class Defaults too: if it's off, the summary can't reach anyone, and APS logs a warning once.

## Read it on clients

```
On Replicated State Changed
  └─► Get Replicated Perception State
        ├─ Out Targets   (array of APSReplicated Target State)
        └─ Out Awareness (the AI's awareness)
              └─► update the detection meter
```

Each **APSReplicated Target State** has `Target`, `Confidence`, `State`, `Threat Level` and `Last Known Position`; Out Awareness is also on the APS Core as the variable `Replicated Awareness`. Bind the event instead of polling on Tick.

::: warn The event fires on clients only
**On Replicated State Changed** is raised when new data **arrives**, which happens only on clients. On a **listen server's host** (and in single player) it never fires: there, read **Get Replicated Perception State** on a short timer, or use the server's own events.
:::

## Bandwidth

The most it can cost is **AI × `Max Replicated Targets` ÷ `Replication Interval`** target states a second: 50 AI × 3 ÷ 0.25 s is 600. Relevance and skipping unchanged updates usually send far less.

Most games only need this on the few AI near the player. Keep replication off in the base profile and on in a close-range child profile, and switch with **Set Profile** when an AI comes near ([Profiles](profiles.md)). Or set `Max Replicated Targets` to 1 and `Replication Interval` to 0.5.

## Debugging in multiplayer

The Visualizer, **Explain Perception** and the recording read what the AI believes, which exists only where perception runs: the server. Debug with a listen server (or play as the host), not from a pure client.

## Checklist

- APS Core on the **Pawn**, the Pawn set to **Replicates**
- `Replicate Perception State` on, if clients show perception in their UI
- `Max Replicated Targets` as small as your UI needs
- Client UI reads **Get Replicated Perception State**, driven by **On Replicated State Changed** (a timer on a listen-server host)
- **Emit Sound**, pain, evidence and confidence calls run on the server (**Has Authority**)

## When something's wrong

| Symptom | Cause |
|---|---|
| The client's target array is empty | `Replicate Perception State` is off, the Pawn doesn't replicate (look for the APS warning), or no target passes relevance |
| The AI perceives nothing and the log says the APS Core is on a controller | Move it to the Pawn or Character Blueprint |
| The meter never updates on the host | On a listen-server host the event doesn't fire: read the state on a timer |
| A sound is never heard | **Emit Sound** ran only on a client: call it from server code or through a server RPC |
| Perception events never fire on clients | By design: perception runs on the server |
| Bandwidth spikes with many AI | Lower `Max Replicated Targets`, raise `Replication Interval`, and replicate only the AI near players |
