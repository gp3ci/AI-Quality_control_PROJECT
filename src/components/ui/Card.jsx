import React from "react";
import { cn } from "../../lib/utils";

export const Card = ({ className, children, ...props }) => {
  return (
    <div className={cn("glass-panel overflow-hidden", className)} {...props}>
      {children}
    </div>
  );
};
