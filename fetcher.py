import requests
import csv
import os
import utils


from dotenv import load_dotenv
load_dotenv()


class ChannelFetcher:
    def __init__(self, channel_id: str,
                 # CSV-related options
                 csv_fieldnames=utils.CSV_FIELDNAMES,
                 csv_delimiter=utils.CSV_DELIMITER,
                 csv_extension=utils.CSV_EXTENSION,
                 csv_filename_prefix=utils.CSV_FILENAME_PREFIX,
                 csv_line_terminator=utils.CSV_LINE_TERMINATOR,
                 ):

        # optionally customizable with (normal or lambda) functions
        self._channel_input_handler = (lambda x: x)
        self._video_data_row_handler = utils.filter_video_to_dict

        self.channel_id = self._channel_input_handler(channel_id)
        self._csv_file = open(csv_filename_prefix + channel_id + csv_extension,
                              "w", newline='', encoding="utf-8")
        self._csv_writer = csv.DictWriter(self._csv_file,
                                          delimiter=csv_delimiter,
                                          lineterminator=csv_line_terminator,
                                          fieldnames=csv_fieldnames)

        self.YOUTUBE_TOKEN = os.environ.get("YOUTUBE_TOKEN")
        self.YOUTUBE_PLAYLIST_ITEMS_ENDPOINT = os.environ.get("YOUTUBE_PLAYLIST_ITEMS_ENDPOINT")

    def set_channel_input_handler(self, fxn):
        self._channel_input_handler = fxn
        return self

    def set_video_data_row_handler(self, fxn):
        self._video_data_row_handler = fxn
        return self

    def _write_to_csv(self, dict_data):
        self._csv_writer.writerows(dict_data)

    def _get_playlist_items(self, playlist_id: str, page_token: str = "", max_results: int = 50):
        try:
            req = requests.get(self.YOUTUBE_PLAYLIST_ITEMS_ENDPOINT, params={
                "key": self.YOUTUBE_TOKEN,
                "part": "snippet",
                "playlistId": playlist_id,
                "maxResults": max_results,
                "pageToken": page_token
            })
        except requests.RequestException as e:
            print(e)
            return None

        data = req.json()
        return_data = (data["items"], data["nextPageToken"] if "nextPageToken" in data else "")
        return return_data

    def _filter_videos_data(self, videos_data):
        return [self._video_data_row_handler(video) for video in videos_data]

    def _process_entire_playlist(self, playlist_id: str):
        yt_response = self._get_playlist_items(playlist_id)
        if yt_response is None:
            # todo: error logging, potentially
            return
        self._write_to_csv(self._filter_videos_data(yt_response[0]))
        page_token = yt_response[1]

        while page_token != "":
            yt_response = self._get_playlist_items(playlist_id, page_token)
            if yt_response is None:
                return

            self._write_to_csv(self._filter_videos_data(yt_response[0]))
            page_token = yt_response[1]

    def run(self):
        uploads_playlist = utils.channel_id_to_uploads_playlist(self.channel_id)
        self._process_entire_playlist(uploads_playlist)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._csv_file.close()
