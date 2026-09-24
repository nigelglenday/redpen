```
                 __
    _ _ ___ ____/ /___  ___ ___
   | '_/ -_) _  / _ \ \/ -_) _ \
   |_| \___\_,_/ .__/_/\___/_//_/
              /_/
   mark up any page. the agent gets the element.
```

[![license](https://img.shields.io/badge/license-MIT-black)](LICENSE)
[![macOS · Linux](https://img.shields.io/badge/macOS%20%C2%B7%20Linux-supported-black)](#)
[![python 3.9+](https://img.shields.io/badge/python-3.9%2B-black)](#)
[![dependencies](https://img.shields.io/badge/dependencies-none-e11)](#)
[![part of termpaper.dev](https://img.shields.io/badge/part%20of-termpaper.dev-e11)](https://termpaper.dev)

You asked an agent to build something, and it made you a page. Now you want to
change eleven things on it.

Without this you screenshot the page and describe what you mean. *"The bullet
under the second heading, make it shorter."* The agent hunts for it, finds a
similar string somewhere else, and edits the wrong one.

**redpen serves the page with a comment overlay.** You highlight the thing, type
what you want, and the agent receives the CSS selector, the element's own HTML,
and the text you selected. It acts on the node, not on your description of it.

```bash
redpen ./build --port 8801
open http://localhost:8801/report.html
```

---

## What you get

- **Comment on anything.** Select text and press `A`, `⌥`-click any element, or
  shift-drag a box. Commenting on a *place* matters as much as on words: "add a
  bullet here" has nothing to highlight.
- **Pins on the page**, numbered, anchored by CSS selector so they survive a
  re-render. Open ones are red; processed ones grey, or hidden.
- **A sidebar** grouping comments by page, with open and processed counts, and
  who the comments are going to.
- **Process in batches.** Comment as you read, then send the lot. Or one at a
  time from its row.
- **Nothing is pushed on you.** The page never reloads itself. When work comes
  back, a banner offers a refresh.

## What an agent receives

One JSON file per comment, next to the files being served:

```json
{
  "comment": "make this shorter, it runs to three lines",
  "selected_text": "Shipment updates arrive by email and are reconciled by hand",
  "selector": "#exec-summary > ul > li:nth-child(1)",
  "element_html": "<li><b>Current state.</b> Shipment updates arrive…</li>",
  "document": "/report.html",
  "source_file": "/Users/you/project/build/report.html",
  "agent": "report-writer",
  "rect": { "x": 164, "y": 322, "w": 618, "h": 52 },
  "at": "2026-09-24T21:51:00Z"
}
```

`source_file` is the point. An agent should not have to map `/report.html` back
to somewhere on disk, because getting that wrong means editing the wrong copy
when a build directory, a published mirror and a repo all hold that filename.

**Open and processed are the filesystem, not a protocol.** A comment is open
while its file sits in `.annotations/`, and processed once something moves it to
`.annotations/done/`. That is all the state there is, so both sides can read it
and neither has to agree with the other about anything.

## Telling an agent about it

redpen does not know who should act on a comment, and deliberately does not
learn. Give it a command and it runs it:

```bash
redpen ./build --on-send ./examples/deliver-tmux --to report-writer
```

The hook gets the annotations directory and the chosen filenames. Its exit code
is the whole contract:

| exit | meaning |
|---|---|
| `0` | delivered. Last line of stdout names who was reached |
| `75` | not now. redpen queues these and retries until it works |
| other | permanent. redpen stops trying and says why |

`75` matters more than it sounds. Process three comments in a row and the first
wakes your agent, which is then busy, so the second would fail. Instead they
stack up and arrive together as one message.

With `REDPEN_PROBE=1` and no files, print the name you would reach and deliver
nothing. That is how the sidebar can say *goes to report-writer* before you send
anything.

See [`examples/deliver-tmux`](examples/deliver-tmux) for a working one.

## Everything else

```
redpen <dir>                     serve a directory
redpen . --proxy localhost:3000  put the overlay in front of a running dev server
redpen <dir> --local             bind 127.0.0.1 instead of the LAN address
redpen <dir> --no-send           collect comments, wake nobody
redpen --bookmarklet             the overlay for a page you do not serve
```

| key | |
|---|---|
| `A` | comment on selected text |
| `⌥` click | comment on the selection, or on the element under the cursor |
| shift-drag | comment on a region |
| `enter` | save it and keep reading |
| `⌥ enter` | save and process it now |
| `esc` | cancel |

One modifier for the whole tool. Nothing needs two.

## Install

```bash
curl -O https://raw.githubusercontent.com/nigelglenday/redpen/main/redpen
chmod +x redpen && mv redpen ~/.local/bin/
```

Python 3.9+, standard library only. No packages, no build step, one file.

## Why it works this way

**It serves the page rather than living in the browser.** An extension cannot
write files next to the thing you are reviewing, and copying comments back by
hand is the step this exists to delete.

**Delivery is a hook.** Who to wake is local knowledge: a tmux session, a
webhook, an issue tracker, a notification. Baking any of that in is what makes a
tool feel like someone else's dotfiles.

**The comment is the record, the notification is best effort.** Every comment is
stamped with its recipient at save time, so a failed delivery costs latency, not
the comment.

---

Part of [termpaper.dev](https://termpaper.dev) · MIT
