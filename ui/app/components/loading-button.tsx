import Button, { type ButtonProps } from "./button";
import { LoadingSpinner } from "./loading";
import React from "react";

export interface LoadingButtonProps extends Omit<ButtonProps, "children" | "disabled"> {
  isLoading: boolean;
  children: React.ReactNode;
  loadingText: string;
}

export default function LoadingButton({
  isLoading,
  children,
  loadingText,
  className,
  ...rest
}: LoadingButtonProps) {
  const content = isLoading ? (
    <>
      <LoadingSpinner width={20} height={20} />
      {loadingText}
    </>
  ) : (
    children
  );

  return (
    <Button
      className={`w-full flex items-center justify-center gap-2 py-2 ${className || ""}`}
      disabled={isLoading}
      {...rest}
    >
      {content}
    </Button>
  );
}
