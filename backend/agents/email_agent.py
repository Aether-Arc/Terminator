import pandas as pd
from services.email_service import send_email


class EmailAgent:

    def send_invites(self, csv_file):

        df = pd.read_csv(csv_file)

        sent = []

        for _, row in df.iterrows():

            message = f"""
            Hello {row['name']},

            You are invited to our event.

            """

            send_email(row["email"], message)

            sent.append(row["email"])

        return sent