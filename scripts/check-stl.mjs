#!/usr/bin/env node
// Validate exported STLs: non-empty, watertight (every edge shared by exactly
// two triangles), and within the printer bed on every axis.
// Usage: node scripts/check-stl.mjs [--bed <mm>] <file.stl...>

import { readFileSync, realpathSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

/** Parse binary or ASCII STL into { triangles: [[x,y,z],[x,y,z],[x,y,z]][] }. */
export function parseStl(buf) {
  if (buf.length >= 84) {
    const n = buf.readUInt32LE(80);
    if (84 + 50 * n === buf.length) {
      const triangles = [];
      for (let i = 0; i < n; i++) {
        const o = 84 + i * 50 + 12; // skip normal
        const f = (k) => buf.readFloatLE(o + k * 4);
        triangles.push([[f(0), f(1), f(2)], [f(3), f(4), f(5)], [f(6), f(7), f(8)]]);
      }
      return { triangles };
    }
  }
  const verts = [...buf.toString('utf8').matchAll(/vertex\s+(\S+)\s+(\S+)\s+(\S+)/g)].map((m) =>
    m.slice(1, 4).map(Number),
  );
  const triangles = [];
  for (let i = 0; i + 2 < verts.length; i += 3) triangles.push(verts.slice(i, i + 3));
  return { triangles };
}

/** Triangle count, bounding-box size, and count of edges not shared by exactly 2 triangles. */
export function analyze(triangles) {
  const min = [Infinity, Infinity, Infinity];
  const max = [-Infinity, -Infinity, -Infinity];
  const key = (p) => p.map((n) => Math.round(n * 1e4)).join(',');
  const edges = new Map();
  for (const tri of triangles) {
    for (const p of tri) {
      for (let a = 0; a < 3; a++) {
        min[a] = Math.min(min[a], p[a]);
        max[a] = Math.max(max[a], p[a]);
      }
    }
    const ks = tri.map(key);
    for (let i = 0; i < 3; i++) {
      const e = [ks[i], ks[(i + 1) % 3]].sort().join('|');
      edges.set(e, (edges.get(e) ?? 0) + 1);
    }
  }
  let nonManifoldEdges = 0;
  for (const c of edges.values()) if (c !== 2) nonManifoldEdges++;
  const count = triangles.length;
  const size = count ? max.map((v, a) => Math.round((v - min[a]) * 100) / 100) : [0, 0, 0];
  return { count, size, nonManifoldEdges };
}

/**
 * Area (mm²) of facets that face down steeper than ~48° and sit entirely above
 * `minZ` — i.e. surfaces a slicer would need supports or a long bridge for.
 */
export function overhangArea(triangles, minZ = 0.5) {
  let area = 0;
  for (const [a, b, c] of triangles) {
    if (Math.min(a[2], b[2], c[2]) <= minZ) continue;
    const u = b.map((v, i) => v - a[i]);
    const w = c.map((v, i) => v - a[i]);
    const n = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]];
    const len = Math.hypot(...n);
    if (len && n[2] / len < -0.75) area += len / 2;
  }
  return area;
}

function main(argv) {
  let bed = 250;
  const files = [];
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--bed') bed = Number(argv[++i]);
    else files.push(argv[i]);
  }
  if (!Number.isFinite(bed) || bed <= 0) {
    console.error(`--bed must be a positive number of mm (got "${argv[argv.indexOf('--bed') + 1]}")`);
    return 2;
  }
  if (!files.length) {
    console.error('usage: check-stl.mjs [--bed <mm>] <file.stl...>');
    return 2;
  }
  let failed = false;
  for (const file of files) {
    const errors = [];
    let r = { count: 0, size: [0, 0, 0], nonManifoldEdges: 0 };
    try {
      r = analyze(parseStl(readFileSync(file)).triangles);
      if (!r.count) errors.push('empty (no triangles)');
      if (r.nonManifoldEdges) errors.push(`${r.nonManifoldEdges} non-manifold edges`);
      if (r.size.some((s) => s > bed)) errors.push(`exceeds bed ${bed} mm`);
    } catch (e) {
      errors.push(`unreadable: ${e.message}`);
    }
    const dims = r.size.join(' × ');
    if (errors.length) {
      failed = true;
      console.error(`FAIL ${file}: ${errors.join('; ')} (${dims} mm, ${r.count} tris)`);
    } else {
      console.log(`OK   ${file}: ${dims} mm, ${r.count} tris`);
    }
  }
  return failed ? 1 : 0;
}

const isMain = () => {
  try {
    return realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url));
  } catch {
    return false;
  }
};
if (isMain()) process.exitCode = main(process.argv.slice(2));
