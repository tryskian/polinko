import { cp, rm } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const source = resolve(root, "site");
const destination = resolve(root, "dist");

await rm(destination, { recursive: true, force: true });
await cp(source, destination, { recursive: true });
