# Changes from upstream

This is the Asciiverse packaging of [clidle](https://github.com/ajeetdsouza/clidle)
by Ajeet D'Souza: a five-letter word-guessing game in the style of
Wordle, in the terminal (Go, Bubble Tea and Lip Gloss), which also runs
as an SSH server (`clidle -serve 0.0.0.0:1337`). Upstream is the
`upstream` remote; the `asciiverse` branch carries the changes below.

Built from upstream `main` at `fb05b78` (2026-10-08, "Update domain"),
the newest commit, after its one release, v0.1.0 (2024-10-31). The
catalog title is "clidle", the author's own name for it. It replaces
wordl (palerdot/wordl-rs) in the catalog: the same game, and clidle is
maintained, keeps a score, and fits small terminals; wordl's slow reveal
and Esc to quit are brought over (below).

## Licence

MIT (LICENSE, "Copyright (c) 2022 Ajeet D'Souza"). The Go modules built
into the binary are MIT or BSD-style (checked module by module
2026-10-20): the Charm libraries, adrg/xdg, creack/pty and others MIT;
golang.org/x, google/uuid, pkg/errors, modernc.org/sqlite and its
libc, memory and mathutil, remyoudompheng/bigfft and charmbracelet/ssh
BSD-style.

## Word lists

Kept as shipped, in `dictionary.go`: 2,315 possible answers, and 12,972
accepted guesses that include them, the sizes of the original Wordle
lists. The repository
names no source for them. The catalog never presents clidle as the New
York Times game.

## Saved files

The total score and every game and guess are kept in an SQLite database,
`clidle/clidle.db` in the XDG data folder (`~/.local/share/clidle` on
Linux, `~/Library/Application Support/clidle` on macOS,
`%LOCALAPPDATA%\clidle` on Windows, by adrg/xdg), or in
`$CLIDLE_DATA_DIR`. Nothing to change.

## Code

Each of these is its own commit, written to be offered upstream as a
pull request:

- **Truncate the status line before styling it.** The status line was
  truncated after Lip Gloss had added its colour codes, so they counted
  towards its length and the closing code was cut: at 30 columns, "Your
  guess must be a 5-letter word." showed as "Your gue...". The plain text
  is truncated first ("Your guess must be a 5-lett...").
- **Quit with Esc as well as Ctrl+C.** The help line shows Esc.
- **Reveal the colours of a guess one letter at a time** (after wordl's
  "slow reveal", here 300 ms a letter, with the letters visible while
  they turn). The keyboard and the result are updated once the whole
  guess is revealed; typing waits; Ctrl+R during a reveal starts a new
  game cleanly.
- **Keep the status line in view when the window is short.** The fit
  check left out the help line and a dropped keyboard still took a line,
  so at 30 rows (status 1, board 18, keyboard 11, help 1) the status line
  with the score and the result was cut off the top. Shown parts are
  joined without blanks; the keyboard is kept over the help line, and the
  help line is shown when the keyboard does not fit either.

## Packaging

- Upstream's workflows (`goreleaser.yml`, its own releases;
  `docker-push.yml`, its server's image; `golangci-lint.yml`) are removed
  in this fork. `.goreleaser.yaml`, `Dockerfile` and `.deepsource.toml`
  stay, unused.
- `.github/workflows/release.yml`: av archives `clidle-<target>` for
  Linux (x86-64, ARM64; static, CGO off), macOS (x86-64, ARM64) and
  Windows (x86-64, ARM64), with the binary, LICENSE, README.md and this
  file, plus SHA256SUMS. Runs on our tags only (`*-av.*`).
- `asciiverse/drive.py` records the catalog preview,
  `asciiverse/clidle.cast` (adapted from wordl's driver): asciinema runs
  `clidle` in a 100x30 tmux session while the script types guesses,
  reads each revealed row's colours from the pane and narrows clidle's
  answer list (one typo cleared with Backspace on the way), then Ctrl+R
  and one guess of a new game, then Esc. The answer is random; the
  catalog's take is five guesses to PIXEL, the best of six.

av starts it as `clidle` with no arguments.

## Checked

Linux, static build (Go 1.26.8, CGO off), in tmux: guesses revealed
letter by letter (colours timed at 0.15, 0.45, 0.75 and 1.75 s),
typing during a reveal ignored, Ctrl+R mid-reveal, a win shown only
after the reveal ("Score: 0" at 0.5 s, "You win!" at 2.1 s, "Score: 90"
after Enter), an incomplete guess at 30 columns, Esc and Ctrl+C quit
with status 0; layout at 100x31, 100x30, 80x24, 80x20, 60x19, 50x31 and
40x12. Windows: cross-built (amd64) and run under Wine: starts, takes
guesses, saves in `%LOCALAPPDATA%\clidle`, Esc quits with status 0;
Wine's console turns the box drawing into "?", so the look on real
Windows is unchecked. macOS: not built here.

## Ours

- **How to play it, at the top of README.md.** A short note on installing and
  starting it with av, or from a release archive; the original text follows
  unchanged.
