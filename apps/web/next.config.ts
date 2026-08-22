import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Docker copies Next's standalone server, while Vercel performs its own
  // function tracing and packaging. Enabling both at once breaks Vercel's
  // onBuildComplete hook under Next 16.
  output: process.env.VERCEL === "1" ? undefined : "standalone",
  poweredByHeader: false,
  async headers() {
    return [{
      source: "/(.*)",
      headers: [
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "X-Frame-Options", value: "DENY" },
        { key: "Referrer-Policy", value: "no-referrer" },
        { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
      ],
    }];
  },
};

export default nextConfig;
