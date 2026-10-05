import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL;

if (!baseURL) {
  throw new Error("VITE_API_BASE_URL is required.");
}

let tokenProvider = null;

export function configureAuthTokenProvider(provider) {
  tokenProvider = provider;
}

const apiClient = axios.create({
  baseURL: baseURL.replace(/\/$/, ""),
  timeout: 120000,
  headers: { Accept: "application/json" },
});

apiClient.interceptors.request.use(async (config) => {
  const token = tokenProvider ? await tokenProvider() : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error),
);

export default apiClient;
