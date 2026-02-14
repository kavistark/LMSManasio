from django import template
from urllib.parse import urlparse, parse_qs

register = template.Library()

@register.filter
def youtube_embed(url):
    if not url:
        return ""

    parsed = urlparse(url)
    video_id = None

    # Normal watch?v=
    if parsed.path == "/watch":
        video_id = parse_qs(parsed.query).get("v", [None])[0]

    # youtu.be short link
    elif "youtu.be" in parsed.netloc:
        video_id = parsed.path.lstrip("/")

    # Shorts
    elif "/shorts/" in parsed.path:
        video_id = parsed.path.split("/shorts/")[-1]

    # Already embed
    elif "/embed/" in parsed.path:
        video_id = parsed.path.split("/embed/")[-1]

    if video_id:
        video_id = video_id.split("?")[0]
        video_id = video_id.split("&")[0]
        return f"https://www.youtube.com/embed/{video_id}"

    return url
