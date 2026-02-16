interface ResponseCardProps {
  text: string;
  score: number;
  rank?: number;
}

export function ResponseCard({ text, score, rank }: ResponseCardProps) {
  const scorePercent = Math.round(score * 100);
  return (
    <div className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
      {rank != null && (
        <span className="mb-2 inline-block text-xs font-medium text-slate-400">
          #{rank} · {scorePercent}% match
        </span>
      )}
      <p className="text-sm text-slate-800">{text}</p>
    </div>
  );
}
