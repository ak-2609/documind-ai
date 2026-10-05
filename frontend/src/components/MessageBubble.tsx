import { memo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import CitationCard from "./CitationCard";
import type { ChatMessage } from "../services/conversationService";

const MessageBubble = memo(function MessageBubble({ message }: { message: ChatMessage }) {
  const user = message.role === "user";
  return <article className={`flex animate-message ${user ? "justify-end" : "justify-start"}`}><div className={user ? "max-w-[85%] rounded-2xl rounded-br-md bg-terracotta px-4 py-3 text-sm leading-6 text-white sm:max-w-[75%]" : "markdown max-w-[92%] rounded-2xl rounded-bl-md border border-line bg-white px-5 py-4 text-sm leading-7 text-ink shadow-[0_3px_14px_rgba(31,31,31,0.04)] sm:max-w-[80%]"}>{user ? <p className="whitespace-pre-wrap">{message.content}</p> : <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>}{!user && !!message.citations?.length && <section className="mt-4 border-t border-line pt-3"><p className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted">Sources</p><div className="flex flex-wrap gap-2">{message.citations.map((citation) => <CitationCard key={`${citation.document_name}-${citation.page_number}`} citation={citation} />)}</div></section>}</div></article>;
});
export default MessageBubble;
