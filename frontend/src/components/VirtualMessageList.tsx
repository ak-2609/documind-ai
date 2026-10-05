import { useEffect, useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import MessageBubble from "./MessageBubble";
import type { ChatMessage } from "../services/conversationService";

export default function VirtualMessageList({ messages }: { messages: ChatMessage[] }) {
  const parent = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({ count: messages.length, getScrollElement: () => parent.current, estimateSize: () => 130, overscan: 6 });
  useEffect(() => { virtualizer.scrollToIndex(Math.max(0, messages.length - 1), { align: "end", behavior: "smooth" }); }, [messages.length]);
  return <div ref={parent} className="h-full overflow-y-auto"><div className="relative mx-auto max-w-3xl" style={{ height: virtualizer.getTotalSize() }}>{virtualizer.getVirtualItems().map((row) => <div key={row.key} data-index={row.index} ref={virtualizer.measureElement} className="absolute left-0 top-0 w-full pb-5" style={{ transform: `translateY(${row.start}px)` }}><MessageBubble message={messages[row.index]} /></div>)}</div></div>;
}
