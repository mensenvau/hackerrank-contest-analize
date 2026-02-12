import os
import time
import tqdm
from collector import HackerRankCollector
from organizer import ResultOrganizer
from reporter import ExcelReporter
from analyzer import CodeAnalyzer
from config import Config

def main():
    print("🚀 Starting Analysis...")
    Config.validate()
    
    collector = HackerRankCollector()
    organizer = ResultOrganizer(Config.OUTPUT_DIR)
    analyzer = CodeAnalyzer()
    reporter = ExcelReporter(Config.OUTPUT_DIR)

    leaderboard = collector.get_leaderboard()
    submissions = collector.get_all_submissions()
    challenges_map = collector.get_challenges()
    
    print("Download code & organize...")
    cache = {} 
    fetcher = lambda s_id: cache.setdefault(s_id, collector.get_submission_source(s_id))
    
    organizer.organize(submissions, fetcher, challenges_map)

    print("AI Analysis...")
    analysis = {}
    
    # Group submissions by user -> challenge, keep best/latest code
    user_challenges = {}
    for s in submissions:
        user, ch = s.get('username'), s.get('challenge')
        if not user or not ch: continue
        user_challenges.setdefault(user, {})[ch] = s

    for user, subs in tqdm.tqdm(user_challenges.items(), desc="Analyzing"):
        # Build code dict for all challenges
        challenge_codes = {}
        for ch, sub in subs.items():
            code = fetcher(sub['id'])
            if code and len(code.strip()) > 10:
                challenge_codes[ch] = code
        
        if not challenge_codes:
            analysis[user] = {'cheating_score': 0, 'notes': ''}
            continue

        # One API call per user
        review = analyzer.analyze_user(user, challenge_codes)
        
        # Save review to user folder
        user_dir = os.path.join(Config.OUTPUT_DIR, organizer.sanitize(user))
        os.makedirs(user_dir, exist_ok=True)
        with open(os.path.join(user_dir, '_ai_review.txt'), 'w', encoding='utf-8') as f:
            f.write(f"Overall Cheating: {review.get('overall_cheating_probability', 0)}%\n")
            f.write(f"Summary: {review.get('overall_summary', '')}\n")
            f.write("=" * 50 + "\n\n")
            for ch in review.get('challenges', []):
                f.write(f"[{ch.get('challenge_name')}] {ch.get('cheating_probability',0)}% - {ch.get('summary','')}\n")

        prob = review.get('overall_cheating_probability', 0)
        summary = review.get('overall_summary', '')
        analysis[user] = {'cheating_score': prob, 'notes': summary}
        
        time.sleep(0.5)

    reporter.generate(leaderboard, analysis)
    print("Done!")

if __name__ == "__main__":
    main()
