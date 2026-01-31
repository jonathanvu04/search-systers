import { PromptCard } from "../components/PromptCard";
import { ResponseBox } from "../components/ResponseBox";

type Prompt = {
  id: number;
  text: string;
  reveal_date: string;
  created_at: string | null;
};

async function fetchTodayPrompt(): Promise<Prompt | null> {
  try {
    const res = await fetch("http://127.0.0.1:8000/prompts/2", {
      // Don't cache during development so you always see the latest prompt.
      cache: "no-store",
    });

    if (!res.ok) {
      return null;
    }

    return res.json();
  } catch {
    // If the API is down, fall back to a default prompt.
    return null;
  }
}

export default async function Home() {
  const prompt = await fetchTodayPrompt();

  const promptText =
    prompt?.text ?? "What gets you up in the morning?";
  const revealDate = prompt?.reveal_date ?? "";

  return (
    <main className="min-h-screen bg-[#F5EAD5] px-4 py-10 md:py-16">
      <div className="mx-auto flex max-w-5xl flex-col items-center gap-10 md:gap-14 md:items-center">
        <header className="w-full text-center">
          <h1 className="text-2xl font-semibold tracking-tight text-[#222222] sm:text-3xl md:text-4xl">
            we&apos;re not really strangers
          </h1>
          <p className="mx-auto mt-3 max-w-xl text-sm text-slate-600 sm:text-base">
            find like-minded people through introspective prompts.
          </p>
        </header>

        <div className="w-full flex justify-center">
          <div className="w-full max-w-xl">
            <PromptCard prompt={promptText} revealDate={revealDate} />
            <ResponseBox />
          </div>
        </div>
      </div>
    </main>
  );
}
