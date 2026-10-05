import apiClient from "../api/client";

export type Citation = { document_name: string; page_number: number };
export type ChatMessage = { id?: string; role: "user" | "assistant"; content: string; citations?: Citation[]; created_at?: string; pending?: boolean };
export type Conversation = { id: string; title: string; created_at: string; updated_at: string };
export type ConversationDetail = Conversation & { messages: ChatMessage[] };

export async function listConversations(offset = 0, limit = 50): Promise<Conversation[]> { return (await apiClient.get("/conversations", { params: { offset, limit } })).data; }
export async function getConversation(id: string): Promise<ConversationDetail> { return (await apiClient.get(`/conversations/${id}`)).data; }
export async function renameConversation(id: string, title: string): Promise<Conversation> { return (await apiClient.patch(`/conversations/${id}`, { title })).data; }
export async function deleteConversation(id: string): Promise<void> { await apiClient.delete(`/conversations/${id}`); }
