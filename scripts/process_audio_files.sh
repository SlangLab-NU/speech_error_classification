AUDIO_DIR=data/audio
LIST_OUTPUT=data/metadata/wav_list.lst
SAMPLING_RATE=16000

python code/audio_processing/convert_mp3_to_wav.py --audio_dir $AUDIO_DIR --output $AUDIO_DIR --sample_rate $SAMPLING_RATE
python code/audio_processing/generate_audio_list.py --audio_dir $AUDIO_DIR --output $LIST_OUTPUT
