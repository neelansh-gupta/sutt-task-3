from django import template
from django.utils.safestring import mark_safe
import markdown
import bleach

register = template.Library()

# Allowed HTML tags and attributes for bleach
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 's', 'code', 'pre', 'blockquote',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'hr', 'a', 'img',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'div', 'span',
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'code': ['class'],
    'pre': ['class'],
    'div': ['class'],
    'span': ['class'],
}

@register.filter(name='markdown')
def markdown_format(text):
    """
    Convert markdown text to HTML and sanitize it
    """
    if not text:
        return ''
    
    # Convert markdown to HTML
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
            'markdown.extensions.extra',
        ]
    )
    html = md.convert(text)
    
    # Sanitize HTML to prevent XSS
    clean_html = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
    
    return mark_safe(clean_html)
