# Changelog

All notable changes to redpen. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-11-20

### Added
- **Esc inside a framed page reaches the page around it.** When a redpen page is shown
  inside another page (Compass's Catch up shows the card's page beside the card) and no
  comment box, drag box or edit mode is open, Esc posts `{redpen: 'escape'}` to the parent
  window, so the parent can take the keyboard back. A page not in a frame is unchanged.
  redpen pages already allow framing (no X-Frame-Options or frame-ancestors).
  atlas-tools#128.

## [0.3.0] - 2026-11-19

### Added
- **A server stops itself after 24 hours unused.** `--idle-hours H` sets the limit
  (0 = never). A page load, comment or edit counts as use; the overlay's background
  poll does not, so an open tab does not keep it alive. Queued comments are delivered
  before it stops. 45 forgotten servers had piled up on the M3 (toolkit#36).

## [0.2.1] - 2026-11-03

### Added
- **First version recorded in this changelog.** Changes before it are in the git history:
  `git log -- redpen`.
