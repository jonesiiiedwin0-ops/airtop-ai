#!/usr/bin/env node

import { access, readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const errors = [];

async function exists(relativePath) {
  try {
    await access(path.join(root, relativePath));
    return true;
  } catch {
    return false;
  }
}

async function readJson(relativePath) {
  const filePath = path.join(root, relativePath);
  try {
    return JSON.parse(await readFile(filePath, "utf8"));
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    errors.push(`${relativePath}: invalid JSON (${message})`);
    return null;
  }
}

function validateSafeRelativePath(value, owner) {
  if (typeof value !== "string" || value.length === 0) {
    errors.push(`${owner}: path must be a non-empty string`);
    return false;
  }

  if (path.posix.isAbsolute(value) || path.win32.isAbsolute(value) || value.includes("..")) {
    errors.push(`${owner}: path must stay relative and inside the plugin`);
    return false;
  }

  return true;
}

async function validateExistingPath(value, owner) {
  if (!validateSafeRelativePath(value, owner)) {
    return;
  }

  try {
    await stat(path.join(root, value));
  } catch {
    errors.push(`${owner}: declared path "${value}" does not exist`);
  }
}

function parseFrontmatter(contents, relativePath) {
  const normalizedContents = contents.replace(/\r\n/g, "\n");

  if (!normalizedContents.startsWith("---\n")) {
    errors.push(`${relativePath}: missing YAML frontmatter`);
    return new Map();
  }

  const end = normalizedContents.indexOf("\n---\n", 4);
  if (end === -1) {
    errors.push(`${relativePath}: frontmatter must close with ---`);
    return new Map();
  }

  const frontmatter = normalizedContents.slice(4, end).trim();
  const values = new Map();
  for (const line of frontmatter.split("\n")) {
    const separator = line.indexOf(":");
    if (separator === -1) {
      continue;
    }

    const key = line.slice(0, separator).trim();
    const rawValue = line.slice(separator + 1).trim();
    values.set(key, rawValue.replace(/^["']|["']$/g, ""));
  }

  return values;
}

async function validateFrontmatter(relativePath, requiredKeys) {
  const contents = await readFile(path.join(root, relativePath), "utf8");
  const values = parseFrontmatter(contents, relativePath);

  for (const key of requiredKeys) {
    if (!values.get(key)) {
      errors.push(`${relativePath}: missing frontmatter key "${key}"`);
    }
  }
}

async function collectFiles(directory) {
  const absoluteDirectory = path.join(root, directory);
  const entries = await readdir(absoluteDirectory, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const relativePath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await collectFiles(relativePath)));
      continue;
    }

    if (entry.isFile()) {
      files.push(relativePath);
    }
  }

  return files;
}

async function validateDirectoryFrontmatter(directory, extension, requiredKeys) {
  if (!(await exists(directory))) {
    return;
  }

  const files = await collectFiles(directory);
  for (const relativePath of files) {
    if (!relativePath.endsWith(extension)) {
      continue;
    }

    await validateFrontmatter(relativePath, requiredKeys);
  }
}

async function validateManifest() {
  if (!(await exists(".cursor-plugin/plugin.json"))) {
    errors.push(".cursor-plugin/plugin.json: required file is missing");
    return;
  }

  const manifest = await readJson(".cursor-plugin/plugin.json");
  if (manifest === null) {
    return;
  }

  if (
    typeof manifest.name !== "string" ||
    !/^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/.test(manifest.name)
  ) {
    errors.push(".cursor-plugin/plugin.json: name must be lowercase plugin format");
  }

  for (const field of ["rules", "skills", "agents"]) {
    if ((await exists(field)) && manifest[field] === undefined) {
      errors.push(`.cursor-plugin/plugin.json: missing declared "${field}" path`);
    }
  }

  for (const field of ["rules", "skills", "agents", "commands", "hooks", "mcpServers"]) {
    const value = manifest[field];
    if (typeof value === "string") {
      await validateExistingPath(value, `.cursor-plugin/plugin.json:${field}`);
    }
    if (Array.isArray(value)) {
      await Promise.all(
        value.map(async (entry, index) => {
          await validateExistingPath(entry, `.cursor-plugin/plugin.json:${field}[${index}]`);
        }),
      );
    }
  }
}

async function main() {
  await validateManifest();

  for (const requiredFile of ["README.md", "LICENSE"]) {
    if (!(await exists(requiredFile))) {
      errors.push(`${requiredFile}: required file is missing`);
    }
  }

  await validateDirectoryFrontmatter("rules", ".mdc", ["description"]);
  await validateDirectoryFrontmatter("skills", "SKILL.md", ["name", "description"]);
  await validateDirectoryFrontmatter("agents", ".md", ["name", "description"]);

  if (errors.length > 0) {
    console.error("Plugin validation failed:");
    for (const error of errors) {
      console.error(`- ${error}`);
    }
    process.exit(1);
  }

  console.log("Plugin validation passed.");
}

await main();
