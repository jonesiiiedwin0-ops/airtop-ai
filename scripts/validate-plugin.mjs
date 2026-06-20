#!/usr/bin/env node

import { existsSync, readFileSync, statSync } from "node:fs";
import path from "node:path";

const pluginDir = path.resolve(process.argv[2] ?? "plugins/winston-ai");
const manifestPath = path.join(pluginDir, ".cursor-plugin", "plugin.json");
const pluginNamePattern = /^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/;
const frontmatterPattern = /^---\n[\s\S]*?\n---\n/;

function fail(message) {
  console.error(`ERROR: ${message}`);
  process.exitCode = 1;
}

function readJson(filePath) {
  try {
    return JSON.parse(readFileSync(filePath, "utf8"));
  } catch (error) {
    fail(`Could not parse JSON at ${filePath}: ${error.message}`);
    return {};
  }
}

function isSafeRelativePath(relativePath) {
  return (
    typeof relativePath === "string" &&
    relativePath.length > 0 &&
    !path.isAbsolute(relativePath) &&
    !relativePath.split(/[\\/]+/).includes("..")
  );
}

function validateFrontmatter(filePath, requiredKeys) {
  const content = readFileSync(filePath, "utf8");
  const match = content.match(frontmatterPattern);

  if (!match) {
    fail(`${filePath} is missing YAML frontmatter`);
    return;
  }

  for (const key of requiredKeys) {
    const keyPattern = new RegExp(`^${key}:\\s*.+$`, "m");
    if (!keyPattern.test(match[0])) {
      fail(`${filePath} frontmatter is missing required key: ${key}`);
    }
  }
}

function validateComponentGroup(manifest, groupName, requiredKeys) {
  const components = manifest[groupName] ?? [];

  if (!Array.isArray(components)) {
    fail(`Manifest field "${groupName}" must be an array`);
    return;
  }

  for (const component of components) {
    const relativePath = component?.path;

    if (!isSafeRelativePath(relativePath)) {
      fail(`Manifest field "${groupName}" contains unsafe path: ${relativePath}`);
      continue;
    }

    const absolutePath = path.join(pluginDir, relativePath);
    if (!existsSync(absolutePath)) {
      fail(`Manifest path does not exist: ${relativePath}`);
      continue;
    }

    if (!statSync(absolutePath).isFile()) {
      fail(`Manifest path is not a file: ${relativePath}`);
      continue;
    }

    validateFrontmatter(absolutePath, requiredKeys);
  }
}

if (!existsSync(pluginDir)) {
  fail(`Plugin directory does not exist: ${pluginDir}`);
} else if (!existsSync(manifestPath)) {
  fail(`Manifest does not exist: ${manifestPath}`);
} else {
  const manifest = readJson(manifestPath);

  if (!pluginNamePattern.test(manifest.name ?? "")) {
    fail(`Manifest name must be lowercase kebab-case compatible: ${manifest.name}`);
  }

  validateComponentGroup(manifest, "rules", ["description"]);
  validateComponentGroup(manifest, "skills", ["name", "description"]);
  validateComponentGroup(manifest, "commands", ["name", "description"]);
  validateComponentGroup(manifest, "agents", ["name", "description"]);
}

if (process.exitCode) {
  console.error("Plugin validation failed.");
} else {
  console.log(`Plugin validation passed: ${pluginDir}`);
}
