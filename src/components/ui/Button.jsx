import React from "react";
import { cn } from "../../lib/utils";

export const Button = React.forwardRef(({ className, variant = "primary", size = "default", children, ...props }, ref) => {
  const baseStyles = "inline-flex items-center justify-center rounded-xl font-medium transition-all focus:outline-none disabled:opacity-50 disabled:pointer-events-none";
  
  const variants = {
    primary: "bg-cyanAccent/10 text-cyan-400 border border-cyanAccent/50 hover:bg-cyanAccent/20 hover:shadow-[0_0_15px_rgba(82,39,255,0.4)]",
    secondary: "bg-copperAccent/10 text-amber-500 border border-copperAccent/50 hover:bg-copperAccent/20 hover:shadow-[0_0_15px_rgba(255,159,252,0.4)]",
    ghost: "hover:bg-slate-800/50 text-slate-300 hover:text-white",
    pulse: "bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg animate-pulse-glow hover:opacity-90 border border-cyanAccent",
    gradient: "bg-gradient-to-r from-cyanAccent to-purple-500 text-white hover:opacity-90 shadow-lg border-none"
  };

  const sizes = {
    default: "h-10 px-4 py-2 text-sm",
    sm: "h-8 px-3 text-xs",
    lg: "h-12 px-8 text-base",
    icon: "h-10 w-10 flex items-center justify-center p-0"
  };

  return (
    <button
      ref={ref}
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      {...props}
    >
      {children}
    </button>
  );
});

Button.displayName = "Button";
