# Scraper
- Open config file and add list of links to videos you want to scrape and execute ```python main.py scrape --type=videos```
- To scrape all video on a channel add link to channel and execute command ```python main.py scrape --type=channel``` (can include exclude / include parameters eg: exclude any videos with specific keywords in title see config.yaml for more)
- n_workers specifies the number of threads to spawn (approximately 2 threads per processor)

