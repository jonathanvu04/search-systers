interface PromptCardProps {
  prompt: string;
}

export function PromptCard({ prompt }: PromptCardProps) {
  return (
    <section className="w-full max-w-xl rounded-2xl bg-white shadow-[0_24px_80px_rgba(15,23,42,0.08)] px-10 py-8">
      <h1 className="mb-6 text-center text-2xl font-semibold tracking-tight text-slate-800">
        {prompt}
      </h1>

      <div className="rounded-xl border border-slate-200 bg-slate-50/60 px-4 py-3">
      
        <textarea
          className="min-h-[160px] w-full resize-none rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 shadow-inner outline-none ring-0 focus:border-sky-400 focus:ring-2 focus:ring-sky-100"
          placeholder="Share your thoughts..."
        />
      </div>
    </section>
  );
}

