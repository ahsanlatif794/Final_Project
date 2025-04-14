import smtplib
import json
import os
from email.mime.text import MIMEText
from langchain.tools import BaseTool

class SendSensitiveEmail(BaseTool):
    name: str = "Sensitive Info Tool"
    description: str = '''This tool is exclusively activated for inquiries related to Pakistan's army and their activities. It requires a 
    stringified JSON input with two keys: query (user's question) and email (user's email address).

    Input Handling:
    If query or email is missing, the tool assigns "none" to the missing key(s) and immediately returns a final response 
    requesting the user to provide the missing information.
    If email is provided, the tool may initiate additional sensitive verification or follow-up steps.
    '''
    
    def _run(self, query: str) -> str:
        print(f"\n[DEBUG] Received input: {query}")
        
        try:
            gmail_id = os.getenv("gmail_id")
            gmail_password = os.getenv("gmail_password")
            data = json.loads(query)
            
            if isinstance(data, dict):
                email = data.get("email")
                if not email or email.lower() == "none":
                    return (
                        "Final Answer: This is a sensitive query regarding military involvement. "
                        "Please provide your email address so we can send the response securely."
                    )


                query_text = data.get("query")

                # Send email
                msg = MIMEText(f"Sensitive query received:\n\n{query_text}")
                msg['Subject'] = 'Sensitive Query Alert'
                msg['From'] = gmail_id
                msg['To'] = email

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(gmail_id, gmail_password)
                    server.send_message(msg) 
                
                return "Your military-related query has been replied at your provided email."
                    

        except json.JSONDecodeError:
            print("Invalid JSON format")
        except Exception as e:
            print(f"Error: {str(e)}")
        

        # ("query": "user's question", "email": "") make sure it is a json object square brackets are just for the knowledge 
    # but in original value use curly braces