import { cn } from "@/lib/utils";

export function StatusPill({ status }: { status: string }) {
  return (
    <span className={cn("rounded-md px-2 py-1 text-xs font-bold", status === "reviewed" ? "bg-basil/10 text-basil" : "bg-ink/5 text-ink/70")}>
      {status}
    </span>
  );
}
