import { defineConfig } from "vite";
import path from "node:path";

const portfolioStaticDir = process.env.POLINKO_PORTFOLIO_STATIC_DIR
  ? path.resolve(__dirname, "..", process.env.POLINKO_PORTFOLIO_STATIC_DIR)
  : path.resolve(__dirname, "../public/portfolio");

export default defineConfig({
  root: __dirname,
  build: {
    outDir: portfolioStaticDir,
    emptyOutDir: true,
    chunkSizeWarningLimit: 650,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("/node_modules/d3") || id.includes("/node_modules/d3-sankey")) {
            return "vendor-d3";
          }
          if (id.includes("/node_modules/gsap") || id.includes("/node_modules/three")) {
            return "vendor-motion";
          }
          if (id.includes("/node_modules/")) {
            return "vendor";
          }
          return undefined;
        },
      },
    },
  },
});
