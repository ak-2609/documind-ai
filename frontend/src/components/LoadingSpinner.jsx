export default function LoadingSpinner({ label = "Loading…", compact = false }) {
  return (
    <span className="inline-flex items-center gap-2 text-sm text-slate-600" role="status">
      <span className={`${compact ? "h-4 w-4" : "h-5 w-5"} animate-spin rounded-full border-2 border-[#E8B89C] border-t-terracotta`} />
      {label}
    </span>
  );
}
