"use client";

import { useState } from "react";
import { supabase } from "../lib/supabase";
import { ResponseCard } from "./ResponseCard";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type SimilarResponse = { id: number; text: string; score: number };
type AgeResponse = { id: number; text: string; name: string | null; age: number | null };
const SIMILAR_TOP_K = 4;

const AGE_FILTERS = [
  { label: "10–20", min: 10, max: 20 },
  { label: "20–30", min: 20, max: 30 },
  { label: "30–40", min: 30, max: 40 },
  { label: "40–50", min: 40, max: 50 },
  { label: "50–60", min: 50, max: 60 },
  { label: "60–70", min: 60, max: 70 },
  { label: "70+",   min: 70, max: 120 },
] as const;

type ActiveFilter = "similar" | string; // "similar" or "10–20", "20–30", etc.

interface PromptResponseFormProps {
  promptId: number;
  promptText: string;
}

export function PromptResponseForm({ promptId, promptText }: PromptResponseFormProps) {
  const [text, setText] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  const [activeFilter, setActiveFilter] = useState<ActiveFilter>("similar");
  const [similarResponses, setSimilarResponses] = useState<SimilarResponse[]>([]);
  const [ageResponses, setAgeResponses] = useState<AgeResponse[]>([]);
  const [filterLoading, setFilterLoading] = useState(false);
  const [lastResponseId, setLastResponseId] = useState<number | null>(null);

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
    setAgeResponses([]);
    setActiveFilter("similar");

    try {
      // Attach user_id if the user is signed in
      const { data: { user } } = await supabase.auth.getUser();
      const submitRes = await fetch(`${API_URL}/responses/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt_id: promptId,
          text: trimmed,
          user_id: user?.id ?? null,
        }),
      });

      if (!submitRes.ok) {
        const errBody = await submitRes.text();
        throw new Error(`Submit failed: ${submitRes.status} ${errBody}`);
      }
      const submitData: { response_id: number } = await submitRes.json();
      const responseId = submitData.response_id;
      if (!responseId) throw new Error("No response ID returned");
      setLastResponseId(responseId);

      const similarRes = await fetch(
        `${API_URL}/responses/${responseId}/similar?top_k=${SIMILAR_TOP_K}`
      );
      if (similarRes.ok) {
        const similar: SimilarResponse[] = await similarRes.json();
        const filtered = similar
          .filter((item) => item.id !== responseId)
          .slice(0, SIMILAR_TOP_K);
        setSimilarResponses(filtered);
      }

      setText("");
      setStatus("success");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      setStatus("error");
    }
  }

  async function handleFilterChange(filter: ActiveFilter) {
    setActiveFilter(filter);

    if (filter === "similar") return;

    const range = AGE_FILTERS.find((f) => f.label === filter);
    if (!range) return;

    setFilterLoading(true);
    try {
      const res = await fetch(
        `${API_URL}/prompts/${promptId}/responses?age_min=${range.min}&age_max=${range.max}`
      );
      if (res.ok) {
        const data: AgeResponse[] = await res.json();
        const filtered = lastResponseId == null
          ? data
          : data.filter((item) => item.id !== lastResponseId);
        setAgeResponses(filtered);
      }
    } catch {
      setAgeResponses([]);
    } finally {
      setFilterLoading(false);
    }
  }

  const hasResults = status === "success" && (similarResponses.length > 0 || lastResponseId);

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

      {hasResults && (
        <div className="mt-8 w-full">
          <div className="mb-4 flex flex-wrap gap-2">
            <button
              onClick={() => handleFilterChange("similar")}
              className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                activeFilter === "similar"
                  ? "bg-[#538BAC] text-white"
                  : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
              }`}
            >
              Similar
            </button>
            {AGE_FILTERS.map((f) => (
              <button
                key={f.label}
                onClick={() => handleFilterChange(f.label)}
                className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                  activeFilter === f.label
                    ? "bg-[#538BAC] text-white"
                    : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {filterLoading && (
            <p className="text-sm text-slate-400">Loading…</p>
          )}

          {activeFilter === "similar" && !filterLoading && (
            <div className="flex flex-col gap-3">
              {similarResponses.length > 0 ? (
                similarResponses.map((item, i) => (
                  <ResponseCard
                    key={item.id}
                    text={item.text}
                    score={item.score}
                    rank={i + 1}
                  />
                ))
              ) : (
                <p className="text-sm text-slate-400">No similar responses found.</p>
              )}
            </div>
          )}

          {activeFilter !== "similar" && !filterLoading && (
            <div className="flex flex-col gap-3">
              {ageResponses.length > 0 ? (
                ageResponses.map((item) => (
                  <ResponseCard
                    key={item.id}
                    text={item.text}
                    name={item.name}
                    age={item.age}
                  />
                ))
              ) : (
                <p className="text-sm text-slate-400">
                  No responses from this age group.
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
