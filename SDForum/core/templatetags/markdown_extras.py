import markdown
import bleach
from django import template

register = template.Library()

ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union({
    "p", "pre", "code", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "strong", "em", "blockquote", "hr", "br"
})
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "code": ["class"],
}

@register.filter
def markdownify(text):
    if not text:
        return ""
    html = markdown.markdown(
        text,
        extensions=["fenced_code", "tables"]
    )
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
