import * as React from "react";
import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex h-11 items-center justify-center gap-2 rounded-md px-4 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-basil disabled:cursor-not-allowed disabled:opacity-50",
        variant === "primary" && "bg-basil text-white hover:bg-[#214f49]",
        variant === "secondary" && "border border-ink/15 bg-white text-ink hover:bg-ink/5",
        variant === "ghost" && "text-ink hover:bg-ink/5",
        className
      )}
      {...props}
    />
  );
}
