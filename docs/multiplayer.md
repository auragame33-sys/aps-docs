# Multiplayer

**For:** anyone shipping multiplayer. Perception is server-authoritative; this page covers getting state to clients.

## The model

**Perception is server-authoritative.** The pipeline is skipped entirely on clients — no traces, no evaluation, no cost. Clients cannot be tricked into reporting detections, and there is nothing to desync.

That leaves one real problem: your **client UI** needs to know something. Detection meters, spectator overlays, "you are being watched" indicators. APS solves that with an opt-in replicated summary, so you do not have to hand-roll it.

---

## Turning on replication

**Profile → Replication:**

| Setting | Default | Meaning |
|---|---|---|
| `b Replicate Perception State` | false | Replicate a compact per-target summary |
| `Max Replicated Targets` | 3 | How many targets are included (1–8). Keep small — this is bandwidth on **every** AI. |
| `Replication Interval` | 0.25 s | Seconds between refreshes |

## Reading it on clients

Use **Get Replicated Perception State** — never the raw array.

```
Event On Replicated State Changed
  └─► Get Replicated Perception State
        → Out Targets   : array of Replicated Target State
        → Out Awareness : EAwarenessLevel
              └─► update your detection meter widget
```

Each `Replicated Target State` carries `Target`, `Confidence`, `State`, `Threat Level` and `Last Known Position`.

**On AI Replicated State Changed** fires on clients whenever the summary updates — bind it instead of polling on Tick.

---

## The relay — and why you should read this

A `UActorComponent` only reaches clients if its **owning actor replicates**. AIControllers do not — the engine keeps them server-side. So a perception component living on the AIController (which most AI tutorials recommend) can **never** replicate its own state. Nothing errors. The client just sees an empty array, forever.

APS handles this for you: when the profile enables replication and the component cannot replicate on its own, it automatically spawns an **APS Perception Relay** component on the possessed Pawn and pushes the summary through that. `Get Replicated Perception State` reads from wherever the data actually lives, so **placement stops mattering**.

You never have to add the relay by hand. Add it to your Pawn's Blueprint only if you want it visible in the component list.

### Simplest advice

**Put the Perception Core on the Pawn**, not the AIController. Everything replicates directly, the relay is never needed, and there is one less moving part.

Put it on the AIController when your AI possesses multiple pawn types and you want perception state to survive re-possession. The relay makes that work correctly.

---

## Checklist

- [ ] Perception Core on the **Pawn** (unless you have a reason to use the controller)
- [ ] `b Replicate Perception State` on, if clients need detection UI
- [ ] `Max Replicated Targets` set to the smallest number your UI actually needs
- [ ] Client UI reads **Get Replicated Perception State**, driven by **On AI Replicated State Changed**
- [ ] All `Emit Sound` / `Report Pain` / `Set Target Confidence` calls happen **on the server** (`Has Authority`)
- [ ] Cross-session memory is server-only — it will not run on clients, which is correct

## Common mistakes

| Symptom | Cause |
|---|---|
| Client sees an empty target array | Component is on the AIController and you are reading `Replicated Targets` directly. Use **Get Replicated Perception State**. |
| Detection meter never updates | `b Replicate Perception State` is off, or you are polling instead of binding `On Replicated State Changed` |
| Sounds are heard on the server but not registered | `Emit Sound` was called client-side only. Route it through a server RPC or call it from server-authoritative code. |
| Perception events never fire on clients | Correct and by design — perception is server-only. Replicate the *consequence*, not the perception. |
| Bandwidth spikes with many AI | Lower `Max Replicated Targets` to 1, raise `Replication Interval` to 0.5 s, and only enable replication on AI whose state the player actually needs to see |

---

## Performance note

Replication cost scales with **agent count × `Max Replicated Targets` ÷ `Replication Interval`**. With 50 AI at 3 targets and 0.25 s, that is 600 target-states per second on the wire.

Most projects only need this on the handful of AI currently near the player. A practical approach: keep replication **off** in the base profile and **on** in a "close range" profile variant, then swap with **Set Profile** when an AI comes within relevant distance of a player.

---

