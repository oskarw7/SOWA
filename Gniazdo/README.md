Dependencies:
ffmpeg and docker is required to be installed on your machine 

to run the simulation environment first go to Gniazdo/ directory then run 

make run-server

after that do 

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

then you can run the simulation with 

make sim

and if you want to see the stream use 

make play
