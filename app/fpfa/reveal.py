"""How a reply's words come into the thread.

Words arrive from the API in bursts, and a tool-plan reply arrives all at
once. The thread shows them at a reading pace instead. Each frame reveals
part of the backlog (reveal_step), the newest words fade in from the
background colour, and a finished reply carries on from the words already on
screen (align_shown) instead of replacing them.

The pacing rules and their constants are copied from Spec Surgeon's
frontend/src/lib/reveal.ts and adapted to Python, so the three apps move
alike. Nothing here imports tkinter: ui.py owns the clock and the Text
widget, and the tests can pin every rule without a display.
"""

from __future__ import annotations

import math
from collections import deque

# How long a revealed piece takes to fade in, in milliseconds.
FADE_MS = 520.0
# The backlog drains with this time constant, in seconds: 800 characters show in about a second.
REVEAL_TAU = 0.3
# The slowest pace, in characters a second, so the last words of a burst never trickle.
REVEAL_MIN_RATE = 150.0
# A frame after a pause counts as at most this long, so a stalled window does not dump its backlog.
MAX_FRAME_SECONDS = 0.25


def reveal_step(backlog: int, dt: float) -> float:
    """Characters to reveal in a frame dt seconds long with backlog characters waiting.

    A fraction. The caller carries what is left into the next frame, so the
    pace is the same at any frame rate.
    """
    if backlog <= 0:
        return 0.0
    seconds = max(dt, 0.0)
    eased = backlog * (1.0 - math.exp(-seconds / REVEAL_TAU))
    return min(float(backlog), max(eased, REVEAL_MIN_RATE * seconds))


def align_shown(shown: str, target: str) -> tuple[int, bool]:
    """Where the words already shown end in target, whatever the spacing between them.

    A finished reply can join its parts with its own spacing, and it gains a
    job caption and a team summary. Returns (offset just past the last
    matched character, whether every shown word was found).
    """
    if target.startswith(shown):
        return len(shown), True
    position = 0
    matched = 0
    for char in shown:
        if char.isspace():
            continue
        while position < len(target) and target[position].isspace():
            position += 1
        if position >= len(target) or target[position] != char:
            return matched, False
        position += 1
        matched = position
    return matched, True


def _is_fence(line: str) -> bool:
    return line.strip().startswith("```")


def stable_boundary(text: str, limit: int | None = None) -> int:
    """The offset where the settled part of a reply ends and its growing part begins.

    The boundary is just past the last blank line that is outside a fenced
    code block and at or before limit. Text before it renders the same alone
    as it does with the rest attached, so the thread draws it once and only
    redraws what follows. 0 when the reply has no such break yet.
    """
    limit = len(text) if limit is None else max(0, min(limit, len(text)))
    boundary = 0
    in_fence = False
    position = 0
    for line in text.split("\n"):
        end = position + len(line)
        if position > limit:
            break
        if _is_fence(line):
            in_fence = not in_fence
        elif not in_fence and line.strip() == "" and position > 0 and end + 1 <= limit:
            # The break is usable once the line after it has begun.
            boundary = end + 1
        position = end + 1
    return min(boundary, limit)


def settle_inline(text: str) -> str:
    """The growing part of a reply with a half-written bold or code span closed.

    While words are still arriving, "the **double-interl" would show two
    asterisks and then jump to bold when the closing pair lands. Closing the
    span for the moment draws the words as they will end up. A marker with
    nothing after it yet is held back instead. Text inside an open code
    fence is left alone, and so is a finished reply: the caller only passes
    text that is still flowing.
    """
    if not text:
        return text
    lines = text.split("\n")
    if sum(1 for line in lines if _is_fence(line)) % 2:
        return text
    last = lines[-1]
    # One asterisk at the end is the first half of a pair that has not arrived.
    trailing = len(last) - len(last.rstrip("*"))
    if trailing % 2:
        last = last[:-1]
    if last.count("**") % 2:
        last = last[:-2] if last.endswith("**") else last + "**"
    if last.count("`") % 2:
        last = last[:-1] if last.endswith("`") else last + "`"
    return "\n".join(lines[:-1] + [last])


class Reveal:
    """One reply as it comes onto the screen.

    target is the text so far; shown is how much of it is on screen. feed()
    takes a longer or corrected target, advance() moves shown forward for one
    frame, and fades() says which of the newest characters are still fading in.
    """

    def __init__(self, target: str = "", *, shown: int | None = None):
        self.target = target
        self.shown = len(target) if shown is None else max(0, min(shown, len(target)))
        self._carry = 0.0
        self._last: float | None = None
        # (when, shown before the frame, shown after it), oldest first.
        self._marks: deque[tuple[float, int, int]] = deque()

    @property
    def text(self) -> str:
        """The part of the target on screen now."""
        return self.target[:self.shown]

    @property
    def flowing(self) -> bool:
        """Text is still waiting to be shown."""
        return self.shown < len(self.target)

    def fading(self, now: float) -> bool:
        """Some shown text is still fading in."""
        self._expire(now)
        return bool(self._marks)

    def active(self, now: float) -> bool:
        return self.flowing or self.fading(now)

    def feed(self, target: str) -> None:
        """Take a new target. Words already shown stay shown where the new text keeps them."""
        if target == self.target:
            return
        if target.startswith(self.target[:self.shown]):
            self.target = target
            return
        at, _whole = align_shown(self.target[:self.shown], target)
        self.target = target
        self.shown = at
        self._marks = deque(mark for mark in self._marks if mark[2] <= at)

    def finish(self) -> None:
        """Show everything now, with nothing left fading."""
        self.shown = len(self.target)
        self._marks.clear()
        self._carry = 0.0

    def advance(self, now: float) -> bool:
        """Reveal one frame's worth. now is in seconds. Returns True when shown moved."""
        backlog = len(self.target) - self.shown
        if backlog <= 0:
            self._last = None
            self._carry = 0.0
            return False
        # The first frame after a pause counts as one frame, not as the whole pause.
        dt = 1.0 / 60.0 if self._last is None else min(max(now - self._last, 0.0), MAX_FRAME_SECONDS)
        self._last = now
        self._carry += reveal_step(backlog, dt)
        take = min(backlog, int(self._carry))
        if take <= 0:
            return False
        self._carry -= take
        before = self.shown
        self.shown = before + take
        self._marks.append((now, before, self.shown))
        return True

    def _expire(self, now: float) -> None:
        horizon = now - FADE_MS / 1000.0
        while self._marks and self._marks[0][0] <= horizon:
            self._marks.popleft()

    def settled(self, now: float) -> int:
        """The offset before which nothing is fading any more."""
        self._expire(now)
        return self._marks[0][1] if self._marks else self.shown

    def fades(self, now: float, steps: int) -> list[tuple[int, int]]:
        """(characters back from the end of the shown text, fade step), newest first.

        Step 0 is the faintest. A character more than the last distance back
        has finished fading. The thread applies these from the end of what it
        drew, which is exact where the newest text has no markdown markers.
        """
        self._expire(now)
        out: list[tuple[int, int]] = []
        for when, before, _after in reversed(self._marks):
            age = (now - when) * 1000.0
            step = max(0, min(steps - 1, int(age / FADE_MS * steps)))
            distance = self.shown - before
            if out and out[-1][1] == step:
                out[-1] = (distance, step)
            else:
                out.append((distance, step))
        return out
