# Autoblog System

A fully functional, 100% free automated blogging system that finds trending topics, writes SEO-optimized articles using the Groq API (Llama 3), and posts them natively to a WordPress website.

## Project Structure

*   `config.py`: Central store for your credentials and WordPress categories.
*   `trends.py`: Connects to Google Trends via a public RSS feed to dynamically get top keywords.
*   `generator.py`: Connects to Groq's high-speed API to prompt Llama 3 to write an SEO-optimized HTML article avoiding generic fluff.
*   `publisher.py`: Connects to the WordPress REST API to post the articles.
*   `main.py`: The orchestrator that ties it all together and schedules runs at 08:00, 14:00, and 20:00 every day.

## How to Run the Bot Locally

1.  Open your command prompt or terminal.
2.  Navigate to the `C:\Users\ADMIN\.gemini\antigravity\scratch\autoblog_system` folder.
3.  Activate the virtual environment:
    ```powershell
    .\venv\Scripts\activate
    ```
4.  Run the bot:
    ```powershell
    python main.py
    ```

The bot will execute a single post immediately upon starting to confirm it works, and will then run continuously in the background, firing again at 8AM, 2PM, and 8PM daily.

## Running in the Background (Deployment)

If you want this to run forever without keeping the terminal window open, you have a couple options on Windows:

### Option 1: PM2 (Node.js Process Manager)
If you have Node.js installed, `pm2` is excellent.
1. `npm install -g pm2`
2. `pm2 start main.py --interpreter .\venv\Scripts\python.exe --name "autoblog"`

### Option 2: Windows Task Scheduler
Instead of relying on the `schedule` python package to run 24/7, you can strip the `start_scheduler()` loop out of `main.py` and write a `.bat` file that simply calls `python main.py`. Then point Windows Task Scheduler to run that `.bat` script 3 times a day.

## SEO Optimization Strategy Implemented
*   **No H1s in Content**: The bot avoids H1s in the article body (which is an SEO penalty risk since themes use H1 for the overall title).
*   **Readable Paragraphs**: Enforces small paragraphs (2-3 sentences).
*   **FAQs Included**: Schema-friendly FAQ sections are generated at the end.
*   **Long-form Content**: Promoted to push for high word-count, high-value topical depth.
*   **Dynamic Trend Hunting**: Guarantees we are posting to topics with high search volume (Google Trends).
