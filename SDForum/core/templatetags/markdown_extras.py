import re
import markdown
from django import template
from django.contrib.auth import get_user_model

register = template.Library()
User = get_user_model()

#regex pattern to find mentions
MENTION_PATTERN = re.compile(r'@(\w+)')


def link_mentions(text):

    def replacer(match):
        username = match.group(1)

        # check user exists
        if User.objects.filter(username=username).exists():
            return f'<strong>@{username}</strong>'

        return f"@{username}"

    return MENTION_PATTERN.sub(replacer, text)


@register.filter
def markdownify(text):
    if not text:
        return ""

    text = link_mentions(text)

    html = markdown.markdown(
        text,
        extensions=["fenced_code", "tables"]
    )

    return html
