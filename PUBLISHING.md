# Publishing these docs — step by step

*This file is for you, not for buyers.*

There are three ways to do this. Pick one:

| Path | Installs needed | Effort | Best if |
|---|---|---|---|
| **A · GitHub CLI** | `gh` (one command) | Lowest — two commands, then it's automated | You're happy pasting two commands |
| **B · GitHub Desktop** | GitHub Desktop app | Medium — clicking through a GUI | You want a visual app for editing later |
| **C · Browser only** | Nothing | Highest first time, fine after | You don't want to install anything |

All three end up in exactly the same place. **Path A is the least work.**

> ### ⚠ Before anything else
> Right now your `Docs` folder is the **only copy that exists**. One bad click in Explorer and it's gone.
> Publishing *is* your backup. Do it today even if the content isn't final — you can change everything afterwards.

---

# Part 0 · Safety — what if I delete something?

| What you delete | What happens |
|---|---|
| Your local `Docs` folder — **before** the first push | ❌ **Gone forever.** Only one copy exists right now. |
| Your local `Docs` folder — **after** pushing | ✅ Fine. Repo → green **Code** button → **Download ZIP** |
| A page, a paragraph, a line | ✅ Fine. Every version is kept — see [I broke something](#i-broke-something-and-want-to-undo-it) |
| The whole GitHub repo | ⚠ Recoverable for ~90 days via GitHub Support. Don't rely on it. |

Once pushed, you have **two independent copies** (your PC and GitHub) and GitHub keeps every version of every file, forever. That's the real reason to do this early.

---

# Path A · GitHub CLI (fastest)

**You run two commands. Everything after that can be automated.**

**1.** Open Command Prompt or PowerShell and run:

```bash
winget install --id GitHub.cli -e
```

**2.** Close the terminal, open a new one, and run:

```bash
gh auth login
```

Answer the prompts:

- **What account?** → `GitHub.com`
- **Preferred protocol?** → `HTTPS`
- **Authenticate Git with your GitHub credentials?** → `Y`
- **How would you like to authenticate?** → `Login with a web browser`
- Copy the one-time code it shows, press Enter, paste it in the browser, approve

**3.** That's your part done. The remaining steps — creating the repo, filling in your username, committing, pushing, enabling Pages — can all be run for you.

If you're doing it yourself, they are:

```bash
cd "C:/Users/ojhah/Downloads/Docs"
git init -b main
git add .
git commit -m "APS documentation"
gh repo create aps-docs --public --source=. --push
gh api -X POST repos/:owner/aps-docs/pages -f build_type=workflow
```

Then skip to [Step 10 — Watch it build](#step-10--watch-it-build).

> **Remember to replace `auragame33-sys`** in `mkdocs.yml` and `README.md` before committing — see [Step 6](#step-6--fill-in-your-username).

---

# Path C · Browser only (no installs)

**1.** Go to **[github.com](https://github.com)** → sign up (see [Step 1](#step-1--make-a-github-account) for the username warning).

**2.** Top-right **+** → **New repository**:

| Field | Value |
|---|---|
| Name | `aps-docs` |
| Visibility | **Public** |
| Add a README | ❌ leave unchecked |

Click **Create repository**.

**3.** On the empty repo page, click the **"uploading an existing file"** link.

**4.** Open your `Docs` folder in Explorer and drag these into the browser:

- the **`docs`** folder (drag the whole folder — structure is preserved)
- `mkdocs.yml`
- `requirements.txt`
- `README.md`
- `PUBLISHING.md`

Click **Commit changes**.

> You can't drag `.github` — Windows hides it and browsers skip dotfolders. Next step handles it.

**5.** Click **Add file → Create new file**. In the filename box type **exactly**:

```
.github/workflows/deploy.yml
```

Typing the `/` characters creates the folders automatically — you'll see them appear as you type.

Open your local `Docs\.github\workflows\deploy.yml` in Notepad, copy everything, paste it into the browser editor, then **Commit changes**.

**6.** Fill in your username: open `mkdocs.yml` in the repo → pencil icon ✏️ → replace `auragame33-sys` in both places → **Commit changes**. Do the same for `README.md`.

**7.** Continue at [Step 9 — Turn on GitHub Pages](#step-9--turn-on-github-pages).

### Editing in the browser afterwards

- **Change text** — open the file → ✏️ pencil → edit → **Commit changes**
- **Add an image** — go to `docs/assets` → **Add file → Upload files** → drag it in → Commit. Then edit the page and add `![Caption](assets/your-image.png)`
- **New page** — **Add file → Create new file**, name it `docs/whatever.md`, then add it to `nav:` in `mkdocs.yml`

No preview, and multi-file edits are tedious — but it works from any machine with a browser.

---

# Path B · GitHub Desktop (visual app)

**Time:** about 20 minutes the first time. After that, publishing an edit takes 30 seconds.

---


## Step 1 — Make a GitHub account

Go to **[github.com](https://github.com)** → **Sign up**.

> ⚠ **Your username becomes part of your docs URL.**
> If you pick `auragame`, your docs live at `auragame.github.io/aps-docs/`.
> Pick something you're happy putting on a store page. You can't change it easily later.

Verify your email when GitHub asks — the rest won't work until you do.

## Step 2 — Install GitHub Desktop

Go to **[desktop.github.com](https://desktop.github.com)** → **Download for Windows** → run the installer.

When it opens, click **Sign in to GitHub.com** and log in with the account from Step 1.

It will ask for your name and email — just click through, the defaults are fine.

## Step 3 — Create the repository

A "repository" (repo) is just a folder that GitHub tracks.

In GitHub Desktop: **File → New repository…**

Fill in exactly this:

| Field | Value |
|---|---|
| **Name** | `aps-docs` |
| **Description** | `Documentation for APS — Advanced Perception System` |
| **Local path** | Anywhere you like, e.g. `C:\Users\ojhah\Documents` |
| **Initialize with a README** | ❌ **leave unchecked** — we already have one |
| **Git ignore** | None |
| **License** | None |

Click **Create repository**.

> If you named it something other than `aps-docs`, that's fine — but you'll need to use *your* name everywhere this guide says `aps-docs`.

## Step 4 — Turn on hidden files in Windows

**Do not skip this.** Two of the files you need to copy are hidden, and if you miss them the site will never publish.

Open **File Explorer** → **View** ribbon → **Show** → tick **Hidden items**.

You'll now see files starting with a dot, like `.gitignore`.

## Step 5 — Copy the docs into the repo

**A.** In GitHub Desktop, click **Show in Explorer** (or **Repository → Show in Explorer**). This opens your new, empty `aps-docs` folder.

**B.** In another Explorer window, open:

```
C:\Users\ojhah\Downloads\Docs
```

**C.** Press **Ctrl+A** to select everything, then **Ctrl+C**.

You should have **9 items** selected:

```
.github            ← hidden folder — must be included
.gitignore         ← hidden file — must be included
docs
tools
APS-Documentation-ALL-IN-ONE.md
mkdocs.yml
PUBLISHING.md
README.md
requirements.txt
```

**D.** Switch to the `aps-docs` window and press **Ctrl+V**.

> ⚠ **Check that `.github` came across.** If it's missing, the site will never build. Copy it manually if needed.

## Step 6 — Fill in your username

Two files need your GitHub username. Open them in Notepad (right-click → Open with → Notepad) or, better, [VS Code](https://code.visualstudio.com).

**In `mkdocs.yml`** — near the top, replace `auragame33-sys` in **two** places:

```yaml
site_url: https://auragame33-sys.github.io/aps-docs/
repo_url: https://github.com/auragame33-sys/aps-docs
```

**In `README.md`** — replace `auragame33-sys` (several places), plus:

- `YOUR-FAB-LINK` → your Fab store page
- `YOUR-YOUTUBE-LINK` → your channel
- `YOUR-EMAIL` → your support email

> **Tip:** in Notepad use **Ctrl+H** (Replace) → find `auragame33-sys` → replace with yours → **Replace All**.

Save both files.

## Step 7 — Commit

Go back to GitHub Desktop. The left panel now lists about 30 changed files. That's correct.

At the bottom left there's a **Summary** box. Type:

```
APS documentation
```

Click the blue **Commit to main** button.

> "Commit" means *save a snapshot locally*. Nothing is online yet.

## Step 8 — Publish

Click **Publish repository** (big blue button, top of the window).

| Field | Value |
|---|---|
| **Name** | `aps-docs` |
| **Keep this code private** | ❌ **UNCHECK THIS** |

> ⚠ **The repo must be public.** GitHub Pages only publishes from private repos on a paid plan. Your documentation is public anyway — this repo holds no plugin source code.

Click **Publish repository**. Takes a few seconds.

## Step 9 — Turn on GitHub Pages

In your browser go to:

```
https://github.com/auragame33-sys/aps-docs
```

Then: **Settings** tab (top right) → **Pages** (left sidebar) → under **Build and deployment**, set **Source** to:

### **GitHub Actions**

There's no save button — it applies as soon as you pick it.

## Step 10 — Watch it build

Click the **Actions** tab (top of the repo page).

You'll see a run called **Deploy documentation**:

- 🟡 **Yellow dot** — building, wait
- ✅ **Green tick** — done, your site is live
- ❌ **Red X** — something failed, see [Troubleshooting](#troubleshooting) below

First build takes 2–3 minutes.

## Step 11 — Open your docs

```
https://auragame33-sys.github.io/aps-docs/
```

Sidebar, search, dark mode, the lot. **Put this link on your Fab page.**

---

# Everyday editing (all paths)

Once set up, the loop is four clicks.

## To change some text

1. Open the file in `aps-docs\docs\` — e.g. `docs\senses.md`
2. Edit it, save
3. **GitHub Desktop** → type a short summary like `Fix vision range typo` → **Commit to main**
4. Click **Push origin** (top of the window)

Wait ~2 minutes. The site updates itself.

> **Commit** saves locally. **Push** sends it to GitHub. You need **both** — this is the #1 thing beginners forget.

## To add an image

1. Save your PNG into `aps-docs\docs\assets\`
   Use a simple lowercase name, no spaces: `debug-sense-mode.png`
2. Open the page where you want it, add one line:

```markdown
![The Sense debug overlay](assets/debug-sense-mode.png)
```

The text in `[square brackets]` is the caption for screen readers. The path in `(round brackets)` is always `assets/` followed by your filename.

3. Commit → Push. Done.

**To control the size**, add a width:

```markdown
![Vision cone](assets/vision-cone.png){ width="600" }
```

## To add a whole new page

1. Create the file, e.g. `aps-docs\docs\changelog.md`
2. Open `mkdocs.yml` and add it to the `nav:` list where you want it in the sidebar:

```yaml
  - Build & ship:
      - Changelog: changelog.md
```

3. Commit → Push.

> A page not listed in `nav:` won't appear in the sidebar, even though the file exists.

## To preview before publishing (optional, recommended)

This shows you the real site on your own machine, updating live as you save. Much better than pushing and waiting.

**One-time:** install [Python](https://www.python.org/downloads/) (tick **"Add Python to PATH"** during install), then open Command Prompt in your `aps-docs` folder and run:

```bash
pip install -r requirements.txt
```

**Then, whenever you're editing:**

```bash
mkdocs serve
```

Open `http://127.0.0.1:8000` in your browser. Every time you save a file, the page refreshes itself. Press **Ctrl+C** in the Command Prompt to stop.

---

# Troubleshooting (all paths)

### ❌ Red X in the Actions tab

Click the failed run, then click the red step to read the error.

**Almost always a broken link.** The build runs in `--strict` mode, which deliberately fails if any page links to a file that doesn't exist. The error names the file and the bad link — fix it, commit, push.

### My site shows 404

- Is the repo **public**? (Settings → General → scroll to bottom)
- Is Pages **Source** set to **GitHub Actions**? (Settings → Pages)
- Has the Actions run finished with a green tick?
- Did you wait 2–3 minutes?

### The site loads but looks unstyled / broken

`site_url` in `mkdocs.yml` doesn't match your real URL. It must be exactly:

```
https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/
```

Including the trailing slash. Fix, commit, push.

### My changes aren't showing up

First: you committed but didn't **Push**. Check GitHub Desktop for a **Push origin** button with a number on it.

If you *did* push and the Actions run is green, it's your browser cache. Press **Ctrl+Shift+R** (hard refresh).

**This bites hardest when you edit `extra.css`.** GitHub Pages caches assets for 10 minutes and the stylesheet filename never changes, so the browser happily keeps the old one. Symptoms: your text edits appear but styling changes don't. Either hard-refresh, or wait 10 minutes.

### I edited the colours and nothing changed

Same cause as above — hard refresh with **Ctrl+Shift+R**. If you're iterating on the design a lot, use `mkdocs serve` locally instead; it reloads instantly with no caching.

## Changing the look

Everything visual is driven from the top of `docs/assets/extra.css`:

```css
:root {
  --aps-accent:      #ffb300;   /* your brand colour */
  --aps-accent-soft: rgba(255, 179, 0, 0.12);
  --aps-radius: 10px;           /* corner rounding */
  --aps-border: rgba(128, 138, 152, 0.22);
}
```

Change `--aps-accent` and the buttons, card hovers, active sidebar item, table hovers, callout bars and footer links all follow.

The header colour is separate — it's Material's palette in `mkdocs.yml`:

```yaml
      primary: black      # header / sidebar
      accent: amber       # links, focus states
```

Valid values are listed at [squidfunk.github.io/mkdocs-material/setup/changing-the-colors](https://squidfunk.github.io/mkdocs-material/setup/changing-the-colors/).

### Swapping in your logo

Replace these two files, keeping the same names:

```
docs/assets/logo.png      ← header logo (shown at 24×24 on a dark bar)
docs/assets/favicon.png   ← browser tab icon
```

Both are the plugin's own `Resources/Icon128.png`. If you switch to an SVG, update the two paths under `theme:` in `mkdocs.yml`.

**Make it a simplified single-colour mark, not your full wordmark** — at 24 pixels on a dark header, fine detail turns to mud.

### The Actions tab is empty — nothing ever ran

The `.github` folder didn't get copied. It's hidden in Windows. Turn on **Hidden items** (Step 4), copy it across, commit, push.

### An image doesn't appear

- Is it inside `docs\assets\`?
- Does the filename in your markdown match **exactly**, including capitals and `.png` vs `.jpg`?
- No spaces in the filename — use `my-image.png`, not `my image.png`

### I broke something and want to undo it

GitHub Desktop → **History** tab → right-click the bad commit → **Revert changes**. Then Push.

Nothing is ever really lost — every version is kept.

---

# Screenshots worth taking

`docs/assets/` is ready for them. In rough priority order:

1. The debug overlay mid-detection — vision cone plus the confidence readout
2. A Perception Profile open in the Details panel
3. The Add Component menu showing **Perception Core**
4. The Behavior Tree from the tutorial
5. Before/after — an AI seeing through a door vs. not

Keep the level, lighting and camera angle consistent across all of them. That consistency is most of what makes documentation *look* expensive.

---

# Adding your videos

Four pages have a placeholder ready — `index.md`, `getting-started.md`, `tutorial-complete-guard.md`, `debugging.md`.

Each looks like this:

```html
> **▶ Video walkthrough** — *Install and first detection (6 min).* Coming soon.
> When it is live, delete this block and uncomment the embed below.

<!-- VIDEO EMBED — replace VIDEO_ID with your YouTube id, then delete the comment markers
<div class="video">
  <iframe src="https://www.youtube.com/embed/VIDEO_ID" title="Install and first detection" allowfullscreen></iframe>
</div>
-->
```

To activate one:

1. Delete the two-line `>` blockquote
2. Delete the line starting `<!-- VIDEO EMBED` and the `-->` line
3. Replace `VIDEO_ID` with the id from your YouTube URL

For `youtube.com/watch?v=**dQw4w9WgXcQ**`, the id is `dQw4w9WgXcQ`.

Sizing is handled automatically on every screen — nothing else to do.

---

# Before you publish — checklist

- [ ] `auragame33-sys` replaced in `mkdocs.yml` (2 places) and `README.md`
- [ ] Fab link, YouTube link and support email filled into `README.md`
- [ ] **Engine versions** — `docs/index.md` says Unreal Engine 5.2. Update if you ship more.
- [ ] **Platforms** — `docs/index.md` says Win64 Editor + Game. Confirm or extend.
- [ ] **Support contact** added to the `docs/index.md` footer
- [ ] Repo is **public**
- [ ] Pages Source set to **GitHub Actions**
- [ ] Screenshots added — the biggest single jump in perceived quality
- [ ] Docs link added to your Fab page and to a short `README.md` inside the plugin folder

---

# Where the docs link goes

| Place | What to put |
|---|---|
| **Fab product page** | The docs URL near the top, plus the top half of `index.md` as the description |
| **GitHub repo** | `README.md` already handles this — it's the shop window, not the docs |
| **Inside the plugin** | A short `README.md` next to `APS.uplugin` with the docs URL and support email. Some buyers never revisit the store page. |
| **YouTube descriptions** | Link the matching docs page under every video |

---

# The all-in-one file

`APS-Documentation-ALL-IN-ONE.md` sits outside `docs/`, so it is **not** published as a page. It's every page in one file, in nav order, with cross-page links flattened to in-document anchors. Useful for an offline copy inside the plugin, sending to a reviewer, or feeding to an AI assistant.

**It is generated. Do not edit it by hand.** After changing anything in `docs/`, run:

```bash
python tools/build_all_in_one.py
```

and commit the result alongside your changes.

The script reads the page order straight from `mkdocs.yml`'s `nav:`, so a new page is picked up automatically once you add it there. It also converts mkdocs-material syntax — admonitions, content tabs, icon shortcodes — into plain markdown, because the single-file version is read on GitHub and in ordinary editors where that syntax renders as literal text.

CI runs `python tools/build_all_in_one.py --check` before building the site and **fails the build** if the committed file does not match what `docs/` would produce. That is deliberate: the file used to be maintained by hand, it drifted, and a stale offline copy is the one somebody reads.

---

# Checking the docs against the plugin

The site claims every default value and node name was read out of the source rather than inferred from property names. This makes that claim checkable:

```bash
python tools/check_against_source.py --source "C:/path/to/Advanced Perception System/Source"
```

It compares every value in a table with a **Default** column against the initialiser in the header, and every node named in an API table against the UFUNCTIONs that actually exist. Recipe tables in the tutorials are skipped — a recommended value is not a claim about a default.

It cannot run in CI, because the plugin source lives in a different repository. Run it locally before opening a sync PR. On the v3.0 pass it caught a replication default documented as `false` when the source says `true`.
