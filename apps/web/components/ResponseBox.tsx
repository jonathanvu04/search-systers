interface ResponseBoxProps {
  onSubmit?: () => void;
}

export function ResponseBox({ onSubmit }: ResponseBoxProps) {
  return (
    <div className="mt-6 flex justify-center">
      <button
        type="button"
        onClick={onSubmit}
        className="inline-flex h-11 items-center justify-center rounded-md bg-[#538BAC] px-10 text-sm font-semibold text-white shadow-[0_10px_30px_rgba(113,88,71,0.45)] transition hover:bg-[#5d4738] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#715847]/60 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-50"
      >
        Submit
      </button>
    </div>
  );
}

