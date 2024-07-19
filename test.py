import logging
from pytube import YouTube
from pytube.innertube import _default_clients
from pytube import cipher
import re

# Set up logging
logging.basicConfig(level=logging.DEBUG)

_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

def get_throttling_function_name(js: str) -> str:
    function_patterns = [
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

    raise Exception("Could not find throttling function name")

cipher.get_throttling_function_name = get_throttling_function_name

def download_video(video_url, save_path='downloads'):
    try:
        logging.debug(f"Creating YouTube object for URL: {video_url}")
        yt = YouTube(video_url)
        logging.debug(f"Successfully created YouTube object. Video title: {yt.title}")

        # Debugging stream selection
        logging.debug("Available streams:")
        for stream in yt.streams:
            logging.debug(stream)

        stream = yt.streams.get_highest_resolution()
        logging.debug(f"Selected stream: {stream}")

        logging.info(f"Downloading {yt.title}...")
        stream.download(output_path=save_path)
        logging.info(f"Downloaded {yt.title} to {save_path}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=b5K8GS3zkkU"
    download_video(video_url, save_path='path_to_save_video')
