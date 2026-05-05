flash:
	mv main.ino driver.ino
	arduino-cli compile --upload -p /dev/ttyACM0 --fqbn esp32:esp32:esp32s3 .
	mv driver.ino main.ino
