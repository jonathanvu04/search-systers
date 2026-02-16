"use client";

import { useState } from "react";
import { supabase } from "../lib/supabase";
import { ResponseCard } from "./ResponseCard";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type SimilarResponse = { id: number; text: string; score: number };

interface PromptResponseFormProps {
  promptId: number;
  promptText: string;
}

export function PromptResponseForm({ promptId, promptText }: PromptResponseFormProps) {
  const [text, setText] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const [similarResponses, setSimilarResponses] = useState<SimilarResponse[]>([]);

  async function handleSubmit() {
    const trimmed = text.trim();
    if (!trimmed) {
      setError("Please enter a response.");
      setStatus("error");
      return;
    }

    setError(null);
    setStatus("submitting");
    setSimilarResponses([]);

    try {
      // Step 1: Insert response into Supabase
      const { data: inserted, error: insertError } = await supabase
        .from("responses")
        .insert({ prompt_id: promptId, text: trimmed })
        .select("id")
        .single();

      if (insertError) {
        throw new Error(insertError.message);
      }

      const responseId = inserted?.id;
      if (!responseId) {
        throw new Error("No response ID returned");
      }

      // Step 2: Call API to compute and store embeddings for all responses
      const embedRes = await fetch(`${API_URL}/responses/${responseId}/embed`, {
        method: "POST",
      });

      if (!embedRes.ok) {
        const errBody = await embedRes.text();
        throw new Error(`Embedding failed: ${embedRes.status} ${errBody}`);
      }

      // Step 3: Fetch top 3 similar responses
      const similarRes = await fetch(
        `${API_URL}/responses/${responseId}/similar?top_k=3`
      );
      if (similarRes.ok) {
        const similar: SimilarResponse[] = await similarRes.json();
        setSimilarResponses(similar);
      }

      setText("");
      setStatus("success");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      setStatus("error");
    }
  }

  return (
    <div className="w-full max-w-xl">
      <section className="w-full max-w-xl rounded-2xl bg-white shadow-[0_24px_80px_rgba(15,23,42,0.08)] px-10 py-8">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-800">
            {promptText}
          </h1>
        </div>

        <div className="rounded-xl border border-slate-200 bg-slate-50/60 px-4 py-3">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={status === "submitting"}
            className="min-h-[160px] w-full resize-none rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 shadow-inner outline-none ring-0 focus:border-sky-400 focus:ring-2 focus:ring-sky-100 disabled:opacity-60"
            placeholder="Share your thoughts..."
          />
        </div>
      </section>

      <div className="mt-6 flex flex-col items-center gap-2">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={status === "submitting"}
          className="inline-flex h-11 items-center justify-center rounded-md bg-[#538BAC] px-10 text-sm font-semibold text-white shadow-[0_10px_30px_rgba(113,88,71,0.45)] transition hover:bg-[#5d4738] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#715847]/60 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-50 disabled:opacity-60"
        >
          {status === "submitting" ? "Submitting…" : "Submit"}
        </button>

        {status === "success" && (
          <p className="text-sm text-green-600">Response saved and embedded.</p>
        )}
        {status === "error" && error && (
          <p className="text-sm text-red-600">{error}</p>
        )}
      </div>

      {similarResponses.length > 0 && (
        <div className="mt-8 w-full">
          <h2 className="mb-3 text-sm font-medium text-slate-600">
            Similar responses
          </h2>
          <div className="flex flex-col gap-3">
            {similarResponses.map((item, i) => (
              <ResponseCard
                key={item.id}
                text={item.text}
                score={item.score}
                rank={i + 1}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
