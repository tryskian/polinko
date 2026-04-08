import { defineConfig } from "vite";
import path from "node:path";

const uiDir = path.resolve(process.cwd(), "../ui");

export default defineConfig({
  root: __dirname,
  build: {
    outDir: uiDir,
    emptyOutDir: true,
  },
});
