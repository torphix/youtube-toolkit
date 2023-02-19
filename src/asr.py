import os
import shutil
import whisper
from tqdm import tqdm
from typing import List
from .utils import open_config
from pydub import AudioSegment
from pyannote.audio import Pipeline


def convert_audio_to_wav(audio_file):
    if audio_file.endswith(".wav"):
        return audio_file
    elif audio_file.endswith(".mp3"):
        sound = AudioSegment.from_mp3(audio_file)
        wav_file = audio_file.replace(".mp3", ".wav")
        sound.export(wav_file, format="wav")
        return wav_file
    else:
        raise ValueError(f"File {audio_file} not supported")


class ASR:
    def __init__(self):
        self.config = open_config()['audio_processing']
        self.model = whisper.load_model(self.config['model_type'])

    def run(self, files: List[str]):
        for audio_file in tqdm(files, "Transcribing"):
            if audio_file.endswith(".wav"):
                transcript = whisper.transcribe(self.model, audio_file)
                with open(f"{audio_file.replace('.wav', '.txt')}", 'w') as f:
                    f.write(transcript['text'])


class Diarizer:
    def __init__(self, hf_token):
        self.pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization@2.1", use_auth_token=hf_token
        )

        self.config = open_config()
        self.data_dir = f"{self.config['download_path']}/{self.config['dataset_name']}"
        self.config = self.config["audio_processing"]

    def run(self):
        for audio_file in tqdm(os.listdir(self.data_dir), "Diarizing"):
            try:
                audio_file = convert_audio_to_wav(f"{self.data_dir}/{audio_file}")
            except ValueError:
                print(f"Skipping {audio_file} as it is not a supported audio file")
                continue
            diarization = self.pipeline(
                audio_file, num_speakers=self.config["n_speakers"]
            )
            print(f"{audio_file.replace('.wav', '.diarization')}")
            with open(f"{audio_file.replace('.wav', '.diarization')}", "w") as f:
                diarization.write_rttm(f)

        # Join diarized speaker segments into a single file then extract from audio file

        # Split audio files into segments based on diarization timestamps
        print("Splitting audio files into segments")
        for audio_file in tqdm(os.listdir(self.data_dir), "Splitting audio files"):
            if audio_file.endswith(".diarization"):
                # Make a new directory for each audio file
                os.makedirs(
                    f"{self.data_dir}/{audio_file.replace('.diarization', '')}",
                    exist_ok=True,
                )
                # Read and split audio
                with open(f"{self.data_dir}/{audio_file}") as f:
                    diarization = f.readlines()
                    # Remove lines that are short and sandwiched between the other speaker
                    # Ie: sometimes the one of the speakers might interrupt the other speaker with a grunt or something
                    # This removes those lines
                    rm_indexes = []
                    for i in range(len(diarization) - 1):
                        line = diarization[i].split(" ")
                        if (
                            float(line[4]) < self.config["min_audio_len"] / 1000
                        ):  # as in ms
                            # Check if sandwhiched between other speaker
                            if (
                                line[7] != diarization[i - 1].split(" ")[7]
                                and line[7] != diarization[i + 1].split(" ")[7]
                            ):
                                rm_indexes.append(i)
                    diarization = [
                        line
                        for i, line in enumerate(diarization)
                        if i not in rm_indexes
                    ]

                for i, line in enumerate(diarization):
                    line = line.split(" ")
                    if i == 0:
                        # Initialize
                        start = float(line[3])
                        end = float(line[4])
                        current_speaker = line[7]
                    if (
                        # Check speaker has changed
                        current_speaker
                        != line[7]
                    ) or (
                        i == len(diarization) - 1
                    ):  # save if last chunk
                        # New speaker, split audio and save chunk
                        audio = AudioSegment.from_wav(
                            f"{self.data_dir}/{audio_file.replace('.diarization', '.wav')}"
                        )
                        audio = audio[start * 1000 : (start + end) * 1000]
                        if len(audio) > self.config["min_audio_len"]:
                            audio.export(
                                f"{self.data_dir}/{audio_file.replace('.diarization', '')}/{i}_{audio_file.replace('.diarization', '')}.wav",
                                format="wav",
                            )
                        # Update start and end time
                        start = float(line[3])
                        end = float(line[4])
                        current_speaker = line[7]
                    else:
                        # Note as VAD is used its necessary to add the new start time to the end time
                        end = float(line[4]) + float(line[3]) - start

                # Move diarization file & wav file to new directory
                os.makedirs(f"{self.data_dir}/{audio_file.replace('.diarization', '')}/full_data", exist_ok=True)
                shutil.move(
                    f"{self.data_dir}/{audio_file}",
                    f"{self.data_dir}/{audio_file.replace('.diarization', '')}/full_data/{audio_file}",
                )
                shutil.move(
                    f"{self.data_dir}/{audio_file.replace('.diarization', '.wav')}",
                    f"{self.data_dir}/{audio_file.replace('.diarization', '')}/full_data/{audio_file.replace('.diarization', '.wav')}",
                )
