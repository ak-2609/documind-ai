import apiClient from "../api/client";

export async function askQuestion({ question, conversationId }) {
  const payload = { question };
  if (conversationId) {
    payload.conversation_id = conversationId;
  }
  const { data } = await apiClient.post("/chat", payload);
  return data;
}
