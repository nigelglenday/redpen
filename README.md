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
- **Pins in the left gutter**, numbered, anchored by CSS selector so they survive
  a re-render. Open ones are red; processed ones grey, or hidden. They sit beside
  the line they mark rather than on top of it, because a review tool that hides
  the text being reviewed is worse than no pin at all.
- **A sidebar** grouping comments by page, with open and processed counts, and
  who the comments are going to.
- **Edit the text itself.** Press `E`, click any paragraph and type over it.
  For wording, a rewrite says it better than a comment describing one. See
  [Edit mode](#edit-mode).
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

Every record has a `type`. A comment is `"comment"` (records written before
0.2.0 have no `type`; treat that as a comment). An edit from
[Edit mode](#edit-mode) is `"edit"` and carries the text before and after
instead of a comment:

```json
{
  "type": "edit",
  "old_text": "Current state. Shipment updates arrive by email and are reconciled by hand every Friday.",
  "new_text": "Current state. Shipment updates arrive by email and are reconciled in a spreadsheet every Friday.",
  "diff": [
    { "op": "equal",  "text": "Current state. Shipment updates arrive by email and are reconciled " },
    { "op": "delete", "text": "by hand" },
    { "op": "insert", "text": "in a spreadsheet" },
    { "op": "equal",  "text": " every Friday." }
  ],
  "selector": "#exec-summary > p:nth-of-type(1)",
  "element_html": "<p><b>Current state.</b> Shipment updates arrive by email and are reconciled by hand every Friday.</p>",
  "new_html": "<p><b>Current state.</b> Shipment updates arrive by email and are reconciled in a spreadsheet every Friday.</p>",
  "document": "/report.html",
  "source_file": "/Users/you/project/build/report.html",
  "agent": "report-writer",
  "rect": { "x": 164, "y": 210, "w": 618, "h": 52 },
  "at": "2026-11-03T21:07:35Z"
}
```

`element_html` is the block as it was before the edit, `new_html` as it was
sent. `diff` is word level: joining the `equal` and `delete` parts gives
`old_text`, joining `equal` and `insert` gives `new_text`.

**Applying an edit.** The served page is usually built from something else, so
an edit to the HTML on disk gets overwritten by the next build. Apply it to the
source:

1. Find the block in the source (HTML, Markdown or the script that generates
   the page) by fragments of `old_text`, using `element_html` to tell apart two
   blocks with similar wording.
2. Change it to read as `new_text`, keeping the inline markup that survived the
   edit: a bold lead-in, a link, emphasis. `new_html` shows which of it did.
3. Rebuild whatever is being served, show the result (a redline, old struck and
   new underlined, is the quickest way to review a set of edits), and move the
   file to `done/`.
4. If you cannot place an edit with confidence, do not guess. Reply on the
   thread (append to `replies`, move it to `answered/`) and say what you could
   not find.

**State is the filesystem, not a protocol.** Three directories, and `ls` tells
you where a comment stands:

```
.annotations/            open      needs the agent     red pin
.annotations/answered/   answered  needs a human       amber pin
.annotations/done/       done      closed              grey pin
```

That is all the state there is, so both sides can read it and neither has to
agree with the other about anything.

## Threads, for when a comment is a question

Some comments are not instructions. *"Should this be 90 days or 60?"* has no
change to make, and before `answered/` existed the agent's only way to respond
was to make one: pick a number and silently commit you, or do nothing. Both are
bad, and the first is bad in a way nobody notices.

An agent answers by writing the file. Append to `replies` and move it to
`answered/`:

```json
"replies": [
  { "by": "agent", "text": "90. It is what the template says and nobody objected.",
    "at": "2026-09-26T12:05:00Z" }
]
```

The pin turns amber, the thread appears under the comment it belongs to, and a
reply box goes back to the same agent. Replying **reopens** the thread: the file
moves back to `.annotations/`, and the delivery hook fires exactly as it does for
a new comment.

It stops there on purpose. Reply and reopen is a review loop; anything more is a
chat client, which this is not.

## Edit mode

For wording, a comment is the long way round. *"Change 'by hand' to 'in a
spreadsheet'"* is a description of an edit; typing it is the edit. Edit mode is
suggesting mode for a served page:

1. Press `E`, or click the **edit text** tab under the comments tab. An
   **EDITING** bar appears at the top of the page.
2. Click any text. Its block (a paragraph, list item, heading, table cell,
   quote, caption) gets a cursor where you clicked. Delete, retype, select a
   phrase and type over it. Paste is plain text only. Enter is a line break,
   not a new paragraph.
3. Edit as many blocks as you like. Changed ones are tinted so you can see what
   you touched. A block you put back exactly as it was is not an edit.
4. **send edits** (or `⌘ enter`) saves one record per changed block and
   delivers them together, exactly like processing a batch of comments. Sent
   blocks turn green and edit mode stays on. **discard** (click twice) puts
   every unsent block back as it was.
5. `esc`, `E` again (outside a block) or the `×` on the bar leaves edit mode.
   Unsent edits stay on the page and in the bar until you send or discard them.

While editing, links do not navigate, pins do not take clicks, and the comment
gestures (`A`, shift-drag) are off, so a click always means "put the cursor
here". Edits show in the drawer next to comments, old text struck and new text
underlined, and delete the same way.

The page itself is never saved. The edit goes to the agent, which changes the
source and rebuilds; see [Applying an edit](#what-an-agent-receives).

Edits are per block. Merging two paragraphs or moving a sentence between them
is out of scope; say that in a comment.

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

Whatever your hook says to the agent, it should cover both record types: a
`comment` is an instruction or a question, an `edit` is new wording to apply to
the source as described under [Applying an edit](#what-an-agent-receives).

**The overlay never prints.** A PDF of the page is the deliverable; the tab,
drawer and pins are scaffolding for reviewing it. If you script the print,
render from the file rather than through redpen: the overlay polls for work
coming back, so `chrome --headless --print-to-pdf` against a served page writes
the PDF and then does not exit.

## Everything else

```
redpen <dir>                     serve a directory
redpen . --proxy localhost:3000  put the overlay in front of a running dev server
redpen <dir> --local             bind 127.0.0.1 instead of the LAN address
redpen <dir> --no-send           collect comments, wake nobody
redpen --bookmarklet             the overlay for a page you do not serve
redpen --overlay                 print the overlay JavaScript, for vendoring
```

### Vendoring the overlay

If you are serving the overlay from your own application rather than from
redpen, pin it. Do not read it out of a working copy: the result then depends on
the state of one checkout on one machine, and two builds of your app from the
same commit can differ.

```bash
git show <commit>:redpen > /tmp/redpen && python3 /tmp/redpen --overlay > vendor/overlay.js
node --check vendor/overlay.js
```

`--overlay` needs no directory, no port and no running server, and emits exactly
the bytes `/__annotate.js` serves, from the same extractor. Record the commit
next to the file and fail your build when they disagree, so an upgrade is a diff
someone reviewed.

There is deliberately no `overlay.js` in this repo. redpen is one file you can
`curl`, and a second copy of the same code is a second copy that drifts.

| key | |
|---|---|
| `A` | comment on selected text |
| `⌥` click | comment on the selection, or on the element under the cursor |
| shift-drag | comment on a region |
| `enter` | save it and keep reading, or send a reply on an answered thread |
| `⌥ enter` | save and process it now |
| `esc` | cancel, or leave edit mode |
| `E` | edit mode on or off |
| `⌘ enter` | in edit mode, send edits |

One modifier for commenting. Nothing needs two.

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
