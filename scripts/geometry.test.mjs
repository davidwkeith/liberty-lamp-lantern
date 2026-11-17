// Geometry checks that render the real model with OpenSCAD.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseStl, analyze, overhangArea } from './check-stl.mjs';

const OPENSCAD = process.env.OPENSCAD ?? 'openscad';
const SRC = fileURLToPath(new URL('../src/lantern.scad', import.meta.url));
const CONTACT = fileURLToPath(new URL('./fixtures/roof-contact.scad', import.meta.url));
const dir = mkdtempSync(join(tmpdir(), 'lantern-'));

/** Render `file` with -D overrides; returns { ok, stderr, tris }. */
function render(file, defs = {}, name = 'out') {
  const out = join(dir, `${name}.stl`);
  const args = ['-o', out, '--export-format', 'binstl'];
  for (const [k, v] of Object.entries(defs)) args.push('-D', `${k}=${JSON.stringify(v)}`);
  const r = spawnSync(OPENSCAD, [...args, file], { encoding: 'utf8' });
  const ok = r.status === 0 && existsSync(out);
  return { ok, stderr: r.stderr, tris: ok ? parseStl(readFileSync(out)).triangles : [] };
}

test('default parameters satisfy every assert', () => {
  const r = render(SRC, { part: 'body' }, 'default');
  assert.ok(r.ok, r.stderr);
});

for (const [defs, msg] of [
  [{ led_h: 16 }, /led_h/],
  [{ panel_thickness: 6 }, /web/],
  [{ insert_depth: 5 }, /screw/],
]) {
  test(`rejects ${JSON.stringify(defs)}`, () => {
    const r = render(SRC, { part: 'body', ...defs }, 'bad');
    assert.equal(r.ok, false);
    assert.match(r.stderr, msg);
  });
}

for (const corner of [0, 1, 2, 3]) {
  test(`roof bears on standoff ${corner}`, () => {
    const r = render(CONTACT, { corner }, `contact${corner}`);
    assert.ok(r.ok, r.stderr);
    assert.ok(analyze(r.tris).count > 0, 'roof does not touch this standoff');
  });
}

test('body prints without supports (no raised down-facing area)', () => {
  const r = render(SRC, { part: 'body' }, 'body');
  assert.ok(r.ok, r.stderr);
  const area = overhangArea(r.tris, 0.5);
  assert.ok(area < 100, `${Math.round(area)} mm² of unsupported overhang`);
});
