.PHONY: all run-server run-server-d run venv play clean

.DEFAULT_GOAL := all

all: clean run-server-d run

# Run RTSP simple server in Docker
run-server:
	docker run --rm -it \
	-v $(PWD)/rtsp-simple-server.yml:/rtsp-simple-server.yml \
	-p 8554:8554 \
	-p 8000:8000/udp \
  -p 8001:8001/udp \
	aler9/rtsp-simple-server:v1.3.0

run-server-d:
	docker run -d --rm -it \
	-v $(PWD)/rtsp-simple-server.yml:/rtsp-simple-server.yml \
	-p 8554:8554 \
	-p 8000:8000/udp \
  -p 8001:8001/udp \
	aler9/rtsp-simple-server:v1.3.0

run:
	python3 main.py -ds -v -d -cc -mm /dev/ttyACM1

venv:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	

# Play the RTSP stream using ffplay
play:
	ffplay -rtsp_transport tcp rtsp://localhost:8554/live.stream

# Optional: stop/remove leftover containers (safety cleanup)
clean:
	docker ps -aq --filter "ancestor=aler9/rtsp-simple-server:v1.3.0" | xargs -r docker stop
