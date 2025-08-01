import json
import re
from collections import Counter

# Load job descriptions
data = json.load(open('data_with_desc.json', encoding='utf-8'))

# Define a list of common skills to look for (expand as needed)
skill_keywords = [
    'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'sql', 'excel', 'powerpoint', 'word',
    'project management', 'communication', 'leadership', 'teamwork', 'problem solving', 'analytical',
    'customer service', 'sales', 'negotiation', 'presentation', 'coaching', 'training', 'compliance',
    'risk', 'audit', 'marketing', 'design', 'digital marketing', 'branding', 'content creation',
    'data analysis', 'machine learning', 'ai', 'cloud', 'aws', 'azure', 'google cloud',
    'linux', 'windows', 'macos', 'networking', 'security', 'sql', 'nosql', 'database',
    'html', 'css', 'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring',
    'jira', 'confluence', 'sap', 'oracle', 'crm', 'erp', 'agile', 'scrum', 'kanban',
    'coaching', 'mentoring', 'training', 'documentation', 'reporting', 'presentation',
    'negotiation', 'stakeholder management', 'budgeting', 'forecasting', 'planning',
    'microsoft office', 'adobe', 'photoshop', 'illustrator', 'video production',
    'e-learning', 'instructional design', 'facilitation', 'customer focus', 'compliance',
    'regulatory', 'legal', 'finance', 'accounting', 'logistics', 'supply chain', 'aviation',
    'maintenance', 'engineering', 'mechanical', 'electrical', 'civil', 'qa', 'qc', 'quality assurance',
    'testing', 'automation', 'scripting', 'bash', 'powershell', 'shell', 'docker', 'kubernetes',
    'devops', 'ci/cd', 'git', 'version control', 'api', 'rest', 'graphql', 'integration',
    'business development', 'strategy', 'operations', 'hr', 'recruitment', 'talent acquisition',
    'training', 'onboarding', 'employee engagement', 'performance management', 'coaching',
    'presentation', 'public speaking', 'writing', 'editing', 'proofreading', 'translation',
    'multilingual', 'bilingual', 'fluent english', 'arabic', 'french', 'german', 'spanish',
]

# Lowercase and deduplicate skill keywords
skill_keywords = sorted(set([s.lower() for s in skill_keywords]))

# Count skills in all job descriptions
skill_counter = Counter()
total_jobs = 0
for job in data:
    desc = job.get('Job Description', '')
    if not desc:
        continue
    total_jobs += 1
    desc_lower = desc.lower()
    for skill in skill_keywords:
        # Use word boundaries for single-word skills
        if ' ' in skill:
            found = skill in desc_lower
        else:
            found = re.search(r'\b' + re.escape(skill) + r'\b', desc_lower)
        if found:
            skill_counter[skill] += 1

# Calculate percentages
results = []
for skill, count in skill_counter.most_common():
    percent = (count / total_jobs) * 100 if total_jobs else 0
    results.append({
        'skill': skill,
        'count': count,
        'percent': round(percent, 2)
    })

# Print professional analysis

print("Skill Trends Analysis (Top 20):\n")
for r in results:
    print(f"{r['skill'].title():30} {r['count']:3} jobs  ({r['percent']:5.1f}%)")

print(f"\nTotal jobs analyzed: {total_jobs}")

# --- EXTRA ANALYSIS: Discover trending keywords not in skills list ---
import string
all_skill_words = set()
for skill in skill_keywords:
    all_skill_words.update(skill.split())

word_counter = Counter()
for job in data:
    desc = job.get('Job Description', '')
    if not desc:
        continue
    # Remove punctuation, split into words
    words = re.findall(r'\b\w+\b', desc.lower())
    for word in words:
        if word not in all_skill_words and len(word) > 2 and not word.isdigit():
            word_counter[word] += 1

# Show top 30 trending words not in skills list
print("\nPotential Trending Keywords (not in skills list, Top 30):\n")
for word, count in word_counter.most_common(200):
    print(f"{word:20} {count:4}")

# Optionally, save to a file
with open('skill_trends.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

with open('trending_keywords.json', 'w', encoding='utf-8') as f:
    json.dump(word_counter.most_common(100), f, ensure_ascii=False, indent=2)
