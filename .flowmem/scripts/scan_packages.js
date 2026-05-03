#!/usr/bin/env node
/**
 * FlowMem — scan_packages.js
 * Reads package.json and outputs dependency tree as JSON.
 * Used to generate flowchart TB (npm dependency graph).
 *
 * Usage:
 *   node scan_packages.js [root_dir]
 *   node scan_packages.js > .flowmem/.cache/packages.json
 */
const fs = require("fs");
const path = require("path");

function getRoot(argv) {
  if (argv[2]) return path.resolve(argv[2]);
  let dir = __dirname;
  while (dir !== path.dirname(dir)) {
    if (fs.existsSync(path.join(dir, "package.json"))) return dir;
    dir = path.dirname(dir);
  }
  return process.cwd();
}

function readPackage(pkgPath) {
  try {
    return JSON.parse(fs.readFileSync(pkgPath, "utf8"));
  } catch {
    return null;
  }
}

function collectWorkspaces(root) {
  const main = readPackage(path.join(root, "package.json"));
  if (!main) return [];
  const packages = [{ path: root, pkg: main }];

  const wsPatterns = main.workspaces || [];
  const patterns = Array.isArray(wsPatterns) ? wsPatterns : wsPatterns.packages || [];

  for (const pattern of patterns) {
    const base = pattern.replace(/\*.*/, "");
    const absBase = path.join(root, base);
    if (fs.existsSync(absBase)) {
      for (const entry of fs.readdirSync(absBase)) {
        const pkgPath = path.join(absBase, entry, "package.json");
        if (fs.existsSync(pkgPath)) {
          const pkg = readPackage(pkgPath);
          if (pkg) packages.push({ path: path.join(absBase, entry), pkg });
        }
      }
    }
  }
  return packages;
}

function buildGraph(packages) {
  const nodes = packages.map((p) => ({
    name: p.pkg.name || path.basename(p.path),
    version: p.pkg.version || "?",
    path: p.path,
    deps: Object.keys(p.pkg.dependencies || {}),
    devDeps: Object.keys(p.pkg.devDependencies || {}),
    peerDeps: Object.keys(p.pkg.peerDependencies || {}),
  }));

  const nodeNames = new Set(nodes.map((n) => n.name));
  const edges = [];

  for (const node of nodes) {
    for (const dep of node.deps) {
      edges.push({ from: node.name, to: dep, type: "prod" });
    }
    for (const dep of node.devDeps) {
      edges.push({ from: node.name, to: dep, type: "dev" });
    }
  }

  // Filter to only internal deps for graph clarity
  const internalEdges = edges.filter((e) => nodeNames.has(e.to));
  const externalDeps = [...new Set(edges.filter((e) => !nodeNames.has(e.to)).map((e) => e.to))];

  return { nodes, internalEdges, externalDeps: externalDeps.slice(0, 30) };
}

const root = getRoot(process.argv);
const packages = collectWorkspaces(root);
const graph = buildGraph(packages);

console.log(JSON.stringify({ root, ...graph }, null, 2));
