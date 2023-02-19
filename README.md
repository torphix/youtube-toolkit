# Scraper
- Open config file and add list of links to videos you want to scrape and execute ```python main.py scrape --type=videos```
- To scrape all video on a channel add link to channel and execute command ```python main.py scrape --type=channel``` (can include exclude / include parameters eg: exclude any videos with specific keywords in title see config.yaml for more)
- n_workers specifies the number of threads to spawn (approximately 2 threads per processor)



## Audioprocessing (transcription & diarization)
For diarization complete pyanote is used, see here for setup instructions:
- 1. visit hf.co/pyannote/speaker-diarization and accept user conditions
- 2. visit hf.co/pyannote/segmentation and accept user conditions
- 3. visit hf.co/settings/tokens to create an access token
- 4. instantiate pretrained speaker diarization pipeline