// The window's layout arithmetic (src/layout.ts): the panel's width beside the thread.
import { test } from "node:test";
import assert from "node:assert/strict";
import { PANEL_MIN, PANEL_OWN_MAX, PANEL_STEP, THREAD_MIN, choiceLabel, panelMax, panelOwn, panelWidth, readLayout, widthAfterKey } from "../src/layout.ts";

test("the panel's own width is a little under half the stage and never past its cap", () => {
  assert.equal(panelOwn(1200), 528);
  assert.equal(panelOwn(1672), PANEL_OWN_MAX);
  assert.equal(panelOwn(3000), PANEL_OWN_MAX);
});

test("a narrow stage still gives the panel its least width", () => {
  assert.equal(panelOwn(772), PANEL_MIN);
  assert.equal(panelOwn(500), PANEL_MIN);
  assert.equal(panelMax(500), PANEL_MIN);
});

test("a width the designer set is held to what the stage can give", () => {
  assert.equal(panelWidth(600, 1400), 600);
  assert.equal(panelWidth(5000, 1400), 1400 - THREAD_MIN);
  assert.equal(panelWidth(100, 1400), PANEL_MIN);
  assert.equal(panelWidth(0, 1400), panelOwn(1400));
});

test("before the stage is measured the width is what was asked, or the least", () => {
  assert.equal(panelWidth(640, 0), 640);
  assert.equal(panelWidth(0, 0), PANEL_MIN);
});

test("the keys on the panel's edge", () => {
  assert.equal(widthAfterKey("ArrowLeft", 500, 1400), 500 + PANEL_STEP);
  assert.equal(widthAfterKey("ArrowRight", 500, 1400), 500 - PANEL_STEP);
  assert.equal(widthAfterKey("ArrowRight", PANEL_MIN, 1400), PANEL_MIN);
  assert.equal(widthAfterKey("ArrowLeft", 1400 - THREAD_MIN, 1400), 1400 - THREAD_MIN);
  assert.equal(widthAfterKey("Home", 500, 1400), 1400 - THREAD_MIN);
  assert.equal(widthAfterKey("End", 500, 1400), PANEL_MIN);
  assert.equal(widthAfterKey("Enter", 500, 1400), 0);
  assert.equal(widthAfterKey("a", 500, 1400), null);
});

test("a stored layout is read as one, and nonsense falls back", () => {
  assert.deepEqual(readLayout({ sidebar: false, panel: "team", panel_width: 612.4 }), { sidebar: false, panel: "team", panel_width: 612 });
  assert.deepEqual(readLayout({ panel: "drawer", panel_width: -4 }), { sidebar: true, panel: "", panel_width: 0 });
  assert.deepEqual(readLayout(null), { sidebar: true, panel: "", panel_width: 0 });
});

test("a choice reads as words and keeps its value", () => {
  assert.equal(choiceLabel("nc_solenoid"), "NC solenoid");
  assert.equal(choiceLabel("pneumatic_actuator"), "Pneumatic actuator");
  assert.equal(choiceLabel("nitrogen"), "Nitrogen");
  assert.equal(choiceLabel("NFPA-OH"), "NFPA-OH");
  assert.equal(choiceLabel("Center to center"), "Center to center");
});
