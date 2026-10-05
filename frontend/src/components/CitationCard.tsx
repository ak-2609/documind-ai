import type { Citation } from "../services/conversationService";

export default function CitationCard({ citation }: { citation: Citation }) {
  return <button type="button" title="PDF preview will be available here" className="inline-flex items-center gap-1.5 rounded-lg border border-[#ECD9CE] bg-terracotta-light px-2.5 py-1.5 text-left text-xs font-medium text-[#814022] transition hover:bg-[#F0D6C8]"><span>📄</span><span className="max-w-40 truncate">{citation.document_name}</span><span className="text-[#A85731]">Page {citation.page_number}</span></button>;
}
