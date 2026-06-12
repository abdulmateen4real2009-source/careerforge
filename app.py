from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from pdf.generator import generate_pdf
from dotenv import load_dotenv
from openai import OpenAI
import os
import uuid

# =========================
# ENV + AI SETUP
# =========================
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# APP INIT
# =========================
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# DATABASE MODEL
# =========================
class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)

    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    location = db.Column(db.String(100))

    bio = db.Column(db.Text)
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    projects = db.Column(db.Text)

    github = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))


# =========================
# LANDING PAGE
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# CREATE CV
# =========================
@app.route("/create", methods=["POST"])
def create_resume():

    username = request.form["username"].lower().strip()

    # ensure unique username fallback
    existing = Resume.query.filter_by(username=username).first()
    if existing:
        username = f"{username}-{str(uuid.uuid4())[:4]}"

    resume = Resume(
        username=username,
        full_name=request.form["full_name"],
        email=request.form["email"],
        phone=request.form["phone"],
        location=request.form["location"],
        bio=request.form["bio"],
        education=request.form["education"],
        skills=request.form["skills"],
        projects=request.form["projects"],
        github=request.form["github"],
        linkedin=request.form["linkedin"]
    )

    db.session.add(resume)
    db.session.commit()

    return redirect(url_for("preview", resume_id=resume.id))


# =========================
# PREVIEW PAGE
# =========================
@app.route("/preview/<int:resume_id>")
def preview(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    return render_template("preview.html", resume=resume)

@app.route("/live-preview")
def live_preview():
    return render_template("live.html")

@app.route("/ai/live-assist", methods=["POST"])
def ai_live_assist():

    text = request.form.get("text", "")
    section = request.form.get("section", "cv")

    prompt = f"""
You are an expert CV assistant.

Analyze and improve this CV section: {section}

Rules:
- Give short actionable suggestions
- Improve clarity
- Add missing skills or achievements
- Be concise

CV CONTENT:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior career coach and CV expert."},
            {"role": "user", "content": prompt}
        ]
    )

    return {"result": response.choices[0].message.content}


# =========================
# PUBLIC PORTFOLIO (SaaS CORE)
# =========================
@app.route("/@<username>")
def portfolio(username):
    resume = Resume.query.filter_by(username=username).first_or_404()
    return render_template("portfolio.html", resume=resume)


# =========================
# PDF DOWNLOAD
# =========================
@app.route("/download/<int:resume_id>")
def download_pdf(resume_id):

    resume = Resume.query.get_or_404(resume_id)

    filename = f"resume_{resume.id}_{uuid.uuid4().hex[:6]}.pdf"
    filepath = os.path.join("static", filename)

    generate_pdf(resume, filepath)

    return redirect(f"/static/{filename}")


# =========================
# 🤖 AI BOOSTER (REAL SaaS ENGINE)
# =========================
@app.route("/ai/boost", methods=["POST"])
def ai_boost():

    mode = request.form.get("mode")  # improve | job | feedback
    text = request.form.get("text", "")
    job = request.form.get("job", "")

    # -------------------------
    # MODE 1: IMPROVE CV
    # -------------------------
    if mode == "improve":

        prompt = f"""
You are a professional CV writer.

Improve this CV to be clear, modern, and ATS-friendly:

{text}
"""

    # -------------------------
    # MODE 2: JOB TAILORING
    # -------------------------
    elif mode == "job":

        prompt = f"""
You are a recruiter.

Rewrite this CV to match the job description.

JOB DESCRIPTION:
{job}

CV:
{text}

Focus on keywords, relevance, and structure.
"""

    # -------------------------
    # MODE 3: RECRUITER FEEDBACK
    # -------------------------
    elif mode == "feedback":

        prompt = f"""
You are a senior recruiter.

Analyze this CV and provide:
- Score out of 10
- Strengths
- Weaknesses
- Improvements

CV:
{text}
"""

    else:
        return {"error": "Invalid mode"}

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a world-class CV expert and career coach."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return {"result": response.choices[0].message.content}


# =========================
# INIT DATABASE
# =========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)