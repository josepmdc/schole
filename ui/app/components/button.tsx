import React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

export default function Button({ children, className, ...rest }: ButtonProps) {
  return (
    <button
      className={`px-6 py-2 m-2 rounded-lg  border border-black cursor-pointer hover:shadow-[0_4px_0_0_#000000] hover:translate-y-[-4px] my-4 ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
}
