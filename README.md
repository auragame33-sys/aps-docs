<h1 align="center">APS — Advanced Perception System</h1>

<p align="center">
  <strong>An 8-sense belief-based AI perception engine for Unreal Engine 5.</strong><br>
  Blueprint-first. Zero C++ required.
</p>

<p align="center">
  <a href="https://auragame33-sys.github.io/aps-docs/"><b>📖 Documentation</b></a>
  <!-- Add these once they exist — replace the URL, then move the line above the comment:
  · <a href="FAB-URL-HERE"><b>🛒 Get it on Fab</b></a>
  · <a href="YOUTUBE-URL-HERE"><b>▶ Video tutorials</b></a>
  -->
</p>

---

## What it does

APS replaces Unreal's built-in `AIPerception` with a system that models **belief** instead of **booleans**.

Your AI does not flip between "sees you" and "does not see you". It builds confidence over time from every sense it owns, fuses them into one value per target, remembers what it lost, records *why* it lost you, guesses where you went, and reacts emotionally.

## Core systems

- **8 senses** — Vision, Hearing, Smell, Touch, Vibration, Damage, Pain, Echolocation. Up to 8 run per AI at once, and you can add your own in Blueprint.
- **Belief lifecycle** — Undetected → Suspected → Detected → Tracked → Lost → Remembered → Expired, with a Blueprint event on every transition.
- **Multi-point visibility** — traces against head, chest, pelvis and shoulders for a *percentage exposed*, not a yes/no. Partial cover finally behaves like partial cover.
- **Three vision cones** — focal, peripheral, and a rear cone that only registers moving targets. Plus keyhole vision.
- **Real occlusion** — multi-channel line of sight with per-surface transmission. Glass is transparent, foliage dampens, concrete blocks.
- **Loss reasons** — the AI knows *why* it lost you (occluded, out of range, sound faded, scent lost), so it can search intelligently instead of sweeping randomly.
- **Spatial belief** — last known position, velocity estimation, an uncertainty radius that grows while you hide, and predictive extrapolation.
- **Threat & emotion** — weighted threat scoring and five emotion channels driven by perception.
- **Squad coordination** — range-gated intel sharing, positional alerts, exclusive combat roles.
- **Player behaviour model** — observes how you play using only what the AI could legitimately perceive, and can persist it across sessions.
- **Fairness tooling** — reaction delay, telegraph events, off-screen hearing penalty, designer-defined safe rooms.
- **7-mode debug suite** — on-screen overlays plus a one-node print function for every event.

## Requirements

| | |
|---|---|
| Engine | Unreal Engine 5.2 |
| Project type | Blueprint or C++ (Blueprint-only works — the plugin ships its own compiled module) |
| Platforms | Win64 Editor + Game |
| Dependencies | None beyond engine modules |
| Network | Server-authoritative, with an opt-in replicated summary for client UI |

## Documentation

Full documentation — install, tutorials, 25 task recipes, complete API and settings reference — lives at:

### 👉 **[auragame33-sys.github.io/aps-docs](https://auragame33-sys.github.io/aps-docs/)**

Start with [Install & Your First AI](https://auragame33-sys.github.io/aps-docs/getting-started/), then [Tutorial: A Complete Guard](https://auragame33-sys.github.io/aps-docs/tutorial-complete-guard/).

Already using Epic's `AIPerception`? There's a [migration guide](https://auragame33-sys.github.io/aps-docs/migrating-from-aiperception/).

## Support

- **Questions and bug reports** — [open an issue](https://github.com/auragame33-sys/aps-docs/issues)

<!-- Add a support email here if you want one. Note it will be public and will attract spam;
     many plugin authors deliberately use GitHub Issues only. -->


---

> **Note**
> This repository hosts the documentation only. Plugin source code and binaries are distributed through Fab, not here.

<p align="center"><sub>© 2026 AuraGame. All rights reserved.</sub></p>
