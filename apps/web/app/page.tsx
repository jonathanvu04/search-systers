import { PromptCard } from "../components/PromptCard";
import { ResponseBox } from "../components/ResponseBox";

export default function Home() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#FBF6F4] px-4">
      <div className="flex flex-col items-center">
        <PromptCard prompt="What gets you up in the morning?" />
        <ResponseBox />
      </div>
    </main>
  );
}
