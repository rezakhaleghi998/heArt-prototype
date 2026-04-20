import * as React from "react";
import { cn } from "@/lib/utils";

export const Textarea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn("min-h-28 w-full rounded-md border border-ink/15 bg-white px-3 py-3 text-sm outline-none focus:border-basil focus:ring-2 focus:ring-basil/20", className)}
      {...props}
    />
  )
);
Textarea.displayName = "Textarea";
