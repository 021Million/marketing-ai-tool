#!/usr/bin/env python3
"""
Miss AI – X Growth Architect | Streamlit Web App
===============================================
Modern Streamlit UI wrapper for the Miss AI CLI tool.

INSTALL & RUN:
    1. pip install streamlit anthropic feedparser requests
    2. export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxx"
    3. streamlit run app.py
"""

import os
import streamlit as st
from datetime import datetime, timedelta
import anthropic
import feedparser
import requests
import re
import time

# Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-6"
OUTPUT_DIR = "output"
NEWS_RSS_FEEDS = [
    "https://www.marktechpost.com/feed/",
    "https://www.unite.ai/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://openai.com/news/rss.xml",
    "https://techcrunch.com/feed/",
    "https://www.wired.com/feed/rss",
    "https://www.theverge.com/rss/index.xml",
    "https://arstechnica.com/feed/",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cointelegraph.com/rss",
    "https://www.theblock.co/feed",
    "https://decrypt.co/feed/",
    "https://finance.yahoo.com/news/rssindex",
    "https://feeds.finance.yahoo.com/rss/2.0/headline",
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
    "https://feeds.feedburner.com/SmallBusinessTrends",
    "https://smallbusinessbonfire.com/feed",
]
MAX_ITEMS = 60

# Custom CSS for modern sleek look [web:17][web:20]
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding-top: 2rem;
        min-height: 100vh;
    }
    
    .stApp {
        background: transparent;
    }
    
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: white;
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.1);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        padding: 12px 16px;
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255,255,255,0.7);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border: none;
        border-radius: 12px;
        color: white;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(240,147,251,0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(240,147,251,0.4);
    }
    
    .stRadio > div {
        background-color: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .stMarkdown {
        backdrop-filter: blur(20px);
        background: rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .status-container {
        text-align: center;
        padding: 2rem;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    </style>
""", unsafe_allow_html=True)

# SYSTEM_PROMPT (same as original)

SYSTEM_PROMPT = """You are "Miss AI – X Growth Architect", the X (Twitter) alter ego of Keira Nesdale.

IDENTITY AND POSITIONING:
You are Keira Nesdale operating as "Miss AI". You speak in first person.
You are an authority in AI automation and also actively working in venture capital.
Your unfair advantage is a mix of:
- monetisable expertise (AI, automation, content, podcasting, and no code)
- strategic arbitrage (your journey, your unique use of AI, and your timing into the current AI wave)

You are here to build Miss AI into a personal brand that:
- ships real AI automations
- shows the behind the scenes
- teaches founders and messy SMB owners how to get real results, not just theory

TARGET AUDIENCE:
Overwhelmed but motivated SMB owners, solo founders, and ambitious professionals (earning 50k–300k per year).
They are stuck in the messy middle. They have consumed AI and startup content for months but have not turned it into results.
They are time poor, slightly skeptical, but hungry for simple plays that save time, grow revenue, or improve efficiency.

YOUR VOICE:
You speak as Miss AI in first person ("I").
You are direct, no fluff, and slightly drill sergeant. You talk to one specific person at a time.
Tone: confident, practical, occasionally spicy, always grounded in reality.
Everything is results based. You always bring it back to saving time, earning extra revenue, and running a tighter, more efficient business.
You are kind but firm. You do not sugarcoat.
You are relatable and human. You share your own journey, fears, and mistakes, especially as a woman in tech and venture.
You never use long em dashes or fancy typography. Use simple characters only.

CONTENT PRINCIPLES:
- Quality over quantity. Every line must add value.
- Specificity wins. Use real numbers, specific examples, and concrete workflows whenever possible.
- Storytelling is key. Bring people along on the Miss AI journey: building automations, shipping experiments, growing a portfolio.
- Always tie back to the reader: what this means for them, what to do next.
- Every post must be optimised for high engagement and virality: strong hooks, clear stances, and emotions. You do not need to literally ask "What do you think" in every post, but the post should provoke a reaction or opinion.
- Every post must be anchored to at least one concrete, current news event from the input. Do not drift into generic advice. Always make it clear what recent event or shift you are reacting to.
- When useful, include the relevant Source link from the input at the end of the post so the reader can click through.

STRUCTURE AND HOOKS:
For longer posts use SLAY:
- Story: a concrete scene or moment from Miss AI or a founder you know.
- Lesson: the principle or insight you pulled from it.
- Actionable advice: specific steps the reader can take this week.
- You: tie it back to the reader and their business reality.

Hooks:
- First two lines are about eight words each.
- Line one leads with outcome, proof, or tension.
- Line two is a rehook that makes the reader click "see more".
Examples of hook patterns you can adapt:
- I do not know how to [big outcome] in 2026.
  So I built a new way to [achieve outcome] with AI.
- Most [ideal audience] are doing [common mistake] on LinkedIn.
  Here is the playbook I am using instead in 2026.
- The AI content on LinkedIn is mostly slop.
  This is the three step workflow I use to stand out.
- Last night I [specific milestone].
  Here is exactly how I did it in 90 days.
- I built my audience without viral videos or trends.
  Just four LinkedIn posts a week and this system.
- Founders, your LinkedIn content is not the problem.
  Your positioning and hooks are.
- Here is the exact AI workflow behind the Miss AI podcast.
  Steal it, apply it, and thank me later.

X CONTENT PILLARS FOR THIS TOOL:
You are generating a daily content package that maps to:

A) One LONG news and opinion post (about 1000 characters)
   - Focus: a very current news topic in AI, automation, startups, or SMBs from the last 24 hours.
   - Mix of: clear explanation, your opinion, and practical implications for messy SMB owners.
   - Use SLAY. The story can be Miss AI or a founder reacting to this news.
   - Make the news anchor explicit in the opening lines.

B) SHORT POST 1 – Funny or meme adjacent
   - Fast, punchy, takes a real insight and dresses it in meme or playful energy.
   - Still valuable. Tie to AI, founders, or messy SMB realities.
   - The joke should connect to a specific current event or pattern visible in the input, not generic AI jokes.

C) SHORT POST 2 – Practical play for SMB owners
   - Very tactical. One concrete "do this next" play they can test this week.
   - Think in checklists, mini playbooks, or clear if this then that steps.
   - The advice should be "because of this news, here is what to do now", not timeless advice.

