"""
AI Career Path Recommender - Flask backend.

Flow per request to /api/recommend:
    1. TensorFlow classifier narrows the profile to a few likely
       career clusters (model/classifier.py).
    2. The LLM (services/llm_service.py, via the OpenAI SDK pointed at
       Groq's free endpoint) turns those clusters + the full profile
       into 3 specific roles, each with a rationale, skill gaps, and a
       step-by-step learning path.
    3. The result is saved to SQLite (db.py) under a session cookie so
       progress persists across visits.

Run:
    python -m model.train_classifier   # once, to train the classifier
    python app.py                      # starts the server on :5000
"""

import os

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, request, render_template, make_response

import db
from model.classifier import predict_clusters, ModelNotTrainedError
from services.llm_service import generate_career_paths, generate_nudge, LLMConfigError

app = Flask(__name__)
db.init_db()

SESSION_COOKIE = "cpr_session_id"


def _get_or_create_session():
    session_id = request.cookies.get(SESSION_COOKIE)
    state = db.get_state(session_id) if session_id else None
    if state is None:
        session_id = db.create_session()
        state = db.get_state(session_id)
    return session_id, state


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    session_id, state = _get_or_create_session()
    resp = make_response(jsonify(state))
    resp.set_cookie(SESSION_COOKIE, session_id, max_age=60 * 60 * 24 * 365, httponly=True)
    return resp


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    session_id, _ = _get_or_create_session()
    body = request.get_json(force=True) or {}
    skills = [s.strip() for s in body.get("skills", []) if s.strip()]
    interests = [s.strip() for s in body.get("interests", []) if s.strip()]
    experience = body.get("experience", "")
    goals = body.get("goals", "")

    if not skills and not interests:
        return jsonify({"error": "Add at least one skill or interest."}), 400

    try:
        clusters = [c for c, _ in predict_clusters(skills, interests, top_k=3)]
    except ModelNotTrainedError as e:
        return jsonify({"error": str(e)}), 503

    profile = {
        "skills": skills,
        "interests": interests,
        "experience": experience,
        "goals": goals,
    }

    try:
        paths = generate_career_paths(profile, clusters)
    except LLMConfigError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"Couldn't generate recommendations: {e}"}), 502

    # assign stable ids the frontend and progress tracking rely on
    for pi, p in enumerate(paths):
        p["id"] = f"p{pi}"
        for si, s in enumerate(p.get("learningPath", [])):
            s["id"] = f"p{pi}_s{si}"

    db.save_recommendation(session_id, profile, paths)

    resp = make_response(jsonify({
        "clusters": clusters,
        "profile": profile,
        "paths": paths,
    }))
    resp.set_cookie(SESSION_COOKIE, session_id, max_age=60 * 60 * 24 * 365, httponly=True)
    return resp


@app.route("/api/select-path", methods=["POST"])
def api_select_path():
    session_id, _ = _get_or_create_session()
    body = request.get_json(force=True) or {}
    path_id = body.get("path_id")
    db.select_path(session_id, path_id)
    return jsonify({"ok": True})


@app.route("/api/progress", methods=["POST"])
def api_progress():
    session_id, _ = _get_or_create_session()
    body = request.get_json(force=True) or {}
    step_id = body.get("step_id")
    completed = bool(body.get("completed"))
    if not step_id:
        return jsonify({"error": "step_id is required"}), 400
    db.set_step_progress(session_id, step_id, completed)
    state = db.get_state(session_id)
    return jsonify({"progress": state["progress"]})


@app.route("/api/nudge", methods=["POST"])
def api_nudge():
    session_id, state = _get_or_create_session()
    if not state or not state["selected_path_id"]:
        return jsonify({"error": "No path selected yet."}), 400

    path = next((p for p in state["paths"] if p["id"] == state["selected_path_id"]), None)
    if not path:
        return jsonify({"error": "Selected path not found."}), 404

    done = [s["title"] for s in path["learningPath"] if s["id"] in state["progress"]]
    remaining = [s["title"] for s in path["learningPath"] if s["id"] not in state["progress"]]

    try:
        text = generate_nudge(path["role"], done, remaining)
    except LLMConfigError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": f"Couldn't get a nudge: {e}"}), 502

    return jsonify({"text": text})


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=debug)
