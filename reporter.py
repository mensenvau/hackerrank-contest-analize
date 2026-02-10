import os
from datetime import datetime

class ExcelReporter:
    def __init__(self, output_dir):
        self.output_dir = output_dir

    def generate(self, leaderboard, analysis):
        data = []
        for user in leaderboard:
            username = user.get('username')
            notes = analysis.get(username, {})
            
            data.append({
                'Username': username,
                'Score': user.get('score'),
                'Time': user.get('time_taken'),
                'Cheating %': f"{notes.get('cheating_score', 0)}%",
                'AI Notes': notes.get('notes', ''),
                'Link': f"https://www.hackerrank.com/{username}"
            })

        # Sort by Score (desc) then Time (asc) without pandas
        data.sort(key=lambda x: (-float(x['Score']), float(x['Time'])))
        
        # Save as Tab-Separated Values (TSV/TXT)
        filename = f"Report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        # Write to file with tab separation and aligned columns
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            header = f"{'Username':<20}\t{'Score':<10}\t{'Time':<15}\t{'Cheating %':<12}\t{'Link':<50}\t{'AI Notes'}\n"
            f.write(header)
            f.write("-" * 150 + "\n")
            
            for row in data:
                line = f"{str(row['Username']):<20}\t{str(row['Score']):<10}\t{str(row['Time']):<15}\t{str(row['Cheating %']):<12}\t{str(row['Link']):<50}\t{str(row['AI Notes'])}\n"
                f.write(line)

        print(f"Report saved: {filepath}")
