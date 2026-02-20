#!/usr/bin/env python3
"""
Miss AI – X Growth Architect | Phase 1 CLI Tool (RSS-only)
==========================================================
Generates a full X (Twitter) content package from the most relevant
news in the last 24 hours (AI, startups, SMB, automation), or from
a manual topic you type.


HOW TO RUN:
    1. Install dependencies:
           python3 -m pip install -r requirements.txt

    2. Set your Anthropic API key (required):
           export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxx"

       Get your key at:
           Anthropic → https://console.anthropic.com/

    3. Run interactively:
           python3 main.py

       Or skip the menu by passing a topic directly:
           python3 main.py "OpenAI just released a new model"

OUTPUT:
    A markdown file is saved to ./output/ with a timestamp in the filename.
"""

import os
import sys
import re
from datetime import datetime, timedelta

import anthropic
import feedparser
import requests

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Model to use. claude-sonnet-4-6 gives the best quality/cost balance.
MODEL = "claude-sonnet-4-6"

# Where generated markdown files are saved
OUTPUT_DIR = "output"

# RSS feeds to watch (AI, startups, SMB, automation)
NEWS_RSS_FEEDS = [
    # AI / tech / startups / finance / crypto
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
    "https://decrypt.co/feed",
    "https://finance.yahoo.com/news/rssindex",
    "https://feeds.finance.yahoo.com/rss/2.0/headline",
    "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",

    # Small business / SMB
    "https://feeds.feedburner.com/SmallBusinessTrends",
    "https://smallbusinessbonfire.com/feed",
]

# Maximum articles to keep from the last 24 hours
MAX_ITEMS = 60

# ─────────────────────────────────────────────────────────────────────────────
# PROMPT (Miss AI brand voice + news-anchored content)
# ─────────────────────────────────────────────────────────────────────────────

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

# ─────────────────────────────────────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def show_menu() -> str:
    """
    Simple mode-selection menu.
    """
    print("\nMiss AI – X Growth Architect")
    print("─" * 52)
    print("[1] Latest: mixed news (AI, startups, SMB, automation)")
    print("[0] Type a topic manually")
    print("─" * 52)
    return input("Choice: ").strip()


def _fetch_one_feed(url: str, max_items: int) -> list:
    """
    Fetch a single RSS/Atom feed and return up to max_items article dicts.

    Each dict:
      title, summary, link, published_dt (datetime), source_url
    """
    try:
        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; MissAI-RSS/1.0)"},
        )
        resp.raise_for_status()
        parsed = feedparser.parse(resp.content)
    except Exception:
        return []

    articles = []
    for entry in parsed.entries[:max_items]:
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

        articles.append(
            {
                "title": title,
                "summary": summary,
                "link": link,
                "published": published_dt,
                "source_url": url,
            }
        )

    return articles


def fetch_all_news_items(hours: int = 24, max_items: int = MAX_ITEMS) -> list:
    """
    Fetch news items from all NEWS_RSS_FEEDS in the last `hours`.
    Returns a list of dicts: {title, summary, link, published}.
    """
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    all_items = []

    print(f"\nFetching news from {len(NEWS_RSS_FEEDS)} RSS feeds (last {hours} hours)...")

    for url in NEWS_RSS_FEEDS:
        items = _fetch_one_feed(url, max_items=10)
        count_before = len(all_items)
        for item in items:
            if item["published"] >= cutoff:
                all_items.append(item)
        count_after = len(all_items)
        added = count_after - count_before
        print(f"  {url[:50]}... → {added} recent items")

    if not all_items:
        return []

    all_items.sort(key=lambda x: x["published"], reverse=True)
    return all_items[:max_items]


def generate_content(news_bundle: str) -> str:
    """
    Send the combined news bundle to Claude and get the content package.
    `news_bundle` is a text list of news items from the last 24h and optionally a daily lesson.
    """
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

    print("\nGenerating content from news bundle...")
    print("Calling Claude API — this takes about 15–30 seconds...\n")

    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    return message.content[0].text


def save_to_markdown(context_title: str, content: str) -> str:
    """
    Write the generated content to a timestamped markdown file in OUTPUT_DIR.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    safe_topic = "".join(c if c.isalnum() or c in " -_" else "" for c in context_title)
    safe_topic = safe_topic[:40].strip().replace(" ", "_") or "News"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{OUTPUT_DIR}/{timestamp}_{safe_topic}.md"

    header = (
        f"# Miss AI – Content Package\n\n"
        f"**Context:** {context_title}  \n"
        f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')}\n\n"
        f"---\n\n"
    )

    with open(filename, "w") as f:
        f.write(header + content)

    return filename

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # API key check
    if not ANTHROPIC_API_KEY:
        print("\nERROR: No Anthropic API key found.")
        print("Set it with:  export ANTHROPIC_API_KEY='sk-ant-...'")
        print("Or paste it directly into main.py in the CONFIGURATION section.")
        print("Get your key at: https://console.anthropic.com/\n")
        sys.exit(1)

    # CLI shortcut: python main.py "some topic"
    if len(sys.argv) > 1:
        manual_topic = " ".join(sys.argv[1:]).strip()
        if not manual_topic:
            print("No topic provided. Exiting.")
            sys.exit(1)
        news_bundle = manual_topic
        context_title = manual_topic[:80]

    else:
        choice = show_menu()

        if choice == "0":
            print("\nMiss AI – X Growth Architect")
            print("─" * 44)
            print("Paste a topic, headline, or article summary.")
            print("(The more detail you give, the better the output.)\n")
            manual_topic = input("> ").strip()
            if not manual_topic:
                print("No topic provided. Exiting.")
                sys.exit(1)
            news_bundle = manual_topic
            context_title = manual_topic[:80]

        elif choice == "1":
            items = fetch_all_news_items(hours=24, max_items=MAX_ITEMS)
            if not items:
                print("\nNo recent news items found in the last 24 hours.")
                sys.exit(1)

            print("\nUsing latest mixed news items (showing first 10):")
            for item in items[:10]:
                print(f"- {item['title']} ({item['published']:%Y-%m-%d %H:%M})")
            print()

            # Optional: future daily lesson
            # daily_lesson = input("Optional: type one lesson you learned today (or leave blank): ").strip()

            lines = []
            for item in items:
                lines.append(
                    f"- Title: {item['title']}\n"
                    f"  Summary: {item['summary']}\n"
                    f"  Source Link: {item['link']}"
                )

            news_bundle = "NEWS – LAST 24 HOURS (ALL FEEDS):\n\n" + "\n\n".join(lines)

            # if daily_lesson:
            #     news_bundle += f"\n\nLESSON_I_LEARNED_TODAY:\n{daily_lesson}\n"

            context_title = "News – last 24h"

        else:
            print("Unknown choice. Exiting.")
            sys.exit(1)

    # Generate
    content = generate_content(news_bundle)

    # Save
    output_file = save_to_markdown(context_title, content)

    print(f"Done! Full content package saved to:\n  {output_file}\n")
    print("── PREVIEW (first 600 chars) " + "─" * 40)
    print(content[:600])
    print("\n[...open the file for the full package]")

if __name__ == "__main__":
    main()
