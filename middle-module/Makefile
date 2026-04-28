build:
	cmake -S . -B build -G Ninja

run:
	cmake --build build && ./build/main

virtual-port:
	socat -v -x PTY,link=/tmp/virt,raw,echo=0 /dev/ttyACM0,raw,echo=0