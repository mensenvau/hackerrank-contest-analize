# HackerRank Contest Analyzer

A tool for contest administrators to analyze HackerRank contest submissions. It collects data, organizes code files, detects potential plagiarism using AI (Gemini), and generates a detailed report.

## Features

- **Data Collection**: Fetches leaderboard and all submissions using your admin cookie.
- **Robustness**: Handles rate limiting (429 errors) with smart retries.
- **Organization**:
  - Creates a `results/` folder.
  - Subfolders for each user.
  - Files for each challenge (e.g., `ChallengeName.txt`) containing all submission attempts chronologically.
  - Shows **Max Possible Score** vs **User Score** in each file header.
- **AI Analysis**: Uses **Google Gemini** to analyze code quality and detect cheating probability.
- **Reporting**: Generates a tab-separated text report (`.txt`) compatible with Excel/Sheets, containing:
  - Username
  - Total Score
  - Time Taken
  - Cheating Probability
  - AI Notes & Profile Links

## Setup

1.  **Install Python 3.8+**
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configuration**:
    - Rename `.env.example` to `.env`.
    - Edit `.env` with your details:
      - `CONTEST_SLUG`: From your contest URL.
      - `HACKERRANK_COOKIE`: Your browser cookie (F12 -> Network).
      - `GEMINI_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/).
      - `REQUEST_DELAY_SECONDS`: Default is 2.0s (increase if needed).

## Usage

Run the main script:

```bash
python main.py
```

## Output

- **Code**: Saved in `results/<username>/<challenge>.txt`
- **Report**: Saved as `results/Report_YYYYMMDD_HHMM.txt`

## Notes

- The tool automatically retries if HackerRank limits requests (429 Too Many Requests).
- The report file is tab-separated. You can open it in Excel or Google Sheets by importing it as a CSV/Text file with `Tab` delimiter.
