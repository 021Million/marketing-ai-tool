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
SYSTEM_PROMPT = """[Exact same SYSTEM_PROMPT from main.py - omitted here for brevity, copy from original]"""

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


