// Normalize NEXT_PUBLIC_API_URL by removing any trailing slashes to avoid double-slash URLs
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL
  ? process.env.NEXT_PUBLIC_API_URL.replace(/\/+$|\s+/g, '')
  : 'http://localhost:8000';
