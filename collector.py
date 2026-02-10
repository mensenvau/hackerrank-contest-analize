import os
import time
import requests
from config import Config

class HackerRankCollector:
    def __init__(self):
        Config.validate()
        self.headers = Config.get_headers()
        self.base_url = "https://www.hackerrank.com/rest/contests"
        self.slug = Config.CONTEST_SLUG
        
    def get_challenges(self):
        print("Fetching challenges metadata...")
        url = f"{self.base_url}/{self.slug}/challenges?offset=0&limit=100"
        try:
            resp = requests.get(url, headers=self.headers)
            resp.raise_for_status()
            models = resp.json().get('models', [])
            # Return map: {"Challenge Name": max_score}
            # Note: HackerRank API field for score might be 'max_score' or 'score' inside challenge model
            return {c.get('name'): c.get('max_score', 0) for c in models}
        except Exception as e:
            print(f"Error fetching challenges: {e}")
            return {}

    def get_all_submissions(self, callback=None):
        submissions = []
        offset = 0
        limit = 100
        
        print("Fetching submissions...")
        while True:
            url = f"{self.base_url}/{self.slug}/judge_submissions/?offset={offset}&limit={limit}"
            try:
                resp = requests.get(url, headers=self.headers)
                resp.raise_for_status()
                models = resp.json().get('models', [])
                
                if not models: break
                    
                for sub in models:
                    submissions.append({
                        "id": sub.get("id"),
                        "username": sub.get("hacker_username") or sub.get("hacker"),
                        "challenge": sub.get("challenge", {}).get("name") or sub.get("challenge_slug"),
                        "status": sub.get("status") or sub.get("result"),
                        "language": sub.get("language"),
                        "score": sub.get("score") or sub.get("display_score", 0),
                        "created_at": sub.get("created_at") or sub.get("created_at_epoch"),
                        "time_taken": sub.get("time_taken")
                    })

                offset += limit
                if callback: callback(len(submissions))
                else: print(f"Fetched {len(submissions)}...")
                time.sleep(Config.REQUEST_DELAY_SECONDS)
                
            except Exception as e:
                print(f"Error fetching submissions: {e}")
                break
                
        return submissions

    def get_submission_source(self, sub_id):
        url = f"{self.base_url}/{self.slug}/submissions/{sub_id}"
        retries = 3
        
        for attempt in range(retries):
            # Respect configured delay
            time.sleep(Config.REQUEST_DELAY_SECONDS)
            
            try:
                resp = requests.get(url, headers=self.headers)
                
                if resp.status_code == 429:
                    wait_time = (attempt + 1) * 10 # Aggressive backoff: 10s, 20s, 30s
                    print(f"⚠️ Rate limited (429). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                if resp.status_code == 404: 
                    return "// Not found"
                
                resp.raise_for_status()
                return resp.json().get('model', {}).get('code', "// No code")
                
            except Exception as e:
                if attempt == retries - 1:
                    return f"// Error: {str(e)}"
                time.sleep(1) # Small delay on other errors before retry
        
        return "// Error: Max retries exceeded"

    def get_leaderboard(self):
        participants = []
        offset = 0
        limit = 100

        print("Fetching leaderboard...")
        while True:
            url = f"{self.base_url}/{self.slug}/leaderboard?offset={offset}&limit={limit}"
            try:
                resp = requests.get(url, headers=self.headers)
                resp.raise_for_status()
                models = resp.json().get('models', [])
                if not models: break

                for p in models:
                     participants.append({
                        "username": p.get("hacker"),
                        "score": p.get("score", 0),
                        "time_taken": p.get("time_taken", 0),
                        "rank": p.get("rank")
                     })

                offset += limit
                print(f"Fetched {len(participants)}...")
                time.sleep(Config.REQUEST_DELAY_SECONDS)
            except Exception as e:
                print(f"Error leaderboard: {e}")
                break
        
        return participants
