import { PromptResponseForm } from "../components/PromptResponseForm";
import { AuthButton } from "../components/AuthButton";
import { supabase } from "../lib/supabase";

type Prompt = {
  id: number;
  text: string;
  created_at: string | null;
};

async function fetchPrompt(promptId: number): Promise<Prompt | null> {
  const { data, error } = await supabase
    .from("prompts")
    .select("*")
    .eq("id", promptId)
    .single();

  if (error || !data) return null;
  return data as Prompt;
}

export default async function Home() {
  const promptId = 2; // Your prompt: "What gets you up in the morning?"
  const prompt = await fetchPrompt(promptId);

  const promptText = prompt?.text ?? "Error";

  return (
    <main className="min-h-screen bg-[#F5EAD5] px-4 py-10 md:py-16">
      <div className="mx-auto flex max-w-5xl flex-col items-center gap-10 md:gap-14 md:items-center">
        <header className="w-full">
          <div className="flex items-center justify-between">
            <div className="flex-1" />
            <h1 className="text-2xl font-semibold tracking-tight text-[#222222] sm:text-3xl md:text-4xl">
              we&apos;re not really strangers
            </h1>
            <div className="flex flex-1 justify-end">
              <AuthButton />
            </div>
          </div>
          <p className="mx-auto mt-3 max-w-xl text-center text-sm text-slate-600 sm:text-base">
            find like-minded people through introspective prompts.
          </p>
        </header>

        <div className="w-full flex justify-center">
          <PromptResponseForm
            promptId={prompt?.id ?? 1}
            promptText={promptText}
          />
        </div>
      </div>
    </main>
  );
}
