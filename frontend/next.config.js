/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Enable server components by default
    serverComponentsExternalPackages: []
  },
  // Enable static optimization where possible
  output: 'standalone',
  // Image optimization
  images: {
    domains: ['localhost'],
    formats: ['image/webp', 'image/avif']
  }
}

module.exports = nextConfig