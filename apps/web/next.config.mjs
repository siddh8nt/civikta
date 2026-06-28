/** @type {import('next').NextConfig} */
const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  images: {
    remotePatterns: [{ protocol: "https", hostname: "picsum.photos" }],
  },
  // Proxy all /api/* calls to the FastAPI backend.
  // Route handlers in app/api/ (e.g. analytics) take precedence over rewrites.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
