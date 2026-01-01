import re
import markdown
import bleach
from django import template
from django.urls import reverse
from django.contrib.auth import get_user_model

register = template.Library()
User = get_user_model()

MENTION_PATTERN = re.compile(r'@(\w+)')

ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union({
    "p", "pre", "code", "h1", "h2", "h3",
    "ul", "ol", "li", "strong", "em",
    "blockquote", "hr", "br", "a"
})

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "code": ["class"],
}


def link_mentions(text):
    """
    Replace @username with profile links IF user exists.
    """

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

    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES
    )
