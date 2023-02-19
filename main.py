import sys
import argparse
from src.scrape import Scraper



if __name__ == '__main__':

    command = sys.argv[1]

    parser = argparse.ArgumentParser()
    if command == 'scrape':
        parser.add_argument('--scrape_channel', action='store_true')
        args, lf_args = parser.parse_known_args()

        scraper = Scraper(scrape_channel=args.scrape_channel)
        scraper.run()
