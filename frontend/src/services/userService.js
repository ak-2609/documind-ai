import apiClient from "../api/client";

export async function getCurrentUser() {
  const { data } = await apiClient.get("/me");
  return data;
}
