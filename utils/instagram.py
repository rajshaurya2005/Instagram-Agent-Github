from instagrapi import Client


def post_on_insta(path, caption, username, password):
    try:
        cl = Client()
        cl.login(username=username, password=password)
        media = cl.clip_upload(path=path, caption=caption)
        return "Posted successfully!", None
    except Exception as e:
        return None, str(e)