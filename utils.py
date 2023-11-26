from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

# todo: better handling of possibly incomplete env file
CSV_DELIMITER = os.environ.get("CSV_DELIMITER") or '\t'
CSV_EXTENSION = os.environ.get("CSV_EXTENSION") or ".tsv"
CSV_FILENAME_PREFIX = os.environ.get("CSV_FILENAME_PREFIX") or "channel_info_"
CSV_LINE_TERMINATOR = os.environ.get("CSV_LINE_TERMINATOR") or "\n"

# note: if this needs to be changed, `filter_video_to_dict` also has to be updated
# which is why I'm leaving it "hardcoded"
# you need to modify the code in order to change the structure of the returned data anyway
CSV_FIELDNAMES = ["title", "url", "published_at", "channel_id"]


def video_id_handler(video_id: str):
    """
    Takes ``video_id`` (e.g. ``dQw4w9WgXcQ``) as param, returns valid video URL.
    """

    youtube_base_url = "https://www.youtube.com/watch?v="
    return youtube_base_url + video_id


def channel_id_to_uploads_playlist(channel_id: str):
    """
    Takes ``channel_id`` (e.g. ``UCBa659QWEk1AI4Tg--mrJ2A``) as param, returns valid ID for channel's uploads playlist
    (e.g. ``UUBa659QWEk1AI4Tg--mrJ2A``).

    Separated from the rest of the code in case this method changes in the future.
    """

    return channel_id[:1] + "U" + channel_id[2:]


def filter_video_to_dict(video: dict):
    """
    Takes ``video`` as input (one element of the ``items`` array returned by YouTube in their
    ``Playlist.List`` API response) and filters the data, returning a dict with the desired columns.
    """
    return {
        "channel_id": video["snippet"]["channelId"],
        "title": video["snippet"]["title"].strip(),
        "url": video_id_handler(video["snippet"]["resourceId"]["videoId"]),
        "published_at": datetime.strftime(
            datetime.strptime(video["snippet"]["publishedAt"].strip(), "%Y-%m-%dT%H:%M:%S%z"),
            "%Y/%m/%d %H:%M:%S"
        )
    }