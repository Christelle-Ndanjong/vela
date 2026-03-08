"""
VELA Job Scraper v2
Pulls remote jobs from 6 free sources
30 skill categories
Run locally or via GitHub Actions daily
Output: jobs.json
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

SKILL_MAP = {
    "Customer Service":          ["customer service", "customer support", "support specialist", "help desk", "cx specialist", "customer success"],
    "Virtual Assistant":         ["virtual assistant", "executive assistant", "admin assistant", "administrative assistant", "personal assistant"],
    "Data Analysis":             ["data analyst", "data analysis", "business analyst", "analytics", "sql analyst", "tableau", "power bi", "data scientist"],
    "Prompt Engineering & AI":   ["prompt engineer", "ai specialist", "llm", "generative ai", "ai trainer", "ai ops", "machine learning", "ai engineer"],
    "Social Media Management":   ["social media manager", "social media specialist", "instagram manager", "tiktok", "social media coordinator"],
    "Content Writing":           ["content writer", "copywriter", "technical writer", "blogger", "seo writer", "content strategist"],
    "SEO Specialist":            ["seo specialist", "seo analyst", "search engine optimization", "keyword research", "link building", "seo manager"],
    "Project Management":        ["project manager", "scrum master", "product owner", "program manager", "agile coach", "delivery manager"],
    "UI/UX Design":              ["ui designer", "ux designer", "product designer", "figma", "ui/ux", "interaction designer", "ux researcher"],
    "Email Marketing":           ["email marketing", "email campaign", "klaviyo", "mailchimp", "crm marketing", "email specialist", "lifecycle marketing"],
    "Cybersecurity":             ["cybersecurity", "security analyst", "soc analyst", "infosec", "penetration tester", "security engineer"],
    "Online Tutoring":           ["tutor", "online teacher", "instructor", "educator", "e-learning", "curriculum developer"],
    "Bookkeeping":               ["bookkeeper", "accountant", "accounting", "quickbooks", "xero", "finance assistant", "payroll"],
    "E-Commerce":                ["shopify", "ecommerce", "woocommerce", "amazon seller", "marketplace manager"],
    "HR & Recruitment":          ["recruiter", "hr specialist", "talent acquisition", "human resources", "people ops", "hr coordinator"],
    "Video Editing":             ["video editor", "video production", "videographer", "motion graphics", "premiere pro", "after effects", "youtube editor"],
    "Graphic Design":            ["graphic designer", "visual designer", "brand designer", "adobe illustrator", "photoshop", "logo designer"],
    "Web Development":           ["web developer", "frontend developer", "backend developer", "fullstack", "react developer", "html css", "javascript developer"],
    "WordPress Management":      ["wordpress developer", "wordpress admin", "cms manager", "website manager", "elementor", "wordpress site"],
    "Transcription":             ["transcriptionist", "transcription", "captioning", "subtitles", "audio transcription", "medical transcription"],
    "Translation":               ["translator", "translation", "localization", "interpreter", "french translator", "bilingual", "language specialist"],
    "Sales Development":         ["sales development", "sdr", "business development", "lead generation", "outbound sales", "inside sales", "account executive"],
    "Community Management":      ["community manager", "community moderator", "discord manager", "online community", "community builder", "engagement manager"],
    "Amazon FBA":                ["amazon fba", "fba specialist", "amazon va", "amazon listing", "amazon ppc", "amazon marketplace"],
    "CRM Management":            ["crm specialist", "salesforce admin", "hubspot admin", "crm manager", "zoho crm", "revenue operations"],
    "Paid Ads Management":       ["paid ads", "google ads", "ppc specialist", "media buyer", "performance marketing", "paid social", "sem specialist"],
    "Podcast Production":        ["podcast editor", "podcast producer", "audio editor", "show notes", "podcast manager", "audio production"],
    "Legal Assistant":           ["legal assistant", "paralegal", "legal researcher", "contract review", "legal admin", "law clerk"],
    "Medical VA":                ["medical virtual assistant", "medical admin", "healthcare admin", "medical billing", "medical coding", "telehealth"],
    "Executive Recruiting":      ["executive recruiter", "headhunter", "talent sourcer", "technical recruiter", "recruitment consultant"],
}

def match_skill(title, tags):
    text = (title + " " + " ".join(tags or [])).lower()
    for skill, keywords in SKILL_MAP.items():
        if any(kw in text for kw in keywords):
            return skill
    return None

def fetch_remoteok():
    print("Fetching from RemoteOK...")
    jobs = []
    try:
        req = urllib.request.Request("https://remoteok.com/api", headers={"User-Agent": "VELA Job Platform"})
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode())
            for job in (data[1:] if data else [])[:150]:
                if not isinstance(job, dict): continue
                title = job.get("position", "")
                tags  = job.get("tags", [])
                skill = match_skill(title, tags)
                if not skill: continue
                jobs.append({"id": job.get("id",""), "title": title, "company": job.get("company","Unknown"), "skill": skill, "tags": tags[:5], "url": job.get("url","https://remoteok.com"), "location": "Worldwide", "salary": job.get("salary",""), "posted": job.get("date",""), "logo": job.get("company_logo",""), "source": "RemoteOK", "remote": True})
    except Exception as e:
        print(f"  RemoteOK error: {e}")
    print(f"  → {len(jobs)} jobs")
    return jobs

def fetch_jobicy():
    print("Fetching from Jobicy...")
    jobs = []
    try:
        req = urllib.request.Request("https://jobicy.com/api/v2/remote-jobs?count=100&geo=worldwide", headers={"User-Agent": "VELA Job Platform"})
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode())
            for job in data.get("jobs", []):
                title = job.get("jobTitle", "")
                tags  = job.get("jobIndustry", [])
                if isinstance(tags, str): tags = [tags]
                skill = match_skill(title, tags)
                if not skill: continue
                jobs.append({"id": str(job.get("id","")), "title": title, "company": job.get("companyName","Unknown"), "skill": skill, "tags": tags[:5], "url": job.get("url","https://jobicy.com"), "location": "Worldwide", "salary": str(job.get("annualSalaryMin","")), "posted": job.get("pubDate",""), "logo": job.get("companyLogo",""), "source": "Jobicy", "remote": True})
    except Exception as e:
        print(f"  Jobicy error: {e}")
    print(f"  → {len(jobs)} jobs")
    return jobs

def fetch_remotive():
    print("Fetching from Remotive...")
    jobs = []
    try:
        req = urllib.request.Request("https://remotive.com/api/remote-jobs?limit=150", headers={"User-Agent": "VELA Job Platform"})
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode())
            for job in data.get("jobs", []):
                title = job.get("title", "")
                tags  = job.get("tags", [])
                skill = match_skill(title, tags)
                if not skill: continue
                jobs.append({"id": str(job.get("id","")), "title": title, "company": job.get("company_name","Unknown"), "skill": skill, "tags": tags[:5], "url": job.get("url","https://remotive.com"), "location": job.get("candidate_required_location","Worldwide"), "salary": job.get("salary",""), "posted": job.get("publication_date",""), "logo": job.get("company_logo",""), "source": "Remotive", "remote": True})
    except Exception as e:
        print(f"  Remotive error: {e}")
    print(f"  → {len(jobs)} jobs")
    return jobs

def fetch_himalayas():
    print("Fetching from Himalayas...")
    jobs = []
    try:
        req = urllib.request.Request("https://himalayas.app/jobs/api?limit=100", headers={"User-Agent": "VELA Job Platform"})
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode())
            for job in data.get("jobs", []):
                title = job.get("title", "")
                tags  = job.get("categories", [])
                if isinstance(tags, str): tags = [tags]
                skill = match_skill(title, tags)
                if not skill: continue
                company = job.get("company", {})
                company_name = company.get("name", "Unknown") if isinstance(company, dict) else str(company)
                company_logo = company.get("logo", "") if isinstance(company, dict) else ""
                jobs.append({"id": str(job.get("slug","")), "title": title, "company": company_name, "skill": skill, "tags": tags[:5], "url": job.get("applicationLink","https://himalayas.app/jobs"), "location": "Worldwide", "salary": "", "posted": job.get("createdAt",""), "logo": company_logo, "source": "Himalayas", "remote": True})
    except Exception as e:
        print(f"  Himalayas error: {e}")
    print(f"  → {len(jobs)} jobs")
    return jobs

def fetch_arbeitnow():
    print("Fetching from Arbeitnow...")
    jobs = []
    try:
        req = urllib.request.Request("https://www.arbeitnow.com/api/job-board-api", headers={"User-Agent": "VELA Job Platform"})
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode())
            for job in data.get("data", [])[:100]:
                if not job.get("remote", False): continue
                title = job.get("title", "")
                tags  = job.get("tags", [])
                skill = match_skill(title, tags)
                if not skill: continue
                jobs.append({"id": str(job.get("slug","")), "title": title, "company": job.get("company_name","Unknown"), "skill": skill, "tags": tags[:5], "url": job.get("url","https://arbeitnow.com"), "location": "Worldwide", "salary": "", "posted": str(job.get("created_at","")), "logo": "", "source": "Arbeitnow", "remote": True})
    except Exception as e:
        print(f"  Arbeitnow error: {e}")
    print(f"  → {len(jobs)} jobs")
    return jobs

def detect_type(title):
    """Detect if job is internship, volunteer, or regular job"""
    title_lower = title.lower()
    if any(w in title_lower for w in ["intern", "internship", "trainee", "apprentice"]):
        return "internship"
    if any(w in title_lower for w in ["volunteer", "volunteering", "pro bono"]):
        return "volunteer"
    return "job"

def deduplicate(jobs):
    seen = set()
    unique = []
    for job in jobs:
        key = (job["title"].lower().strip(), job["company"].lower().strip())
        if key not in seen:
            seen.add(key)
            unique.append(job)
    return unique

def save(jobs):
    skill_counts = {}
    for job in jobs:
        s = job["skill"]
        skill_counts[s] = skill_counts.get(s, 0) + 1
    # Tag job types
    for job in jobs:
        if "type" not in job:
            job["type"] = detect_type(job.get("title",""))
    output = {"updated": datetime.now(timezone.utc).isoformat(), "total": len(jobs), "skill_counts": skill_counts, "jobs": jobs}
    with open("jobs.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n✅ Saved {len(jobs)} jobs to jobs.json")
    print("\n📊 Jobs by skill:")
    for skill, count in sorted(skill_counts.items(), key=lambda x: -x[1]):
        print(f"   {skill}: {count}")

def main():
    print("🌍 VELA Job Scraper v2 Starting...\n")
    all_jobs = []
    all_jobs.extend(fetch_remoteok())
    all_jobs.extend(fetch_jobicy())
    all_jobs.extend(fetch_remotive())
    all_jobs.extend(fetch_himalayas())
    all_jobs.extend(fetch_arbeitnow())
    print(f"\n📥 Total raw: {len(all_jobs)}")
    unique = deduplicate(all_jobs)
    print(f"📊 After dedup: {len(unique)} jobs")
    unique.sort(key=lambda x: x.get("posted", ""), reverse=True)
    save(unique)
    print("\n🚀 Done. Upload jobs.json to GitHub to update the live board.")

if __name__ == "__main__":
    main()
