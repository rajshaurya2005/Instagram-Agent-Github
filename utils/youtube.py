import requests
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL


def download_youtube_video(url):
    ydl_opts = {
        "outtmpl": "youtube.%(ext)s",
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "quiet": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "youtube.mp4"


def fetch_youtube_meta(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("meta", property="og:title")
    description_tag = soup.find(
        "meta", {"name": "description"}
    ) or soup.find("meta", property="og:description")

    title = title_tag["content"] if title_tag else "Title not found"
    description = (
        description_tag["content"] if description_tag else "Description not found"
    )
    return title, description