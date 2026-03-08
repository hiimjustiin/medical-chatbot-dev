/** @type {import('next').NextConfig} */
const nextConfig = {
  // 设置前端端口为3001，避免与NestJS后端冲突
  experimental: {
    appDir: true,
  },
  // 自定义服务器配置
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:3000/api/:path*', // 代理到NestJS后端
      },
    ];
  },
};

export default nextConfig;
