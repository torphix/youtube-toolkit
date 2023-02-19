import pytube
from tqdm import tqdm
import concurrent.futures
from .utils import open_config


class Scraper:
    def __init__(self, scrape_channel: bool = False):
        self.config = open_config()["scraper"]
        self.download_path = (
            f"{self.config['download_path']}/{self.config['dataset_name']}"
        )
        if scrape_channel:
            assert (
                self.config["channel_link"] is not None
            ), "Channel link not provided in config.yaml"
            channel = pytube.Channel(self.config["channel_link"])
            self.video_links = [url for url in channel.video_urls]
        else:
            assert (
                len(self.config["video_links"]) > 0
            ), "No video links provided in config.yaml"
            self.video_links = self.config["video_links"]

        self.video_links = set(self.video_links)

    def run(self):
        with tqdm(total=len(self.config["video_links"])) as pbar:
            with concurrent.futures.ThreadPoolExecutor(
                self.config["n_workers"]
            ) as executor:
                futures = [
                    executor.submit(self.download_audio, url)
                    for url in self.config["video_links"]
                ]
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    pbar.update(1)

    def download_audio(self, video_link: str):
        video = pytube.YouTube(video_link)
        # Filter out videos with keywords in title
        for keyword in self.config["title_keyword_filter"]:
            if keyword in video.title:
                return
        # Download audio
        # strip characters that are not allowed in filenames
        filename = (
            "".join([c for c in video.title if c.isalpha() or c.isdigit() or c == " "])
            .rstrip()
            .lower()
            .replace(" ", "_")
            .replace("__", "_") + '.mp3'
        )

        video.streams.filter(only_audio=True).first().download(
            self.download_path, filename=filename
        )
