import { PromptCard } from "../components/PromptCard";
import { ResponseBox } from "../components/ResponseBox";

export default function Home() {
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
            <PromptCard prompt="What gets you up in the morning?" />
            <ResponseBox />
          </div>
        </div>
      </div>
    </main>
  );
}
