"""
Seed mock profiles and responses into Supabase.

Run once from the services/api directory with your venv active:
    python seed_mock.py

Uses the service_role key (from .env) which bypasses RLS.
"""

import os
import sys
import uuid

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL", "")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

if not url or not key:
    print("Error: Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env")
    sys.exit(1)

sb = create_client(url, key)

# ---------------------------------------------------------------------------
# 1. Mock profiles (deterministic UUIDs so re-runs are idempotent)
# ---------------------------------------------------------------------------
MOCK_PROFILES = [
    {"id": "00000000-0000-0000-0000-000000000001", "name": "Alice",   "age": 18},
    {"id": "00000000-0000-0000-0000-000000000002", "name": "Bob",     "age": 24},
    {"id": "00000000-0000-0000-0000-000000000003", "name": "Carlos",  "age": 35},
    {"id": "00000000-0000-0000-0000-000000000004", "name": "Diana",   "age": 42},
    {"id": "00000000-0000-0000-0000-000000000005", "name": "Evelyn",  "age": 55},
    {"id": "00000000-0000-0000-0000-000000000006", "name": "Frank",   "age": 67},
    {"id": "00000000-0000-0000-0000-000000000007", "name": "Grace",   "age": 73},
    {"id": "00000000-0000-0000-0000-000000000008", "name": "Taylor",   "age": 25},
    {"id": "00000000-0000-0000-0000-000000000009", "name": "Michael",   "age": 22},
    {"id": "00000000-0000-0000-0000-000000000010", "name": "Jasmine",   "age": 36},
    {"id": "00000000-0000-0000-0000-000000000011", "name": "William",   "age": 42},
    {"id": "00000000-0000-0000-0000-000000000012", "name": "Emma",   "age": 50},
]

print("Upserting mock profiles …")
sb.table("profiles").upsert(MOCK_PROFILES, on_conflict="id").execute()
print(f"  ✓ {len(MOCK_PROFILES)} profiles ready")

# ---------------------------------------------------------------------------
# 2. Ensure the prompt exists
# ---------------------------------------------------------------------------
PROMPT_TEXT = "What's something you believe about life that you didn't a year ago?"

existing = (
    sb.table("prompts")
    .select("id")
    .eq("text", PROMPT_TEXT)
    .limit(1)
    .execute()
)

if existing.data and len(existing.data) > 0:
    prompt_id = existing.data[0]["id"]
    print(f"  Prompt already exists (id={prompt_id})")
else:
    ins = sb.table("prompts").insert({"text": PROMPT_TEXT}).execute()
    prompt_id = ins.data[0]["id"]
    print(f"  ✓ Created prompt (id={prompt_id})")

# ---------------------------------------------------------------------------
# 3. Mock responses tied to profiles
# ---------------------------------------------------------------------------
MOCK_RESPONSES = [
    # Alice (18)
    {"user_id": "00000000-0000-0000-0000-000000000001",
     "text": "That failure isn't the end — it's just data you can learn from."},
    {"user_id": "00000000-0000-0000-0000-000000000001",
     "text": "You don't have to have everything figured out at 18."},

    # Bob (24)
    {"user_id": "00000000-0000-0000-0000-000000000002",
     "text": "Real friendships survive distance and silence."},
    {"user_id": "00000000-0000-0000-0000-000000000002",
     "text": "Comparison really is the thief of joy — I finally feel that, not just know it."},

    # Carlos (35)
    {"user_id": "00000000-0000-0000-0000-000000000003",
     "text": "Saying no is one of the most generous things you can do for yourself."},
    {"user_id": "00000000-0000-0000-0000-000000000003",
     "text": "Career success means nothing if you don't take care of your health."},

    # Diana (42)
    {"user_id": "00000000-0000-0000-0000-000000000004",
     "text": "Kids teach you more about patience than any book ever could."},
    {"user_id": "00000000-0000-0000-0000-000000000004",
     "text": "It's never too late to change your mind about who you want to be."},

    # Evelyn (55)
    {"user_id": "00000000-0000-0000-0000-000000000005",
     "text": "Grief doesn't shrink — you just grow around it."},
    {"user_id": "00000000-0000-0000-0000-000000000005",
     "text": "The people who matter most rarely ask you to prove your worth."},

    # Frank (67)
    {"user_id": "00000000-0000-0000-0000-000000000006",
     "text": "Retirement showed me that purpose doesn't come from a title."},

    # Grace (73)
    {"user_id": "00000000-0000-0000-0000-000000000007",
     "text": "Every decade teaches you that the last one's worries were smaller than you thought."},
    
    {"user_id": "00000000-0000-0000-0000-000000000008",
     "text": "The purpose of living is to discover why you’re alive."},
    
    {"user_id": "00000000-0000-0000-0000-000000000009",
     "text": "We spend our lives trying to understand the thing we’re currently living."},
    
    {"user_id": "00000000-0000-0000-0000-000000000010",
     "text": "Life is the process of becoming someone who can answer that question."},
    
    {"user_id": "00000000-0000-0000-0000-000000000011",
     "text": "We search for meaning just to realize the search is the meaning"},
    
    {"user_id": "00000000-0000-0000-0000-000000000012",
     "text": "The goal of life is to define what the goal of life is."},
    
    
]

rows = [{"prompt_id": prompt_id, **r} for r in MOCK_RESPONSES]

print(f"Inserting {len(rows)} mock responses …")
sb.table("responses").insert(rows).execute()
print(f"  ✓ {len(rows)} responses inserted")

print("\nDone! You can now view them via GET /responses or in the Supabase dashboard.")
