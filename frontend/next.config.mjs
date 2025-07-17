/** @type {import('next').NextConfig} */
const NEXT_PUBLIC_SERVER_BASE_URL =
  process.env.NEXT_PUBLIC_SERVER_BASE_URL || 'http://localhost:8000';

const nextConfig = {
  reactStrictMode: false,
  rewrites: async () => {
    return [
      {
        source: '/api/auth/token/:path*',
        destination: `${NEXT_PUBLIC_SERVER_BASE_URL}/api/v1/auth/token/:path*`,
      },
      {
        source: '/api/users/register',
        destination: `${NEXT_PUBLIC_SERVER_BASE_URL}/api/v1/users/register`,
      },
      {
        source: '/api/knowledge-base/:path*',
        destination: `${NEXT_PUBLIC_SERVER_BASE_URL}/api/v1/knowledge-base/:path*`,
      },
      {
        source: '/api/chat/:path*',
        destination: `${NEXT_PUBLIC_SERVER_BASE_URL}/api/v1/chat/:path*`,
      },
    ];
  },
};

export default nextConfig;
