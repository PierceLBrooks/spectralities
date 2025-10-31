
git submodule update --init --recursive
python3 -m pip install -r audio2spec/requirements.txt
python3 -m pip install -r requirements.txt
python3 spectralities.py yourwav.wav

