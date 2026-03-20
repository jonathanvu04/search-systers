interface ResponseCardProps {
  text: string;
  score?: number;
  rank?: number;
  name?: string | null;
  age?: number | null;
}

export function ResponseCard({ text, score, rank, name, age }: ResponseCardProps) {
  const hasScore = score != null && rank != null;
  const hasProfile = name || age != null;

  return (
    <div className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
      {hasScore && (
        <span className="mb-2 inline-block text-xs font-medium text-slate-400">
          #{rank} · {Math.round(score * 100)}% match
        </span>
      )}
      {!hasScore && hasProfile && (
        <span className="mb-2 inline-block text-xs font-medium text-slate-400">
          {name ?? "Anonymous"}{age != null ? `, age ${age}` : ""}
        </span>
      )}
      <p className="text-sm text-slate-800">{text}</p>
    </div>
  );
}
