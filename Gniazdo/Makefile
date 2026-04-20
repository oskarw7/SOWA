.PHONY: run-server play clean sim

# Run RTSP simple server in Docker
run-server:
	docker run --rm -it \
	-v $(PWD)/rtsp-simple-server.yml:/rtsp-simple-server.yml \
	-p 8554:8554 \
	aler9/rtsp-simple-server:v1.3.0

# Play the RTSP stream using ffplay
play:
	ffplay -rtsp_transport tcp rtsp://localhost:8554/live.stream

# Optional: stop/remove leftover containers (safety cleanup)
clean:
	docker ps -aq --filter "ancestor=aler9/rtsp-simple-server:v1.3.0" | xargs -r docker stop

sim:
	python3 ./main.py