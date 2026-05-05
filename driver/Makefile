flash:
	@mv main.ino driver.ino
	arduino-cli compile --upload -p /dev/ttyACM0 --fqbn esp32:esp32:esp32s3 .
	@mv driver.ino main.ino

check:
	cp main.ino main.cpp
	cpplint --filter=-build/include_what_you_use main.cpp || (rm main.cpp; exit 1)
	rm main.cpp
