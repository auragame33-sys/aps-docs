# Memory & Recall

**APS gives the AI somewhere to put a thought. What goes in, when it comes back out, and what it means are yours.**

The perception pipeline already tracks *where* a target is and *how sure* the AI is about it. Memory is the separate question: what does this AI know about that target, in your game's terms?

APS deliberately does not answer that. It does not decide that clothing matters, or vehicles, or which hand you swung with. It gives you a tagged store per agent, and your logic decides what to write and what to do about it.

!!! quote "The brain analogy"
    Senses notice. Thoughts decide. APS is the first half — it hands you the
    observation and the place to file it. What the AI *concludes* is your
    Behavior Tree, your Blueprint, your game.

---

## What a memory is

A memory is a **tag** on a **subject**, plus optional payload.

| Field | Type | Holds |
|---|---|---|
| `Tag` | Name | What this memory is — `"WoreRed"`, `"AttackedMe"`, `"DroveTruck"` |
| `Number` | Float | A count, a strength, a damage total — whatever the tag means |
| `Place` | Vector | A location the memory is about |
| `Related Actor` | Actor | Another actor the memory is about — an accomplice, a vehicle, a weapon |
| `Count` | Int | Times this tag has been written for this subject. Maintained for you |
| `Age` | Float | Seconds since it was last written. Maintained for you |

`Count` and `Age` are the two you did not have to think about, and they are usually the two that make the behaviour interesting — *"he has done this four times"* and *"that was a long time ago"* are different beliefs from *"he did this"*.

## What a subject is

Something to remember *about*. Either an actor, or a place.

=== "An actor"

    ```
    Make Actor Subject (Player)  →  Subject
    ```

=== "A place"

    ```
    Make Place Subject (Location, "BackAlley")  →  Subject
    ```

Places are subjects in their own right, so an AI can hold beliefs about a doorway it does not like without any actor being involved.

---

## Writing

**Remember** (`Subject`, `Tag`, `Number`, `Place`, `Related Actor`)

Everything after `Tag` is optional. Writing the same tag again updates it and increments `Count` rather than adding a duplicate.

```
On AI Detect (Target)
  → Make Actor Subject (Target)
  → Remember (Subject, "SeenNearVault", Place: Target Location)
```

That is the whole integration. There is no registration step, no schema, and no list of allowed tags.

## Reading

| Node | Returns |
|---|---|
| **Recall** (`Subject`) | Every memory about that subject, newest first. False if none |
| **Recall Tag** (`Subject`, `Tag`) | One specific memory. False if never written |
| **Has Memory Of** (`Subject`) | Whether anything at all is held |
| **Get Remembered Subject Count** | How many distinct subjects this agent holds |

!!! warning "There is no 'on recall' event, on purpose"
    APS never tells you *now is the moment to remember something*. That decision
    is the interesting part of your AI, and a firing event would be APS making it
    for you — you would be reacting to APS's idea of a relevant moment instead of
    your own.

    Call **Recall** where your logic actually wants to know: on detect, on a
    Behavior Tree decorator, when choosing a line of dialogue, when picking a
    search point.

## Forgetting

| Node | Effect |
|---|---|
| **Forget** (`Subject`, `Tag`) | Drops one tag |
| **Forget Subject** (`Subject`) | Drops everything about one subject |
| **Forget Everything** | Wipes this agent's store |

**Forget Everything** is what you ship on a difficulty reset, a new chapter, or an accessibility toggle for players who do not want the AI accumulating anything about them.

---

## It does not survive the session

There is no save file, and no cross-session persistence. A freshly spawned AI is a fresh mind: it has met nobody and remembers nothing until it perceives something itself.

This is a deliberate design decision, not a missing feature. An AI that already knows the player at the instant it spawns is hard to reason about, hard to test, and almost never what was actually wanted — and keying a save file to a runtime actor ID is unreliable in the first place.

!!! info "If you *do* want it to persist"
    **Recall** the memories you care about, write them into your own save game
    alongside everything else you persist, and **Remember** them back on load.
    Your game already knows what a save means; APS does not, and guessing would
    be worse than asking.

## Limits

Three profile settings under **Memory**, all with sensible defaults:

| Setting | Default | Meaning |
|---|---|---|
| `Memory Max Subjects` | 32 | Distinct subjects per agent. The least recently written is dropped past this |
| `Memory Max Tags Per Subject` | 16 | Distinct tags per subject. The oldest is dropped past this |
| `Memory Retention Seconds` | 300 | A subject untouched for this long is released |

These exist so an agent that meets a great many things releases them without anyone having to think about it. Raise them for a boss that should hold a grudge; lower them for a crowd.

---

## Worked example: a witness who builds a case

None of the following is APS logic. It is what *you* write, using the store APS gives you.

```
On AI Detect (Suspect)
  → Make Actor Subject (Suspect) → S
  → Remember (S, "SeenAtScene", Place: Suspect Location)
  → Branch: Suspect is holding a weapon?
      → Remember (S, "Armed")

On Damaged By (Instigator)
  → Make Actor Subject (Instigator) → S
  → Remember (S, "AttackedMe", Number: Damage)
```

Later, when the AI decides how to react:

```
Recall Tag (S, "AttackedMe") → Memory
  → Branch: Memory.Count >= 3
      → this one is not a suspect any more, they are a threat
  → Branch: Memory.Age > 120
      → it was a while ago; challenge rather than open fire
```

The behaviour — three strikes, a two-minute cooling-off — is entirely yours. APS supplied `Count`, `Age`, and somewhere to put `"AttackedMe"`.

Swap the tags and the same code is a shopkeeper who remembers shoplifters, a wolf that remembers which clearing hurt it, or a detective who remembers what you were wearing.

---

## See also

- **[Evidence & Search](evidence-and-search.md)** — things left in the world that an AI can find and form beliefs about
- **[Knowledge & Comms](knowledge-and-comms.md)** — sharing what one AI knows with a faction, with latency and fidelity loss
- **[Player Behavior Model](player-behavior-model.md)** — the separate, automatic model of *how* a player plays
