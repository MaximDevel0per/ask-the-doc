import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy: /api-Anfragen gehen im Dev-Modus ans FastAPI-Backend (Port 8000)
//wird automatisch beim start aufgerufen
// Im Container zeigt VITE_API_PROXY auf den backend-Service statt auf localhost
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": process.env.VITE_API_PROXY || "http://localhost:8000",
    },
  },
});
