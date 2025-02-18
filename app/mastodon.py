import requests
from loguru import logger
from app.config import MASTODON_INSTANCE, MASTODON_ACCESS_TOKEN

def post_to_mastodon(transcript: str, title: str) -> dict:
    """Posts the podcast transcript as a thread to Mastodon"""
    headers = {
        'Authorization': f'Bearer {MASTODON_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    try:
        # Post main content
        main_content = f"🎙️ New AI Podcast Discussion: {title}\n\n#AIPodcast"
        main_post = requests.post(
            f"{MASTODON_INSTANCE}/api/v1/statuses",
            json={"status": main_content, "visibility": "public"},
            headers=headers
        ).json()

        # Split and post replies
        chunks = []
        current_chunk = ""
        
        for line in transcript.strip().split('\n\n'):
            if not line.strip():
                continue
                
            speaker, text = line.split(':', 1)
            emoji = {
                'host-female': '👩‍🎤',
                'main-speaker': '🎙️',
                'guest-1': '👤',
                'guest-2': '👥',
                'guest-3': '🗣️',
                'guest-4': '💭'
            }.get(speaker.strip(), '🎯')
            
            formatted_line = f"{emoji} {speaker}: {text.strip()}"
            
            if len(current_chunk + "\n\n" + formatted_line) > 450:
                chunks.append(current_chunk)
                current_chunk = formatted_line
            else:
                current_chunk = current_chunk + "\n\n" + formatted_line if current_chunk else formatted_line

        if current_chunk:
            chunks.append(current_chunk)

        # Post replies
        reply_posts = []
        last_post_id = main_post['id']
        
        for chunk in chunks:
            reply = requests.post(
                f"{MASTODON_INSTANCE}/api/v1/statuses",
                json={
                    "status": chunk,
                    "in_reply_to_id": last_post_id,
                    "visibility": "public"
                },
                headers=headers
            ).json()
            reply_posts.append(reply)
            last_post_id = reply['id']

        return {
            'mainPost': {'url': main_post['url'], 'id': main_post['id']},
            'replyPosts': [{'url': post['url'], 'id': post['id']} for post in reply_posts]
        }

    except Exception as e:
        logger.error(f"Failed to post to Mastodon: {str(e)}")
        raise 