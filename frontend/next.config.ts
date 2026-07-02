import path from "path";
import { loadEnvConfig } from "@next/env";
import type { NextConfig } from "next";

// Load shared .env from project root (same file used by backend and Docker Compose).
loadEnvConfig(path.resolve(__dirname, ".."));

const nextConfig: NextConfig = {
  output: "standalone",
  allowedDevOrigins: ["192.168.2.162"],
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};

export default nextConfig;
