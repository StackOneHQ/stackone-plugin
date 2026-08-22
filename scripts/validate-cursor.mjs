// Validate .cursor-plugin/plugin.json against Cursor's own published schema
// (github.com/cursor/plugins/schemas/plugin.schema.json). CI checks that repo
// out at a pinned commit and passes its path as argv[2].
import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";
import Ajv from "ajv";
import addFormats from "ajv-formats";

const schemaRoot = process.argv[2];
if (!schemaRoot) {
  console.error("usage: node scripts/validate-cursor.mjs <path-to-cursor/plugins-checkout>");
  process.exit(2);
}
const schema = JSON.parse(readFileSync(resolve(schemaRoot, "schemas/plugin.schema.json"), "utf8"));
const manifest = JSON.parse(readFileSync(".cursor-plugin/plugin.json", "utf8"));

const ajv = new Ajv({ allErrors: true, strict: false });
addFormats(ajv);
const validate = ajv.compile(schema);
const errors = [];
if (!validate(manifest)) {
  for (const e of validate.errors) errors.push(`${e.instancePath || "/"} ${e.message}`);
}
if (manifest.logo && !existsSync(manifest.logo)) errors.push(`logo ${manifest.logo} not found`);
if (manifest.mcpServers && typeof manifest.mcpServers === "string" && !existsSync(manifest.mcpServers)) {
  errors.push(`mcpServers file ${manifest.mcpServers} not found`);
}
const mcp = JSON.parse(readFileSync("mcp.json", "utf8"));
if (!mcp.mcpServers || !mcp.mcpServers.stackone || !mcp.mcpServers.stackone.url) {
  errors.push("mcp.json must define mcpServers.stackone.url");
}
if (errors.length) {
  console.error("Cursor plugin validation failed:\n  " + errors.join("\n  "));
  process.exit(1);
}
console.log(`ok: .cursor-plugin/plugin.json valid against cursor/plugins schema (${manifest.name} v${manifest.version})`);
