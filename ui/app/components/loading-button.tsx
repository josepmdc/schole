import Button from "./button";
import { LoadingSpinner } from "./loading";

export interface LoadingButtonProps {
  isLoading: boolean;
  message: string;
  loadingText: string;
}

export default function LoadingButton(props: LoadingButtonProps) {
  const content = props.isLoading ? (
    <>
      <LoadingSpinner width={20} height={20} />
      {props.loadingText}
    </>
  ) : (
    props.message
  );

  return (
    <Button
      className="w-full flex items-center justify-center gap-2 py-2"
      type="submit"
      disabled={props.isLoading}
    >
      {content}
    </Button>
  );
}
