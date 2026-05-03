#!/usr/bin/env node
/**
 * FlowMem — scan_ts_exports.js
 * Extracts TypeScript interfaces, types, classes, and exports via regex parsing.
 * (Does not require a full TS compiler — works on any .ts/.tsx project)
 * Used to generate classDiagram for TypeScript projects.
 *
 * Usage:
 *   node scan_ts_exports.js [root_dir]
 *   node scan_ts_exports.js > .flowmem/.cache/ts_exports.json
 */
const fs = require("fs");
const path = require("path");

const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build", ".next", "out", ".flowmem"]);

function getRoot(argv) {
  if (argv[2]) return path.resolve(argv[2]);
  let dir = __dirname;
  while (dir !== path.dirname(dir)) {
    if (fs.existsSync(path.join(dir, "package.json"))) return dir;
    dir = path.dirname(dir);
  }
  return process.cwd();
}

function walkDir(dir, exts, results = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (SKIP_DIRS.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walkDir(full, exts, results);
    else if (exts.some((e) => entry.name.endsWith(e))) results.push(full);
  }
  return results;
}

const INTERFACE_RE = /export\s+(?:default\s+)?interface\s+(\w+)(?:\s+extends\s+([^{]+))?/g;
const CLASS_RE = /export\s+(?:default\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?/g;
const TYPE_RE = /export\s+type\s+(\w+)\s*=/g;
const ENUM_RE = /export\s+enum\s+(\w+)/g;
const METHOD_RE = /^\s{2,4}(?:public\s+|private\s+|protected\s+|readonly\s+|static\s+|async\s+)*(\w+)\s*(?:<[^>]*>)?\s*\(([^)]*)\)/gm;

function parseFile(filepath, root) {
  const rel = path.relative(root, filepath);
  let source;
  try { source = fs.readFileSync(filepath, "utf8"); }
  catch { return null; }

  const interfaces = [], classes = [], types = [], enums = [];

  for (const m of source.matchAll(INTERFACE_RE)) {
    interfaces.push({ name: m[1], extends: m[2]?.trim().split(",").map((s) => s.trim()).filter(Boolean) || [] });
  }
  for (const m of source.matchAll(CLASS_RE)) {
    const methods = [];
    for (const mm of source.matchAll(METHOD_RE)) {
      if (mm[1] !== "constructor") methods.push({ name: mm[1], params: mm[2].split(",").map((p) => p.trim().split(":")[0].trim()).filter(Boolean) });
    }
    classes.push({
      name: m[1],
      extends: m[2] || null,
      implements: m[3]?.trim().split(",").map((s) => s.trim()).filter(Boolean) || [],
      methods: methods.slice(0, 10),
    });
  }
  for (const m of source.matchAll(TYPE_RE)) types.push(m[1]);
  for (const m of source.matchAll(ENUM_RE)) enums.push(m[1]);

  if (!interfaces.length && !classes.length && !types.length && !enums.length) return null;
  return { file: rel, interfaces, classes, types, enums };
}

const root = getRoot(process.argv);
const files = walkDir(root, [".ts", ".tsx"]);
const results = files.map((f) => parseFile(f, root)).filter(Boolean);

const allClasses = results.flatMap((r) => r.classes);
const allInterfaces = results.flatMap((r) => r.interfaces);
const allTypes = results.flatMap((r) => r.types);

console.log(JSON.stringify({ root, files: results, allClasses, allInterfaces, allTypes }, null, 2));
