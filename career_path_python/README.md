# AI Career Path Recommender

A personalized career recommendation tool for interns: input your skills
and interests, get AI-suggested job roles and learning paths, and track
your progress through them over time.

Built with **Python + TensorFlow + the OpenAI Python SDK**, per the task
brief — with one substitution explained below.

## About the OpenAI API substitution

The task brief names the OpenAI API. OpenAI's API is **pay-per-token with
no standing free tier** (confirmed as of September 2026 — new accounts get
no automatic credits, and the free tier is a heavily rate-limited $15
trial). To keep this runnable at zero cost, the app uses the **OpenAI
Python SDK** (`pip install openai`, the exact library the brief implies)
pointed at **Groq's free, OpenAI-compatible endpoint** instead of
`api.openai.com`. Groq's free tier needs no credit card and is rate-limited
rather than metered — plenty for a personal/portfolio project like this.

If you get paid OpenAI access later, switching back is a two-line change in
`services/llm_service.py`:

```python
GROQ_BASE_URL = "https://api.groq.com/openai/v1"   # replace with "https://api.openai.com/v1" (or delete base_url entirely)
GROQ_MODEL = "llama-3.3-70b-versatile"              # replace with "gpt-4o-mini" or similar
```

Everything else — the client code, the request/response shape, the JSON
parsing — is identical either way, since Groq deliberately mirrors OpenAI's
API.

## How TensorFlow fits in

Open-ended reasoning (matching a free-text profile to specific job titles,
writing a rationale, building a learning path) is what the LLM is for.
TensorFlow is used for what it's actually good at here: a small **text
classifier** (`model/`) trained on labeled examples that narrows a profile
down to a few likely career clusters (e.g. "Embedded Systems & IoT",
"Digital Marketing & SEO") before the LLM writes the specific roles. This
keeps the LLM prompt grounded and gives the pipeline a real, defensible use
for a trained model rather than bolting TensorFlow on decoratively.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Get a free Groq API key (no card required)
#    https://console.groq.com/keys
cp .env.example .env
# then edit .env and paste your key in

# 4. Train the TensorFlow classifier (one-time, ~10 seconds)
python -m model.train_classifier

# 5. Run the app
python app.py
```

Open **http://localhost:5000**.

## How it works

1. You enter skills, interests, experience level, and optional goals.
2. `model/classifier.py` scores your profile against a small set of career
   clusters using the trained TensorFlow model.
3. `services/llm_service.py` sends your profile + the top clusters to the
   LLM (via the OpenAI SDK → Groq) and gets back 3 specific job roles, each
   with a match rationale, skills to develop, and a 4–6 step learning path.
4. Everything is saved to a local SQLite database (`career_recommender.db`,
   created automatically) keyed to a browser cookie, so your profile,
   chosen path, and checked-off progress persist across visits.
5. Checking off a learning step timestamps it; the progress bar and a
   "Get a nudge" button (a second, lighter LLM call) use that history to
   give you a concrete next action.

## Project structure

```
app.py                    Flask app and API routes
db.py                     SQLite persistence (profile, paths, progress)
model/
  train_classifier.py     Trains and saves the TF text classifier
  classifier.py           Loads the model, predicts career clusters
data/
  training_data.py        Labeled examples the classifier trains on
services/
  llm_service.py          OpenAI SDK client (pointed at Groq), prompts
templates/index.html      Page shell
static/app.js             Frontend logic (fetches the API, renders UI)
static/style.css          Styling
```

## Retraining / extending the classifier

If recommendations feel off for a particular field, add more labeled
examples to `data/training_data.py` (or a new category to `CATEGORIES`),
then re-run:

```bash
python -m model.train_classifier
```

No need to restart anything else — `model/classifier.py` loads the saved
model fresh on first use after a restart.
