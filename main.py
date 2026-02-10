import os
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
    
    unique_subs = {}
    for s in submissions:
        user, ch = s.get('username'), s.get('challenge')
        if not user or not ch: continue
        unique_subs.setdefault(user, {})[ch] = s

    for user, subs in tqdm.tqdm(unique_subs.items()):
        max_prob = 0
        notes = []
        
        for ch, sub in subs.items():
            code = fetcher(sub['id'])
            res = analyzer.analyze(code, ch)
            if res['prob'] > max_prob: max_prob = res['prob']
            if res['prob'] > 40: notes.append(f"[{ch}: {res['prob']}%] {res['notes']}")
        
        analysis[user] = {'cheating_score': max_prob, 'notes': "; ".join(notes)}

    reporter.generate(leaderboard, analysis)
    print("Done!")

if __name__ == "__main__":
    main()
