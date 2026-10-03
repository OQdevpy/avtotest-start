import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// `vite build --mode demo` — backendsiz demo: brauzer ichidagi server (src/lib/demoServer.js).
export default defineConfig(({ mode }) => {
  const demo = mode === "demo";
  return {
    plugins: [react()],
    base: demo ? "./" : "/",
    define: { __DEMO__: JSON.stringify(demo) },
    resolve: {
      alias: demo
        ? [{ find: /^\.{1,2}\/(lib\/)?transport$/, replacement: fileURLToPath(new URL("./src/lib/transport.demo.js", import.meta.url)) }]
        : [],
    },
    server: {
      port: 5173,
      proxy: { "/api": "http://127.0.0.1:8000" },
    },
    build: { sourcemap: false, outDir: demo ? "dist-demo" : "dist" },
  };
});
