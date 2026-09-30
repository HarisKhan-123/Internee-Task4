"""
Generates the actual career-path content: job roles, rationale, skill
gaps and a learning path, given a profile and the candidate career
clusters the TensorFlow classifier narrowed it down to.

Uses the OpenAI Python SDK (`pip install openai`) - the same client
library and request shape the task brief asked for - but pointed at
Groq's free, OpenAI-compatible endpoint instead of api.openai.com,
since OpenAI's API is pay-per-token with no standing free tier while
Groq's is genuinely free (no card required, rate-limited rather than
metered). See README.md for why, and for the one-line change needed
to point this at real OpenAI later if you have paid access.
"""

import json
import os
import re

from openai import OpenAI

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-120b"


class LLMConfigError(RuntimeError):
    pass


def _client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise LLMConfigError(
            "GROQ_API_KEY is not set. Get a free key at "
            "https://console.groq.com/keys and put it in your .env file "
            "(see .env.example)."
        )
    return OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)


def _extract_json(text):
    """The model is asked to reply with only JSON, but strip code
    fences or stray text defensively in case it doesn't comply."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(\[.*\]|\{.*\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    else:
        start = min(
            (i for i in (text.find("["), text.find("{")) if i != -1),
            default=0,
        )
        end = max(text.rfind("]"), text.rfind("}"))
        if start >= 0 and end > start:
            text = text[start:end + 1]
    return json.loads(text)


def generate_career_paths(profile, candidate_clusters):
    """
    profile: {"skills": [...], "interests": [...], "experience": str, "goals": str}
    candidate_clusters: list of category names from the TF classifier
    Returns a list of up to 3 dicts:
        {role, matchReason, skillsToDevelop: [...], learningPath: [{title, description, estWeeks}]}
    """
    client = _client()

    prompt = f"""You are a career advisor for university/college interns.

Intern profile:
- Skills: {", ".join(profile.get("skills", [])) or "none listed"}
- Interests: {", ".join(profile.get("interests", [])) or "none listed"}
- Experience level: {profile.get("experience", "not specified")}
- Other notes: {profile.get("goals", "none")}

A separate classifier has narrowed their likely direction to these career
clusters: {", ".join(candidate_clusters)}.

Suggest exactly 3 specific, well-matched job roles for this intern, drawing
from (but not limited to) those clusters. Roles should be concrete job
titles, not the cluster names themselves, and should be genuinely distinct
from each other.

Reply with ONLY a JSON array, no other text, shaped exactly like:
[
  {{
    "role": "Job title",
    "matchReason": "2-3 sentences on why this fits their specific skills and interests",
    "skillsToDevelop": ["short skill", "short skill", "short skill"],
    "learningPath": [
      {{"title": "Step title", "description": "1 sentence on what to actually do", "estWeeks": 2}}
    ]
  }}
]
Each learningPath must have 4 to 6 steps, ordered from foundational to
advanced, concrete and actionable (name real tools, project types, or
certifications where relevant)."""

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=2000,
    )
    raw = response.choices[0].message.content
    data = _extract_json(raw)

    if not isinstance(data, list) or not data:
        raise ValueError("Model did not return a usable list of paths.")
    return data[:3]


def generate_nudge(role, done_steps, remaining_steps):
    client = _client()
    prompt = (
        f"An intern is working toward becoming a {role}. "
        f"They've completed these learning steps: "
        f"{'; '.join(done_steps) if done_steps else 'none yet'}. "
        f"Remaining steps: "
        f"{'; '.join(remaining_steps) if remaining_steps else 'none - they are done'}. "
        "Write a short, warm, practical nudge (2-3 sentences max) that names "
        "one concrete next action. Plain text only, no headers or markdown."
    )
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()
