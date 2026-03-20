"use client";

import { useEffect, useState } from "react";
import { supabase, signInWithGoogle, signOut } from "../lib/supabase";
import type { User } from "@supabase/supabase-js";

type Profile = { name: string; age: number | "" };

export function AuthButton() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [profile, setProfile] = useState<Profile>({ name: "", age: "" });
  const [saving, setSaving] = useState(false);

  async function loadProfile(userId: string) {
    const { data } = await supabase
      .from("profiles")
      .select("name, age")
      .eq("id", userId)
      .maybeSingle();

    if (data) {
      setProfile({ name: data.name ?? "", age: data.age ?? "" });
    } else {
      // Auto-create a profile row on first sign-in so the user
      // exists in the profiles table and responses can link to them.
      await supabase.from("profiles").upsert(
        { id: userId },
        { onConflict: "id" }
      );
    }
  }

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
      setLoading(false);
      if (data.user) loadProfile(data.user.id);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      if (session?.user) loadProfile(session.user.id);
    });

    return () => subscription.unsubscribe();
  }, []);

  async function saveProfile() {
    if (!user) return;
    setSaving(true);

    const row = {
      id: user.id,
      name: profile.name || null,
      age: profile.age === "" ? null : Number(profile.age),
    };

    await supabase.from("profiles").upsert(row, { onConflict: "id" });
    setSaving(false);
    setEditOpen(false);
  }

  if (loading) {
    return <div className="h-9 w-20" />;
  }

  if (!user) {
    return (
      <button
        onClick={() => signInWithGoogle()}
        className="rounded-md bg-[#538BAC] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#436f8a]"
      >
        Sign in
      </button>
    );
  }

  const displayName =
    profile.name ||
    user.user_metadata?.full_name ||
    user.email?.split("@")[0] ||
    "Profile";
  const avatarUrl = user.user_metadata?.avatar_url as string | undefined;

  return (
    <div className="relative">
      <button
        onClick={() => {
          setMenuOpen((prev) => !prev);
          setEditOpen(false);
        }}
        className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
      >
        {avatarUrl ? (
          <img
            src={avatarUrl}
            alt=""
            className="h-6 w-6 rounded-full"
            referrerPolicy="no-referrer"
          />
        ) : (
          <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#538BAC] text-xs font-bold text-white">
            {displayName[0]?.toUpperCase()}
          </span>
        )}
        <span className="hidden sm:inline">{displayName}</span>
      </button>

      {menuOpen && !editOpen && (
        <div className="absolute right-0 z-10 mt-2 w-44 rounded-md border border-slate-200 bg-white py-1 shadow-lg">
          <button
            onClick={() => setEditOpen(true)}
            className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-100"
          >
            Edit Profile
          </button>
          <button
            onClick={async () => {
              await signOut();
              setMenuOpen(false);
            }}
            className="w-full px-4 py-2 text-left text-sm text-slate-700 hover:bg-slate-100"
          >
            Sign out
          </button>
        </div>
      )}

      {menuOpen && editOpen && (
        <div className="absolute right-0 z-10 mt-2 w-64 rounded-md border border-slate-200 bg-white p-4 shadow-lg">
          <h3 className="mb-3 text-sm font-semibold text-slate-800">
            Edit Profile
          </h3>

          <label className="mb-1 block text-xs font-medium text-slate-500">
            Name
          </label>
          <input
            type="text"
            value={profile.name}
            onChange={(e) =>
              setProfile((p) => ({ ...p, name: e.target.value }))
            }
            className="mb-3 w-full rounded-md border border-slate-200 px-3 py-1.5 text-sm text-slate-800 outline-none focus:border-[#538BAC] focus:ring-1 focus:ring-[#538BAC]"
            placeholder="Your name"
          />

          <label className="mb-1 block text-xs font-medium text-slate-500">
            Age
          </label>
          <input
            type="number"
            min={1}
            max={120}
            value={profile.age}
            onChange={(e) =>
              setProfile((p) => ({
                ...p,
                age: e.target.value === "" ? "" : Number(e.target.value),
              }))
            }
            className="mb-4 w-full rounded-md border border-slate-200 px-3 py-1.5 text-sm text-slate-800 outline-none focus:border-[#538BAC] focus:ring-1 focus:ring-[#538BAC]"
            placeholder="Your age"
          />

          <div className="flex gap-2">
            <button
              onClick={saveProfile}
              disabled={saving}
              className="flex-1 rounded-md bg-[#538BAC] px-3 py-1.5 text-sm font-medium text-white transition hover:bg-[#436f8a] disabled:opacity-60"
            >
              {saving ? "Saving…" : "Save"}
            </button>
            <button
              onClick={() => setEditOpen(false)}
              className="flex-1 rounded-md border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-600 transition hover:bg-slate-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
