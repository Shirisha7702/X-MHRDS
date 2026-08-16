import re

def mask_pii(text):
    """
    Scrubs Personally Identifiable Information (PII) from user-generated text.
    Masks:
    - Emails (e.g. user@domain.com -> [EMAIL])
    - Phone numbers (various formats -> [PHONE])
    - Reddit usernames (e.g. u/user_name -> [USER])
    - Subreddit names (e.g. r/SuicideWatch -> [SUBREDDIT])
    - Common locations/names indicators (e.g. "my name is John" -> "my name is [NAME]")
    """
    if not isinstance(text, str):
        return ""

    # 1. Mask Subreddits
    text = re.sub(r'\b[rR]/\w+\b', '[SUBREDDIT]', text)

    # 2. Mask Usernames
    text = re.sub(r'\b[uU]/\w+\b', '[USER]', text)

    # 3. Mask Emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    text = re.sub(email_pattern, '[EMAIL]', text)

    # 4. Mask Phone numbers
    # Matches patterns like 1-800-273-8255, +1 (800) 273-8255, 988, etc.
    phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    text = re.sub(phone_pattern, '[PHONE]', text)
    
    # 5. Mask Name indicators: "name is [Name]", "I am [Name]"
    # Simple semantic heuristics for safety. Only the prefix is matched case-insensitively
    # (scoped inline flag) - the [A-Z][a-z]+ capture must stay case-sensitive, otherwise
    # ordinary lowercase words (e.g. "I am feeling") would be misdetected as names.
    text = re.sub(r'\b(?:(?i:my name is|i am called|this is))\s+([A-Z][a-z]+)\b', r'my name is [NAME]', text)
    text = re.sub(r'\b(?:(?i:i\'m|i am))\s+([A-Z][a-z]+)\b', r'I am [NAME]', text)
    
    return text

if __name__ == "__main__":
    sample = "Hello, my name is Sarah. You can contact me at sarah.123@gmail.com or call u/sarah_help on r/teenagers or at 555-123-4567."
    print("Original:", sample)
    print("Anonymized:", mask_pii(sample))
