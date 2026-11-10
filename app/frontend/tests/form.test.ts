// The Zone details form on its way to the app (src/form.ts).
import { test } from "node:test";
import assert from "node:assert/strict";
import { PatchQueue, mergeForm } from "../src/form.ts";

function fakeTimer() {
  const pending = new Map<number, () => void>();
  let next = 1;
  return {
    timer: {
      set: (fn: () => void) => {
        const id = next++;
        pending.set(id, fn);
        return id;
      },
      clear: (handle: unknown) => {
        pending.delete(handle as number);
      },
    },
    fire() {
      const all = [...pending.values()];
      pending.clear();
      all.forEach((fn) => fn());
    },
    get count() {
      return pending.size;
    },
  };
}

test("typing waits for a pause, and the latest value of a field wins", async () => {
  const sent: Record<string, unknown>[] = [];
  const clock = fakeTimer();
  const queue = new PatchQueue(async (values) => void sent.push(values), clock.timer);
  queue.set("density", "0.2");
  queue.set("density", "0.25");
  queue.set("zone_id", "DH-1");
  assert.equal(clock.count, 1, "one timer, restarted by each key");
  assert.deepEqual(sent, []);
  clock.fire();
  await queue.flush();
  assert.deepEqual(sent, [{ density: "0.25", zone_id: "DH-1" }]);
  assert.equal(queue.dirty, false);
});

test("an action flushes first, and patches arrive in the order they were made", async () => {
  const order: string[] = [];
  let release!: () => void;
  const slow = new Promise<void>((resolve) => (release = resolve));
  const clock = fakeTimer();
  let first = true;
  const queue = new PatchQueue(async (values) => {
    if (first) {
      first = false;
      await slow;
    }
    order.push(JSON.stringify(values));
  }, clock.timer);
  queue.set("ahj", "City");
  const one = queue.flush();
  queue.set("ahj", "County");
  const two = queue.flush();
  release();
  await Promise.all([one, two]);
  assert.deepEqual(order, ['{"ahj":"City"}', '{"ahj":"County"}']);
  assert.equal(clock.count, 0, "a flush clears the waiting timer");
});

test("a failed patch does not stop the next one", async () => {
  const sent: string[] = [];
  const queue = new PatchQueue(async (values) => {
    if ("bad" in values) throw new Error("refused");
    sent.push(Object.keys(values).join());
  }, fakeTimer().timer);
  queue.set("bad", "x");
  await queue.flush();
  queue.set("good", "y");
  await queue.flush();
  assert.deepEqual(sent, ["good"]);
});

test("a form the app changed keeps the fields still being typed", () => {
  const server = { zone_id: "DH-2", density: "0.2", qod: true };
  const local = { zone_id: "DH-1", density: "0.3", qod: false };
  assert.deepEqual(mergeForm(server, local, ["density"]), { zone_id: "DH-2", density: "0.3", qod: true });
  assert.deepEqual(mergeForm(server, local, []), server);
});
