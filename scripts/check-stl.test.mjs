import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseStl, analyze, overhangArea } from './check-stl.mjs';

const CLI = fileURLToPath(new URL('./check-stl.mjs', import.meta.url));

/** 12 triangles of an axis-aligned cube of side `s`. */
function cubeTris(s = 1) {
  const v = (x, y, z) => [x * s, y * s, z * s];
  const quads = [
    [v(0, 0, 0), v(0, 1, 0), v(1, 1, 0), v(1, 0, 0)], // bottom
    [v(0, 0, 1), v(1, 0, 1), v(1, 1, 1), v(0, 1, 1)], // top
    [v(0, 0, 0), v(1, 0, 0), v(1, 0, 1), v(0, 0, 1)], // front
    [v(0, 1, 0), v(0, 1, 1), v(1, 1, 1), v(1, 1, 0)], // back
    [v(0, 0, 0), v(0, 0, 1), v(0, 1, 1), v(0, 1, 0)], // left
    [v(1, 0, 0), v(1, 1, 0), v(1, 1, 1), v(1, 0, 1)], // right
  ];
  return quads.flatMap(([a, b, c, d]) => [[a, b, c], [a, c, d]]);
}

function toAscii(tris) {
  const facets = tris
    .map((t) => `facet normal 0 0 0\nouter loop\n${t.map((p) => `vertex ${p.join(' ')}`).join('\n')}\nendloop\nendfacet`)
    .join('\n');
  return Buffer.from(`solid t\n${facets}\nendsolid t\n`);
}

function toBinary(tris) {
  const buf = Buffer.alloc(84 + 50 * tris.length);
  buf.writeUInt32LE(tris.length, 80);
  tris.forEach((t, i) => {
    const o = 84 + i * 50 + 12;
    t.flat().forEach((n, j) => buf.writeFloatLE(n, o + j * 4));
  });
  return buf;
}

function tmpFile(name, buf) {
  const p = join(mkdtempSync(join(tmpdir(), 'stl-')), name);
  writeFileSync(p, buf);
  return p;
}

function runCli(args) {
  try {
    execFileSync(process.execPath, [CLI, ...args], { stdio: 'pipe' });
    return { code: 0, stderr: '' };
  } catch (e) {
    return { code: e.status, stderr: String(e.stderr) };
  }
}

test('parses ascii cube', () => {
  const r = analyze(parseStl(toAscii(cubeTris())).triangles);
  assert.equal(r.count, 12);
  assert.deepEqual(r.size, [1, 1, 1]);
  assert.equal(r.nonManifoldEdges, 0);
});

test('parses binary cube', () => {
  const r = analyze(parseStl(toBinary(cubeTris())).triangles);
  assert.equal(r.count, 12);
  assert.deepEqual(r.size, [1, 1, 1]);
  assert.equal(r.nonManifoldEdges, 0);
});

test('flags non-manifold', () => {
  const r = analyze(parseStl(toAscii(cubeTris().slice(1))).triangles);
  assert.ok(r.nonManifoldEdges > 0);
});

test('flags oversize', () => {
  const r = runCli(['--bed', '250', tmpFile('big.stl', toBinary(cubeTris(300)))]);
  assert.equal(r.code, 1);
  assert.match(r.stderr, /exceeds bed/);
});

test('flags empty', () => {
  const r = runCli(['--bed', '250', tmpFile('empty.stl', Buffer.alloc(0))]);
  assert.equal(r.code, 1);
  assert.match(r.stderr, /empty/);
});

test('passes a valid part', () => {
  const r = runCli(['--bed', '250', tmpFile('ok.stl', toBinary(cubeTris(100)))]);
  assert.equal(r.code, 0);
});

test('runs when invoked through a symlink', async () => {
  const { symlinkSync } = await import('node:fs');
  const link = join(mkdtempSync(join(tmpdir(), 'stl-')), 'check-stl.mjs');
  symlinkSync(CLI, link);
  let code = 0;
  try {
    execFileSync(process.execPath, [link, '/nonexistent.stl'], { stdio: 'pipe' });
  } catch (e) {
    code = e.status;
  }
  assert.equal(code, 1);
});

test('rejects a non-numeric --bed', () => {
  const r = runCli(['--bed', tmpFile('ok.stl', toBinary(cubeTris(100)))]);
  assert.notEqual(r.code, 0);
  assert.match(r.stderr, /--bed/);
});

test('overhangArea counts only raised down-facing area', () => {
  const lifted = cubeTris(10).map((t) => t.map(([x, y, z]) => [x, y, z + 5]));
  assert.equal(overhangArea(cubeTris(10), 0.5), 0); // bottom sits on the bed
  assert.equal(Math.round(overhangArea(lifted, 0.5)), 100);
});
