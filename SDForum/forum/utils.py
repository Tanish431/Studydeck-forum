import re
from django.contrib.auth import get_user_model

User = get_user_model()

#regex for mentions
MENTION_PATTERN = r'@(\w+)'

def extract_mentions(text):
    usernames = set(re.findall(MENTION_PATTERN, text))
    return User.objects.filter(username__in=usernames)
