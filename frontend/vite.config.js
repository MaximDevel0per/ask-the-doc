import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy: /api-Anfragen gehen im Dev-Modus ans FastAPI-Backend (Port 8000)
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
