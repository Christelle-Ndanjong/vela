"""
VELA Job Scraper
Pulls remote jobs from RemoteOK and Jobicy APIs
Run locally or via GitHub Actions daily
Output: jobs.json
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ─── VELA skill keywords mapped to our 15 skills ───────────────────────────
SKILL_MAP = {
    "Customer Service":       ["customer service", "customer support", "support specialist", "help desk", "cx"],
    "Virtual Assistant":      ["virtual assistant", "executive assistant", "va ", "admin assistant", "administrative"],
    "Data Analysis":          ["data analyst", "data analysis", "business analyst", "analytics", "sql", "tableau", "power bi"],
    "Prompt Engineering & AI":["prompt engineer", "ai specialist", "llm", "generative ai", "ai trainer", "ai ops"],
    "Social Media Management":["social media", "community manager", "instagram", "content creator", "tiktok"],
    "Content Writing":        ["content writer", "copywriter", "technical writer", "blogger", "seo writer"],
    "SEO Specialist":         ["seo", "search engine", "keyword research", "link building", "serp"],
    "Project Management":     ["project manager", "scrum master", "product owner", "program manager", "agile"],
    "UI/UX Design":           ["ui designer", "ux designer", "product designer", "figma", "ui/ux"],
    "Email Marketing":        ["email marketing", "email campaign", "klaviyo", "mailchimp", "crm marketing"],
    "Cybersecurity":          ["cybersecurity", "security analyst", "soc analyst", "infosec", "penetration"],
    "Online Tutoring":        ["tutor", "teacher", "instructor", "educator", "e-learning", "curriculum"],
    "Bookkeeping":            ["bookkeeper", "accountant", "accounting", "quickbooks", "xero", "finance"],
    "E-Commerce":             ["shopify", "e-commerce", "ecommerce", "woocommerce", "amazon seller"],
    "HR & Recruitment":       ["recruiter", "hr specialist", "talent acquisition", "human resources", "people ops"],
}

def match_skill(title, tags):
    """Match a job to a VELA skill category"""
    text = (title + " " + " ".join(tags or [])).lower()
    for skill, keywords in SKILL_MAP.items():
        if any(kw in text for kw in keywords):
            return skill
    return None

def fetch_remoteok():
    """Fetch jobs from RemoteOK API"""
    print("Fetching from RemoteOK...")
    jobs = []
    try:
        req = urllib.request.Request(
            "https://remoteok.com/api",
            headers={"User-Agent": "VELA Job Platform (vela.work)"}
        )
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode())
            # First item is metadata, skip it
            entries = data[1:] if data else []
            for job in entries[:100]:
                if not isinstance(job, dict):
                    continue
                title = job.get("position", "")
                tags  = job.get("tags", [])
                skill = match_skill(title, tags)
                if not skill:
                    continue
                jobs.append({
                    "id":          job.get("id", ""),
                    "title":       title,
                    "company":     job.get("company", "Unknown"),
                    "skill":       skill,
                    "tags":        tags[:5],
                    "url":         job.get("url", "https://remoteok.com"),
                    "location":    "Worldwide",
                    "salary":      job.get("salary", ""),
                    "posted":      job.get("date", ""),
                    "logo":        job.get("company_logo", ""),
                    "source":      "RemoteOK",
                    "remote":      True,
                })
    except Exception as e:
        print(f"RemoteOK error: {e}")
    print(f"  → {len(jobs)} matched jobs from RemoteOK")
    return jobs

def fetch_jobicy():
    """Fetch jobs from Jobicy API"""
    print("Fetching from Jobicy...")
    jobs = []
    try:
        req = urllib.request.Request(
            "https://jobicy.com/api/v2/remote-jobs?count=50&geo=worldwide",
            headers={"User-Agent": "VELA Job Platform (vela.work)"}
        )
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode())
            entries = data.get("jobs", [])
            for job in entries:
                title = job.get("jobTitle", "")
                tags  = job.get("jobIndustry", [])
                if isinstance(tags, str):
                    tags = [tags]
                skill = match_skill(title, tags)
                if not skill:
                    continue
                jobs.append({
                    "id":       str(job.get("id", "")),
                    "title":    title,
                    "company":  job.get("companyName", "Unknown"),
                    "skill":    skill,
                    "tags":     tags[:5],
                    "url":      job.get("url", "https://jobicy.com"),
                    "location": "Worldwide",
                    "salary":   job.get("annualSalaryMin", ""),
                    "posted":   job.get("pubDate", ""),
                    "logo":     job.get("companyLogo", ""),
                    "source":   "Jobicy",
                    "remote":   True,
                })
    except Exception as e:
        print(f"Jobicy error: {e}")
    print(f"  → {len(jobs)} matched jobs from Jobicy")
    return jobs

def fetch_remotive():
    """Fetch jobs from Remotive API"""
    print("Fetching from Remotive...")
    jobs = []
    try:
        req = urllib.request.Request(
            "https://remotive.com/api/remote-jobs?limit=100",
            headers={"User-Agent": "VELA Job Platform (vela.work)"}
        )
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode())
            entries = data.get("jobs", [])
            for job in entries:
                title = job.get("title", "")
                tags  = job.get("tags", [])
                skill = match_skill(title, tags)
                if not skill:
                    continue
                jobs.append({
                    "id":       str(job.get("id", "")),
                    "title":    title,
                    "company":  job.get("company_name", "Unknown"),
                    "skill":    skill,
                    "tags":     tags[:5],
                    "url":      job.get("url", "https://remotive.com"),
                    "location": job.get("candidate_required_location", "Worldwide"),
                    "salary":   job.get("salary", ""),
                    "posted":   job.get("publication_date", ""),
                    "logo":     job.get("company_logo", ""),
                    "source":   "Remotive",
                    "remote":   True,
                })
    except Exception as e:
        print(f"Remotive error: {e}")
    print(f"  → {len(jobs)} matched jobs from Remotive")
    return jobs

def deduplicate(jobs):
    """Remove duplicate jobs by title+company"""
    seen = set()
    unique = []
    for job in jobs:
        key = (job["title"].lower().strip(), job["company"].lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique

def save(jobs):
    """Save jobs to JSON file"""
    output = {
        "updated":    datetime.now(timezone.utc).isoformat(),
        "total":      len(jobs),
        "jobs":       jobs,
    }
    with open("jobs.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n✅ Saved {len(jobs)} jobs to jobs.json")

def main():
    print("🌍 VELA Job Scraper Starting...\n")
    all_jobs = []
    all_jobs.extend(fetch_remoteok())
    all_jobs.extend(fetch_jobicy())
    all_jobs.extend(fetch_remotive())

    # Deduplicate
    unique = deduplicate(all_jobs)
    print(f"\n📊 Total after deduplication: {len(unique)} jobs")

    # Sort newest first
    unique.sort(key=lambda x: x.get("posted", ""), reverse=True)

    save(unique)
    print("\n🚀 Done. Push jobs.json to GitHub to update the live board.")

if __name__ == "__main__":
    main()
