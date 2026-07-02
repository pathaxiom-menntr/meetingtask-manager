import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces a self-contained .next/standalone folder — required for the
  // production Docker image. Only node_modules needed at runtime are copied.
  output: "standalone",
};

export default nextConfig;
