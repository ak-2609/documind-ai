export type ChatAttachment = {
  id: string;
  name: string;
  status: "uploading" | "indexed" | "failed";
};

export default function ChatAttachment({ attachment }: { attachment: ChatAttachment }) {
  const status = attachment.status === "uploading" ? "Indexing…" : attachment.status === "indexed" ? "Ready for questions" : "Upload failed";
  const tone = attachment.status === "failed" ? "text-danger" : attachment.status === "indexed" ? "text-success" : "text-muted";
  return <div className="flex w-full max-w-[320px] items-center gap-3 rounded-xl border border-line bg-[#FBF8F5] px-3 py-2.5"><span className="grid h-8 w-8 place-items-center rounded-lg bg-terracotta-light text-base">📄</span><div className="min-w-0"><p className="truncate text-sm font-medium text-ink">{attachment.name}</p><p className={`mt-0.5 text-xs ${tone}`}>{status}</p></div></div>;
}