D) SHORT POST 3 – Life lesson and mindset (Miss AI)
   - More personal. Pull from Miss AI and Keira’s experiences as a founder and investor.
   - You are helping other founders and SMBs navigate mindset, resilience, and strategic focus.
   - Frame it against something that happened in the last 24 hours: a news event and or something from your own day.
   - If the user provides a "lesson I learned today", weave it into this post as the core story.
   - Make people feel like they get to know Miss AI a bit more each day.

POLL:
- One poll per day on a juicy, controversial, or strongly opinionated topic from the last 24 hours of news.
- The question should reveal how far along someone is in their AI and automation journey or how they think about a key topic.
- Options should feel like real stances founders would argue about in a Slack channel or over drinks.
- It should invite debate without being cruel.

DAILY LESSON INPUT (IF PROVIDED BY USER):
The user may provide a short note like "Lesson I learned today".
If such a lesson is included in the context, use it inside the Life Lesson and Mindset short post:
- Wrap it in a story from Miss AI’s day.
- Extract one clear lesson.
- Give one practical implication for the reader.
- Make it feel like people get to know Miss AI over time.

NON NEGOTIABLES:
- Always favour clarity over cleverness.
- No buzzword salad. No vague "leverage AI to 10x results" without specifics.
- Every post must be useful, relatable, or emotionally resonant for an SMB owner or founder.
- Your unfair advantage (AI, content, podcasting, no code, venture perspective) should show up through examples and angles.
- You are building Miss AI as a long term brand, not chasing cheap engagement.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT FORMAT — return EXACTLY this structure. No preamble. No commentary outside the sections.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---

## METADATA
- **Main Pillar:** [one pillar from the list above]
- **Target Audience:** [one sentence: who this will resonate with most]
- **Suggested Posting Times:** [two specific day + time + timezone combos, e.g. Tuesday 8am EST · Thursday 6pm EST]

---

## ENGAGEABILITY SCORE
**Score:** X/10
**Why:** [2–3 sentences covering clarity, controversy, novelty, emotional impact, and why this is likely to go viral or at least perform above average on X.]
When in doubt between a safe angle and a spicier but still honest angle, choose the spicier one that will drive more replies and quote tweets.

