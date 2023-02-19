import os
import sys
import argparse
from src.scrape import Scraper
from src.utils import open_config
from src.asr import Diarizer, ASR


def scrape():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scrape_channel", action="store_true")
    args, lf_args = parser.parse_known_args()

    scraper = Scraper(scrape_channel=args.scrape_channel)
    scraper.run()


def process_audio():
    parser = argparse.ArgumentParser()
    parser.add_argument("--diarize", action="store_true")
    parser.add_argument("--asr", action="store_true")
    parser.add_argument("--hf_token", type=str, default=None)
    args, lf_args = parser.parse_known_args()

    if args.diarize:
        assert (
            args.hf_token is not None
        ), "Huggingface token not set. required for speaker diarization, see here https://huggingface.co/docs/hub/security-tokens"
        diarizer = Diarizer(args.hf_token)
        diarizer.run()

    if args.asr:
        # Get all wav files
        config = open_config()
        data_dir = f"{config['download_path']}/{config['dataset_name']}"
        files = [
            f"{data_dir}/{folder}/{file}"
            for folder in os.listdir(f"{data_dir}")
            if os.path.isdir(f"{data_dir}/{folder}")
            for file in os.listdir(f"{data_dir}/{folder}")
            if file.endswith(".wav")
        ]
        asr = ASR()
        asr.run(files)


if __name__ == "__main__":
    command = sys.argv[1]

    parser = argparse.ArgumentParser()
    if command == "scrape":
        scrape()

    elif command == "process_audio":
        process_audio()

    elif command == "scrape_and_process":
        scrape()
        process_audio()

    else:
        raise ValueError(
            f"Command {command} not recognized, please use one of scrape, process_audio, scrape_and_process"
        )
