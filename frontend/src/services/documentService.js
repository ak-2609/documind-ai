import apiClient from "../api/client";

export async function uploadDocument(file, onUploadProgress) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post("/upload", formData, {
    onUploadProgress,
  });
  return data;
}
