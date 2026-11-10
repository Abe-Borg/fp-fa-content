/**
 * The Zone details form travels to the app as the designer types: each change
 * joins a patch that is sent after a short pause, and every action flushes the
 * patch first, so a run, a send, or a switch to another job always reads the
 * form as it is on screen. Pure (the sender and the clock are passed in), so
 * `node --test` pins the order.
 */
import type { FormValues } from "./types";

export const PATCH_DELAY_MS = 250;

type Send = (values: FormValues) => Promise<void>;
type Timer = { set: (fn: () => void, ms: number) => unknown; clear: (handle: unknown) => void };

const realTimer: Timer = {
  set: (fn, ms) => setTimeout(fn, ms),
  clear: (handle) => clearTimeout(handle as ReturnType<typeof setTimeout>),
};

export class PatchQueue {
  private pending: FormValues = {};
  private handle: unknown = null;
  private inFlight: Promise<void> = Promise.resolve();
  private send: Send;
  private timer: Timer;
  private delay: number;

  constructor(send: Send, timer: Timer = realTimer, delay = PATCH_DELAY_MS) {
    this.send = send;
    this.timer = timer;
    this.delay = delay;
  }

  /** A field the designer changed. The latest value of a field wins. */
  set(name: string, value: string | boolean): void {
    this.pending[name] = value;
    if (this.handle !== null) this.timer.clear(this.handle);
    this.handle = this.timer.set(() => {
      this.handle = null;
      // A patch the app did not take stays waiting; the next action's flush says so.
      this.flush().catch(() => undefined);
    }, this.delay);
  }

  /** True while a change has not reached the app. */
  get dirty(): boolean {
    return Object.keys(this.pending).length > 0;
  }

  /**
   * Send what is waiting now. Resolves once every patch sent so far has reached the app, and
   * rejects when the last one did not: its values go back to waiting (unless the field was typed
   * again since), so the action that asked does not run on inputs the app never got.
   */
  flush(): Promise<void> {
    if (this.handle !== null) {
      this.timer.clear(this.handle);
      this.handle = null;
    }
    if (this.dirty) {
      const values = this.pending;
      this.pending = {};
      const previous = this.inFlight.catch(() => undefined);
      this.inFlight = previous
        .then(() => this.send(values))
        .catch((error) => {
          for (const [name, value] of Object.entries(values)) {
            if (!(name in this.pending)) this.pending[name] = value;
          }
          throw error;
        });
    }
    return this.inFlight;
  }
}

/**
 * The form the page shows: the app's form when it changed under the page (a job
 * opened, a segment added), with the fields the designer is still typing kept.
 */
export function mergeForm(server: FormValues, local: FormValues, unsent: Iterable<string>): FormValues {
  const merged: FormValues = { ...server };
  for (const name of unsent) {
    if (name in local) merged[name] = local[name];
  }
  return merged;
}
