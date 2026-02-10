import os
import shutil

class ResultOrganizer:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def sanitize(self, name):
        return "".join([c for c in str(name) if c.isalnum() or c in (' ', '-', '_')]).strip()

    def organize(self, submissions, fetcher, challenges_meta=None):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        user_subs = {}
        for sub in submissions:
            user = sub.get('username')
            if not user: continue
            user_subs.setdefault(user, []).append(sub)

        print(f"Organizing {len(user_subs)} users...")

        for user, subs in user_subs.items():
            user_dir = os.path.join(self.output_dir, self.sanitize(user))
            os.makedirs(user_dir, exist_ok=True)

            challenge_subs = {}
            for sub in subs:
                c_name = sub.get('challenge', 'Unknown')
                challenge_subs.setdefault(c_name, []).append(sub)

            for c_name, c_subs in challenge_subs.items():
                c_subs.sort(key=lambda x: x.get('created_at', 0))
                
                # Fetch Max Possible Score from metadata
                possible_max = challenges_meta.get(c_name, 0) if challenges_meta else 0
                
                # Calculate User's Best Score
                try:
                    user_max = max(float(s.get('score', 0)) for s in c_subs)
                except:
                    user_max = 0

                filepath = os.path.join(user_dir, f"{self.sanitize(c_name)}.txt")

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Challenge: {c_name}\nUser: {user}\nScore: {user_max} / {possible_max}\n{'='*30}\n\n")
                    
                    for sub in c_subs:
                        f.write(f"### [ID: {sub.get('id')}] Status: {sub.get('status')} | Score: {sub.get('score')} | Time: {sub.get('created_at')}\n")
                        code = fetcher(sub.get('id'))
                        f.write(f"{code}\n\n{'-'*30}\n\n")
