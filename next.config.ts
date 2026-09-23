import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,
  output: "standalone",
  turbopack: {
    root: __dirname,
  },
};

export default nextConfig;
