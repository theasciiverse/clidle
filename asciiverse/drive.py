#!/usr/bin/env python3
"""Records asciiverse/clidle.cast, the catalog preview, at 100x30.

Usage: drive.py <clidle binary> <out.cast>

asciinema rec runs `clidle` (by name, from a throwaway folder on PATH, with
a throwaway data folder) in a detached 100x30 tmux session. This script
types guesses, reads the colours of each revealed row from the pane and
narrows the answer list (clidle's own, from dictionary.go) down, the way a
player would, until the word is found; then it starts a new game with
Ctrl+R, types one guess and quits with Esc. Adapted from wordl's driver.
Needs tmux and asciinema 3."""
import os, re, shutil, subprocess, sys, tempfile, time

binary, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
here = os.path.dirname(os.path.abspath(__file__))
source = open(os.path.join(here, "..", "dictionary.go")).read()
common = source[source.index("commonWords:"):source.index("allWords:")]
answers = [w.lower() for w in re.findall(r'"([A-Z]{5})"', common)]

S = f"clidle-preview-{os.getpid()}"
TMUX = ["tmux", "-L", S]
home = tempfile.mkdtemp()
shutil.copy(binary, os.path.join(home, "clidle"))
env = dict(os.environ, HOME=home, PATH=home + ":" + os.environ["PATH"],
           XDG_DATA_HOME=os.path.join(home, "data"),
           TERM="xterm-256color", COLORTERM="truecolor", LANG="C.UTF-8",
           USER="player", LOGNAME="player")
for k in ("VTE_VERSION", "TERM_PROGRAM", "TERM_PROGRAM_VERSION", "TMUX", "CLIDLE_DATA_DIR"):
    env.pop(k, None)

def key(*k):
    subprocess.run(TMUX + ["send-keys", "-t", S, *k])

def typ(word):
    for ch in word:
        key(ch)
        time.sleep(0.14)

# the game's colours for a revealed letter (model.go, keyState.color); tmux
# reports the grey as 97;97;97
COLOURS = {(83, 141, 78): "g", (181, 159, 59): "y", (97, 97, 97): "-", (98, 98, 98): "-"}
LETTER = re.compile(r"\x1b\[38;2;(\d+);(\d+);(\d+)m([A-Z])\x1b")

def board():
    """The colour of each letter in the board's rows, top to bottom, read
    from `tmux capture-pane -e`: rows of exactly five coloured letters (the
    keyboard's rows are longer)."""
    lines = subprocess.run(TMUX + ["capture-pane", "-e", "-p", "-t", S],
                           capture_output=True, text=True).stdout.split("\n")
    rows = []
    for line in lines:
        cells = LETTER.findall(line)
        if len(cells) == 5:
            rows.append("".join(COLOURS.get(tuple(map(int, c[:3])), "?") for c in cells))
    return rows

def feedback(guess, answer):
    res, left = ["-"] * 5, {}
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            res[i] = "g"
        else:
            left[a] = left.get(a, 0) + 1
    for i, g in enumerate(guess):
        if res[i] != "g" and left.get(g, 0):
            res[i] = "y"; left[g] -= 1
    return "".join(res)

def best(cands):
    """The candidate whose worst-case leftover group is smallest."""
    if len(cands) <= 2:
        return cands[0]
    def worst(g):
        groups = {}
        for a in cands:
            f = feedback(g, a); groups[f] = groups.get(f, 0) + 1
        return max(groups.values())
    return min(cands, key=worst)

cmd = ("env TERM=xterm-256color asciinema rec --overwrite -q --window-size 100x30 --idle-time-limit 2"
       " --title clidle --capture-env TERM,COLORTERM,LANG -c clidle " + out)
subprocess.run(TMUX + ["new-session", "-d", "-s", S, "-x", "100", "-y", "30",
                       "-c", home, cmd], env=env, check=True)
try:
    time.sleep(2.5)
    cands, guess, row = list(answers), "crane", 0
    while True:
        if row == 1:                   # one typo, cleared with Backspace
            typ(guess[:3] + "x"); time.sleep(0.4)
            key("BSpace"); time.sleep(0.3); typ(guess[3:])
        else:
            typ(guess)
        time.sleep(0.5); key("Enter"); time.sleep(2.6)
        rows = board()
        seen = rows[row] if row < len(rows) else "?????"
        print(guess, seen, file=sys.stderr)
        if seen == "ggggg":
            break
        cands = [a for a in cands if feedback(guess, a) == seen] or cands
        guess, row = best(cands), row + 1
        if row == 6:
            break
    time.sleep(4.0)
    key("C-r"); time.sleep(1.5)
    typ("slate"); time.sleep(0.5); key("Enter"); time.sleep(3.5)
    key("Escape")
    for _ in range(50):
        r = subprocess.run(TMUX + ["has-session", "-t", S], capture_output=True)
        if r.returncode:
            break
        time.sleep(0.1)
finally:
    subprocess.run(TMUX + ["kill-server"], capture_output=True)
    shutil.rmtree(home, ignore_errors=True)
