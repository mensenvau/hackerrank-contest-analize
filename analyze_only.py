"""
Standalone AI analysis script.
Reads code files from results/, sends ALL challenges per user in one API call,
saves per-user review to results/username/_ai_review.txt, and generates final report.

Usage: python analyze_only.py
"""
import os
import time
import tqdm
from analyzer import CodeAnalyzer
from reporter import ExcelReporter
from config import Config

def extract_code_from_file(filepath):
    """Extract the last/best code submission from a challenge file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by ### header to find individual submissions
    parts = content.split('### ')
    if len(parts) < 2:
        return ""

    # Take last submission block (most recent)
    last_block = parts[-1]
    # Remove the header line (first line = "[ID: ...] Status: ...")
    lines = last_block.split('\n')
    code_lines = lines[1:]  # Skip header

    # Remove trailing separator dashes
    code = '\n'.join(code_lines).strip()
    code = code.rstrip('-').strip()

    return code

def read_all_users(results_dir):
    """Read all users and their challenge codes from results/ folder."""
    users = {}

    for username in sorted(os.listdir(results_dir)):
        user_dir = os.path.join(results_dir, username)
        if not os.path.isdir(user_dir):
            continue

        challenges = {}
        for filename in os.listdir(user_dir):
            if not filename.endswith('.txt') or filename.startswith('_'):
                continue

            challenge_name = filename.replace('.txt', '')
            filepath = os.path.join(user_dir, filename)
            code = extract_code_from_file(filepath)

            if code and len(code.strip()) > 10:
                challenges[challenge_name] = code

        if challenges:
            users[username] = challenges

    return users

def save_user_review(user_dir, review_data):
    """Save AI review to user's folder as _ai_review.txt"""
    filepath = os.path.join(user_dir, '_ai_review.txt')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Overall Cheating Probability: {review_data.get('overall_cheating_probability', 0)}%\n")
        f.write(f"Summary: {review_data.get('overall_summary', '')}\n")
        f.write("=" * 50 + "\n\n")

        for ch in review_data.get('challenges', []):
            f.write(f"Challenge: {ch.get('challenge_name', 'Unknown')}\n")
            f.write(f"Cheating: {ch.get('cheating_probability', 0)}%\n")
            f.write(f"Note: {ch.get('summary', '')}\n")
            f.write("-" * 30 + "\n")

def main():
    print("🤖 AI Analysis Only Mode\n")

    analyzer = CodeAnalyzer()
    if not analyzer.model:
        print("❌ GEMINI_API_KEY missing.")
        return

    user_codes = read_all_users(Config.OUTPUT_DIR)
    print(f"Found {len(user_codes)} users.\n")

    if not user_codes:
        return

    # Read existing leaderboard from previous report
    leaderboard = []
    for f in sorted(os.listdir(Config.OUTPUT_DIR)):
        if f.startswith('Report_') and f.endswith('.txt'):
            report_path = os.path.join(Config.OUTPUT_DIR, f)
            print(f"Reading leaderboard from: {report_path}")
            with open(report_path, 'r', encoding='utf-8') as fp:
                lines = fp.readlines()[2:]  # Skip header + separator
                for line in lines:
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        leaderboard.append({
                            'username': parts[0].strip(),
                            'score': float(parts[1].strip()) if parts[1].strip() else 0,
                            'time_taken': float(parts[2].strip()) if parts[2].strip() else 0,
                        })
            break  # Use first (oldest) report

    # Run AI analysis per user (one API call per user)
    analysis = {}

    for user, challenges in tqdm.tqdm(user_codes.items(), desc="Analyzing"):
        review = analyzer.analyze_user(user, challenges)

        # Save to user folder
        user_dir = os.path.join(Config.OUTPUT_DIR, user)
        save_user_review(user_dir, review)

        # Collect for report
        prob = review.get('overall_cheating_probability', 0)
        summary = review.get('overall_summary', '')

        # Per-challenge details for notes
        ch_notes = []
        for ch in review.get('challenges', []):
            if ch.get('cheating_probability', 0) > 30:
                ch_notes.append(f"[{ch['challenge_name']}: {ch['cheating_probability']}%]")

        notes = f"{summary}"
        if ch_notes:
            notes += " | " + " ".join(ch_notes)

        analysis[user] = {'cheating_score': prob, 'notes': notes}

        time.sleep(0.5)

    # Generate final report
    if not leaderboard:
        leaderboard = [{'username': u, 'score': 0, 'time_taken': 0} for u in user_codes]

    reporter = ExcelReporter(Config.OUTPUT_DIR)
    reporter.generate(leaderboard, analysis)
    print("\n✨ Done!")

if __name__ == "__main__":
    main()
