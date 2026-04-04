import { defineConfig } from "vite";

export default defineConfig({
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: {
      "/health": "http://127.0.0.1:8000",
      "/chat": "http://127.0.0.1:8000",
      "/chats": "http://127.0.0.1:8000",
      "/session": "http://127.0.0.1:8000",
      "/skills": "http://127.0.0.1:8000",
    },
  },
});
