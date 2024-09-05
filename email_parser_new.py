import email
from email import policy
from email.parser import BytesParser

def parse_eml(file_path):
    # Read the .eml file
    with open(file_path, 'rb') as file:
        msg = BytesParser(policy=policy.default).parse(file)
    
    # Extract email metadata
    email_data = {
        "subject": msg['subject'],
        "from": msg['from'],
        "to": msg['to'],
        "date": msg['date'],
        "content": "",
        "thread_depth": 0,
        "replies": []
    }
    
    # Extract the body of the email (plain text or HTML)
    if msg.is_multipart():
        for part in msg.iter_parts():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    email_data["content"] = payload.decode('utf-8', errors='ignore')
                break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            email_data["content"] = payload.decode('utf-8', errors='ignore')

    # Helper function to extract replies based on the quoted sections of the email
    def extract_replies(msg_body):
        # Split by the common reply indicators (i.e., "On <date>, <someone> wrote:")
        lines = msg_body.splitlines()
        replies = []
        current_reply = []
        in_reply = False

        for line in lines:
            if line.startswith("On ") and "wrote:" in line:
                if current_reply:
                    replies.append("\n".join(current_reply))
                    current_reply = []
                in_reply = True
            elif in_reply:
                current_reply.append(line)

        # Add the last collected reply
        if current_reply:
            replies.append("\n".join(current_reply))

        return replies

    # Extract replies from the email content
    if email_data["content"]:
        replies = extract_replies(email_data["content"])
        email_data["thread_depth"] = len(replies)
        for reply in replies:
            email_data["replies"].append({
                "content": reply
            })

    # Save the extracted data to a file
    output_file = "parsed_email_data.txt"
    with open(output_file, "w") as f:
        f.write(f"Subject: {email_data['subject']}\n")
        f.write(f"From: {email_data['from']}\n")
        f.write(f"To: {email_data['to']}\n")
        f.write(f"Date: {email_data['date']}\n")
        f.write(f"Content: {email_data.get('content', 'No content')}\n")
        f.write(f"Thread Depth: {email_data['thread_depth']}\n")
        f.write("Replies:\n")
        for idx, reply in enumerate(email_data["replies"]):
            f.write(f"\tReply {idx+1} Content:\n{reply['content']}\n\n")

    print(f"Data saved to {output_file}")

# Usage
parse_eml('/Users/disha.patel/Downloads/test.eml')

def clean_email_content(file_path, output_path):
    with open(file_path, 'r') as file:
        content = file.readlines()

    cleaned_content = []
    skip_phrases = [
        'You received this message because',  # Footer unsubscribe message
        'unsubscribe from this group',        # Unsubscribe info
        'https://',                           # Links
        'On Fri,',                            # Previous replies
        'On Tue,',                            # Previous replies
        'wrote:',                             # Email quotes
        'c.', 'w.'                            # Contact information
    ]

    for line in content:
        # Skip lines that contain any of the skip_phrases
        if not any(skip_phrase in line for skip_phrase in skip_phrases):
            cleaned_content.append(line.strip())

    # Write the cleaned content to a new file
    with open(output_path, 'w') as file:
        for line in cleaned_content:
            if line:  # Skip empty lines
                file.write(line + '\n')

    print("ran")

# Usage
clean_email_content('/Users/disha.patel/Desktop/parsed_email_data.txt', '/Users/disha.patel/Desktop/cleaned_email_data.txt')