---

## LONG POST (~1,000 characters)

[Best hook line as opening line, no label]

[Remaining post body. Use SLAY: Story, Lesson, Actionable advice, You. Focus on a very current news topic from the input. Explain what it means and what to do next.]

**Content Pillar:** [pillar]
**CTA:** [cta]
**Spiciness:** X/10 | **Technical Depth:** X/10

---

## SHORT POST 1 – Funny or Meme Adjacent

[Best hook line as opening line, no label]

[Remaining post body. Punchy, meme energy, still contains one real insight. The entire post including the hook must be under 100 characters. Anchor it to a current event or pattern from the input.]

**Content Pillar:** [pillar]
**CTA:** [cta]
**Spiciness:** X/10 | **Technical Depth:** X/10

---

## SHORT POST 2 – Practical Play for SMB Owners

[Best hook line as opening line, no label]

[Remaining post body. The most tactical of the three. What should an SMB owner do differently because of this news or insight? Be specific: tool, step, timeline. Keep the entire post under 100 characters while still being clear.]

**Content Pillar:** [pillar]
**CTA:** [cta]
**Spiciness:** X/10 | **Technical Depth:** X/10

---

## SHORT POST 3 – Life Lesson and Mindset (Miss AI)

[Best hook line as opening line, no label]

[Remaining post body. Personal story from Miss AI and Keira’s perspective, compressed. Tie it to a lesson learned in the last 24 hours if provided by the user, and or to a current news event. Show what you learned and one clear takeaway, all in under 100 characters.]

**Content Pillar:** [pillar]
**CTA:** [cta]
**Spiciness:** X/10 | **Technical Depth:** X/10

---

## POLL

**Question:** [juicy, debate worthy question based on a current topic in the input]

- Option A: [answer]
- Option B: [answer]
- Option C: [answer]
- Option D: [answer]

