import pandas as pd
# Assuming this might fail during a live demo if SMTP drops
try:
    from services.email_service import send_email
except ImportError:
    send_email = None

class EmailAgent:
    def send_invites(self, csv_file=None):
        print("Executing outreach protocol...")
        # Mocking the process for a seamless UI demo
        sent = ["hacker1@iit.edu", "hacker2@nit.edu", "hacker3@bits.edu"]
        
        # If you actually have a CSV and working SMTP, use this logic:
        # if csv_file and send_email:
        #     df = pd.read_csv(csv_file)
        #     for _, row in df.iterrows():
        #         message = f"Hello {row['name']}, You are invited..."
        #         send_email(row["email"], message)
        #         sent.append(row["email"])

        return sent