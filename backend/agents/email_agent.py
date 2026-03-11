import pandas as pd
import re
import io

class EmailAgent:
    def validate_email(self, email):
        return re.match(r"[^@]+@[^@]+\.[^@]+", str(email))

    def send_invites(self, csv_content=None, base_draft="You are invited to the event!"):
        print("[*] EmailAgent: Executing outreach protocol...")
        sent_logs = []
        
        # Check if CSV string was actually provided and isn't empty
        if csv_content and len(csv_content.strip()) > 0:
            try:
                # Parse the raw string as a CSV
                df = pd.read_csv(io.StringIO(csv_content))
                for _, row in df.iterrows():
                    # Handle different potential column names (case-insensitive)
                    cols = {c.lower(): c for c in df.columns}
                    email_col = cols.get('email', df.columns[0]) # fallback to first col
                    name_col = cols.get('name', None)
                    
                    email = row.get(email_col, '')
                    name = row.get(name_col, 'Participant') if name_col else 'Participant'
                    
                    if self.validate_email(email):
                        message = f"Hi {name},\n\n{base_draft}\n\nBest,\nSwarm AI"
                        sent_logs.append({"email": email, "status": "Drafted", "preview": message[:40] + "..."})
            except Exception as e:
                print(f"[*] EmailAgent Error parsing CSV string: {e}")
                sent_logs = [{"email": "error@system.com", "status": "Failed", "preview": "Failed to parse CSV"}]
        else:
            print("[*] EmailAgent: No CSV provided. Firing fallback mock.")
            sent_logs = [{"email": "hacker1@iit.edu", "status": "Mocked", "preview": base_draft[:40] + "..."}]

        return sent_logs