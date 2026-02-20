 ## 2026-02-18
- What I built: First Miss AI X CLI (Command-Line Interface) that generates long + short posts and a poll from a topic. Input a topic, it generates a long form 3 short form and a poll related to the topic
- Biggest challenge: Understanding VS Code terminals are different from Claude Code terminal and setting the Anthropic API key.
- Lesson: Keep Claude Code (code edits) separate from the shell (python commands).
- Next step: Auto-generate AUTO_POST_QUEUE file and plan X posting automation.
- Random notes: Terminals are tied to workspaces. 1 folder for 1 project. API = a window at a resturant to order a specific data . RSS= moving conveyor belt of incoming news and I can pick them up as they appear
- End Goal is to build agent system that can search the internet/reddit and X for trending topics, generate engaging viral content (Inclusive of generating images and videos to match) and optimize posting, be able to post into communities. 

 ## 2026-02-19
 # Miss AI – Build Journey Log  
**Date:** February 19, 2026

## 1. What I actually built

- I got a working **Miss AI CLI tool** that:
  - Pulls live news from ~15 RSS feeds (AI, startups, SMB, finance, crypto).
  - Bundles the last 24 hours of headlines and summaries.
  - Sends that bundle to Claude with a detailed Miss AI system prompt.
  - Generates 1 long SLAY post, 3 short posts, and 1 poll, all anchored to current news.
  - Saves everything into a timestamped markdown file in `/output`.

- I reshaped the tool to be **Miss AI–specific**:
  - First‑person “I” voice as Miss AI / Keira.
  - Positioning as AI automation + venture perspective.
  - Focus on messy SMB owners and founders.
  - Hooks + SLAY + unfair advantage baked into the system prompt.

- I also:
  - Fixed path issues on my Mac and learned how to run Python scripts properly.
  - Installed dependencies via `python3 -m pip install -r requirements.txt`.
  - Understood how `requirements.txt`, RSS feeds, `main.py`, and `SYSTEM_PROMPT` all fit together.

---

## 2. Design decisions I made

- **Phase 1 = RSS only**
  - Chose free RSS feeds over paid APIs or heavy scrapers for now.
  - Moved to one combined “mixed news” mode instead of separate startup/AI/SMB modes.
  - Let Claude decide what is most important based on:
    - How often a topic is mentioned.
    - Relevance to AI, automation, and messy SMB owners.

- **Anchor everything to current events**
  - Decided that every post must be tied to a recent news item.
  - No generic “AI is the future” fluff; everything must say:
    - “Because of this news, here is what it means for you and what to do.”

- **Aspirational but not fake**
  - Asked if the persona felt too advanced.
  - Landed on: it is okay to be slightly ahead of where I feel, as long as:
    - I am actually doing the work.
    - The content is grounded in real news and real plays I would run.

---

## 3. Future plan I defined

- **Miss AI version (internal / my brand)**
  - Keep the current CLI tool as my Miss AI engine.
  - Next steps:
    - Build **n8n automations** to:
      - Trigger the script daily.
      - Grab the output.
      - Post automatically to X (and later other platforms).
    - Add image and video generation later (reels, memes, infographics).

- **Generic version (for others)**
  - Duplicate the project.
  - Strip out Miss AI and Keira references.
  - Let users:
    - Paste their **brand voice**.
    - Choose / configure their **news category** (e.g. NZ real estate).
    - Toggle which outputs they want (long post, shorts, poll).
  - Use it as a neutral engine people can try for free or as a paid product.

- **Front end and UX**
  - Build a simple **Miss AI web front end** so I and my team can use it without Terminal.
  - Likely built with **Streamlit** (Python, quick, hosted via Streamlit Cloud).

---

## 4. Skills and concepts I picked up

- **Technical workflow basics**
  - Navigating folders and fixing path issues.
  - Running `python3 main.py` and installing packages from `requirements.txt`.
  - Using environment variables (`export ANTHROPIC_API_KEY=...`).

- **Architecture thinking**
  - Separating:
    - Data source (RSS).
    - Brain (Claude + system prompt).
    - Scheduler/poster (n8n, future X automations).
  - Designing in stages: Phase 1 (RSS + content), then automation, then web f