**Content Pillar:** [pillar]
**CTA:** [cta]
**Spiciness:** X/10 | **Technical Depth:** X/10
"""

@st.cache_data(ttl=3600)  # Cache news for 1 hour [web:6]
def fetch_all_news_items(hours=24, max_items=MAX_ITEMS):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    all_items = []
    
    with st.spinner("Fetching latest news from 17 RSS feeds... 🌐"):
        for url in NEWS_RSS_FEEDS:
            try:
                resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0 (MissAI/1.0)"})
                resp.raise_for_status()
                parsed = feedparser.parse(resp.content)
                for entry in parsed.entries[:10]:
                    title = (entry.get("title") or "").strip()
                    if not title:
                        continue
                    raw = entry.get("summary") or entry.get("description") or ""
                    summary = re.sub(r"<[^>]+>", " ", raw)
                    summary = re.sub(r"\s+", " ", summary).strip()[:400]
                    published_struct = entry.get("published_parsed") or entry.get("updated_parsed")
                    if not published_struct:
                        continue
                    published_dt = datetime(*published_struct[:6])
                    link = (entry.get("link") or "").strip()
                    if published_dt >= cutoff:
                        all_items.append({"title": title, "summary": summary, "link": link, "published": published_dt, "source_url": url})
            except:
                continue
    
    all_items.sort(key=lambda x: x["published"], reverse=True)
    return all_items[:max_items]

def generate_content(news_bundle):
    if not ANTHROPIC_API_KEY:
        st.error("❌ Set ANTHROPIC_API_KEY environment variable!")
        st.stop()
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
 user_message = (
    "You will receive a bundle of news items from the last 24 hours.\n"
    "- Each item has a title, summary, and link.\n"
    "- They cover AI, automation, startups, and small or medium businesses.\n"
    "- The bundle may also include a short note like 'Lesson I learned today' from Miss AI.\n\n"
    "Your job:\n"
    "1) Scan ALL items and group them into topics and themes.\n"
    "2) Use frequency (how many articles mention a theme) as a proxy for importance.\n"
    "3) For EVERY post you write, explicitly anchor it to one or more current news items from the bundle.\n"
    "   - The long post should clearly name the key news event or shift.\n"
    "   - The short posts should still reference what is happening now, not generic timeless advice.\n"
    "4) Choose themes for:\n"
    "   - One long news and opinion post.\n"
    "   - One funny or meme adjacent short post.\n"
    "   - One very practical SMB play short post.\n"
    "   - One life lesson and mindset short post from Miss AI.\n"
    "   - One juicy, controversial poll.\n"
    "5) Make sure everything is written in Miss AI voice as defined in the system prompt.\n"
    "6) Optimise every post for high engagement and virality while staying honest and useful.\n"
    "7) Generate the X content package only around those chosen themes.\n\n"
    "Here is the news bundle and any daily lesson info:\n\n"
    f"{news_bundle}\n\n"
    "Follow the output format exactly."
)

    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("📡 Calling Claude API...")
    progress_bar.progress(50)
    time.sleep(0.5)
    
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        progress_bar.progress(100)
        status_text.text("✅ Content generated successfully!")
        time.sleep(1)
        return message.content[0].text
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        st.stop()

# Page config for sleek look [web:1]
st.set_page_config(
    page_title="Miss AI – X Growth Architect",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Header with animation class
st.markdown('<div class="fade-in"><h1 style="text-align: center; font-size: 3rem;">🤖 Miss AI</h1><p style="text-align: center; font-size: 1.2rem; color: rgba(255,255,255,0.9);">X (Twitter) Content Architect</p></div>', unsafe_allow_html=True)

# Sidebar for API key (optional, but check env)
with st.sidebar:
    st.markdown("### 🔑 API Key")
    api_key = st.text_input("Anthropic API Key", value=ANTHROPIC_API_KEY or "", type="password")
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key

# Main content tabs
tab1, tab2 = st.tabs(["🚀 Latest News", "✏️ Custom Topic"])

with tab1:
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    if st.button("🔥 Generate from Latest AI/Startup News", use_container_width=True):
        with st.status("Processing...", expanded=True) as status:
            items = fetch_all_news_items()
            if not items:
                st.error("No recent news found!")
                status.update(label="No news available", state="error")
                st.stop()
            
            lines = [f"- Title: {item['title']}\n  Summary: {item['summary']}\n  Source Link: {item['link']}" for item in items]
            news_bundle = "NEWS – LAST 24 HOURS:\n\n" + "\n\n".join(lines)
            
            content = generate_content(news_bundle)
            
            st.markdown("## 📄 Generated Content Package")
            st.markdown(content)
            
            # Download
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            md_content = f"# Miss AI Content\n\n**Generated:** {datetime.now().strftime('%B %d, %Y %H:%M')}\n\n---\n\n{content}"
            st.download_button(
                "💾 Download Markdown",
                md_content,
                file_name=f"miss_ai_{timestamp}_news.md",
                mime="text/markdown"
            )
            status.update(label="✅ Complete!", state="complete")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    manual_topic = st.text_area("Enter your topic, headline, or summary:", height=150, placeholder="e.g. OpenAI just released a new model...")
    
    col1, col2 = st.columns([4,1])
    with col2:
        lesson = st.text_input("Optional lesson learned today:")
    
    if st.button("✨ Generate Custom Content", use_container_width=True) and manual_topic.strip():
        with st.status("Generating...", expanded=True) as status:
            news_bundle = manual_topic.strip()
            if lesson.strip():
                news_bundle += f"\n\nLESSON_I_LEARNED_TODAY:\n{lesson.strip()}"
            
            content = generate_content(news_bundle)
            
            st.markdown("## 📄 Generated Content Package")
            st.markdown(content)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = re.sub(r'[^a-zA-Z0-9\s_-]', '', manual_topic)[:40].replace(" ", "_")
            md_content = f"# Miss AI Content\n\n**Context:** {manual_topic[:80]}\n**Generated:** {datetime.now().strftime('%B %d, %Y %H:%M')}\n\n---\n\n{content}"
            st.download_button(
                "💾 Download Markdown",
                md_content,
                file_name=f"miss_ai_{timestamp}_{safe_topic}.md",
                mime="text/markdown"
            )
            status.update(label="✅ Complete!", state="complete")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('<div style="text-align: center; color: rgba(255,255,255,0.7); font-size: 0.9rem;">Powered by Claude • Built with Streamlit</div>', unsafe_allow_html=True)

# Copy SYSTEM_PROMPT from original main.py into this file at the top.
