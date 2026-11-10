/**
 * How a reply's words come onto the page: the pacing rules of Spec Surgeon's
 * frontend/src/lib/reveal.ts, so the practice's apps move alike.
 *
 * Words arrive in network bursts, and a tool-plan reply arrives all at once.
 * The page shows them at a reading pace instead: each animation frame reveals
 * part of the backlog (revealStep), every revealed piece fades in, and a
 * finished reply carries on from the words already shown (alignShown) instead
 * of replacing them.
 *
 * Pure, so `node --test` pins every rule.
 */

/** How long a revealed piece takes to fade in (ms); `.fresh` in styles.css runs the same length. */
export const FADE_MS = 520;
/** The backlog drains with this time constant (s): a burst of 800 characters shows in about a second. */
export const REVEAL_TAU = 0.3;
/** The slowest pace (characters a second), so the last words of a burst never trickle. */
export const REVEAL_MIN_RATE = 150;
/** A frame after a pause counts as at most this long (s), so a stalled page does not dump its backlog. */
export const MAX_FRAME_SECONDS = 0.25;

/** Characters to reveal in a frame `dt` seconds long with `backlog` characters waiting. A fraction:
 *  the caller carries what is left into the next frame, so the pace is the same at any frame rate. */
export function revealStep(backlog: number, dt: number): number {
  if (backlog <= 0) return 0;
  const seconds = Math.max(dt, 0);
  const eased = backlog * (1 - Math.exp(-seconds / REVEAL_TAU));
  return Math.min(backlog, Math.max(eased, REVEAL_MIN_RATE * seconds));
}

/** `end`, moved past a surrogate pair it would split. */
export function safeCut(text: string, end: number): number {
  if (end <= 0 || end >= text.length) return Math.max(0, Math.min(end, text.length));
  const code = text.charCodeAt(end - 1);
  return code >= 0xd800 && code < 0xdc00 ? end + 1 : end;
}

const isSpace = (ch: string) => ch === " " || ch === "\n" || ch === "\t" || ch === "\r" || ch === "\f" || ch === "\v";

/**
 * Where the words already shown end in `target`, whatever the spacing between
 * them: a finished reply joins its parts with its own spacing, and gains its
 * team summary. `at` is the offset just past the last matched character;
 * `whole` says whether every shown word was found.
 */
export function alignShown(shown: string, target: string): { at: number; whole: boolean } {
  if (target.startsWith(shown)) return { at: shown.length, whole: true };
  let j = 0;
  let at = 0;
  for (let i = 0; i < shown.length; i += 1) {
    const ch = shown[i];
    if (isSpace(ch)) continue;
    while (j < target.length && isSpace(target[j])) j += 1;
    if (j >= target.length || target[j] !== ch) return { at, whole: false };
    j += 1;
    at = j;
  }
  return { at, whole: true };
}

/**
 * One reply as it comes onto the page. `target` is the text so far, `shown`
 * how much of it is on the page. feed() takes a longer or corrected target,
 * advance() moves one frame, fresh() says where the pieces still fading begin.
 */
export class Reveal {
  target: string;
  shown: number;
  private carry = 0;
  private last = 0;
  /** Where each piece still fading begins, and when it was revealed (ms), oldest first. */
  marks: number[] = [];
  times: number[] = [];

  constructor(target = "", shown?: number) {
    this.target = target;
    this.shown = shown === undefined ? target.length : Math.max(0, Math.min(shown, target.length));
  }

  get text(): string {
    return this.target.slice(0, this.shown);
  }

  get flowing(): boolean {
    return this.shown < this.target.length;
  }

  /** Take a new target. Words already shown stay shown where the new text keeps them. */
  feed(target: string): void {
    if (target === this.target) return;
    const shownText = this.target.slice(0, this.shown);
    if (target.startsWith(shownText)) {
      this.target = target;
      return;
    }
    const { at } = alignShown(shownText, target);
    this.target = target;
    this.shown = at;
    let keep = this.marks.length;
    while (keep > 0 && this.marks[keep - 1] >= at) keep -= 1;
    this.marks.length = keep;
    this.times.length = keep;
  }

  /** Show everything now, with nothing left fading. */
  finish(): void {
    this.shown = this.target.length;
    this.marks = [];
    this.times = [];
    this.carry = 0;
    this.last = 0;
  }

  /** Reveal one frame's worth. now is performance.now(). Returns true when `shown` moved. */
  advance(now: number): boolean {
    this.expire(now);
    const backlog = this.target.length - this.shown;
    if (backlog <= 0) {
      this.last = 0;
      this.carry = 0;
      return false;
    }
    const dt = this.last ? Math.min((now - this.last) / 1000, MAX_FRAME_SECONDS) : 1 / 60;
    this.last = now;
    this.carry += revealStep(backlog, dt);
    const take = Math.floor(this.carry);
    if (take <= 0) return false;
    this.carry -= take;
    this.marks.push(this.shown);
    this.times.push(now);
    this.shown = safeCut(this.target, this.shown + take);
    return true;
  }

  /** Forget the pieces that finished fading. */
  expire(now: number): void {
    let drop = 0;
    while (drop < this.times.length && now - this.times[drop] >= FADE_MS) drop += 1;
    if (drop) {
      this.marks.splice(0, drop);
      this.times.splice(0, drop);
    }
  }

  /** Some text is still waiting or still fading. */
  active(now: number): boolean {
    this.expire(now);
    return this.flowing || this.marks.length > 0;
  }
}
