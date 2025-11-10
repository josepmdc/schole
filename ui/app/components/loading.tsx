import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

interface LoadingSpinnerProps {
  width: number;
  height: number;
  color?: string;
}

export function LoadingSpinner(props: LoadingSpinnerProps) {
  return (
    <Loader2
      className="animate-spin"
      width={props.width}
      height={props.height}
      color={props.color}
    />
  );
}

export function Loading() {
  const [showLoading, setLoading] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(true), 150);
    return () => clearTimeout(timer);
  }, []);

  if (!showLoading) {
    return null;
  }

  return (
    <div className="absolute bg-white bg-opacity-60 z-10 h-full w-full flex items-center justify-center">
      <div className="flex items-center">
        <LoadingSpinner height={48} width={48} />
      </div>
    </div>
  );
}
