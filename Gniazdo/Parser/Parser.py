import os
import struct
import threading
from enum import IntEnum, auto

import serial

HEADER = 0x55
PACKET_SIZE = 8
FORMAT = "<BBBBf"


class NAME(IntEnum):
    MOVE = 0
    STOP = auto()
    reset_pos = auto()


FMT = struct.Struct(FORMAT)


class Parser:
    def __init__(self, cam, mode="console", device="/tmp/virt", flag=None):

        self.running = False
        self.cam = cam
        self.flag = flag
        if mode == "console":
            self.input_thread = self.input_thread_console
        elif mode == "serial":
            self.input_thread = self.input_thread_serial

            port = os.path.realpath(device)
            self.serial0 = serial.Serial(
                port=port, baudrate=115200, timeout=0.1, write_timeout=0.1
            )
            print("Starting serial ...")

            if flag is not None and flag:
                port_fwd = "/dev/ttyACM0"
                if device[-1] == "0":
                    port_fwd = port_fwd[:-1] + "1"

                self.serial_forward = serial.Serial(
                    port=port_fwd, baudrate=115200, timeout=0.1, write_timeout=0.1
                )
                print("Started forwarding serial ...")

    def start(self):
        self.running = True
        self.thread = threading.Thread(
            target=self.input_thread, args=(self.cam,), daemon=True
        )
        self.thread.start()

        if self.flag is not None and self.flag:
            self.reverse_fwd_thread = threading.Thread(
                target=self._reverse_forward_thread, daemon=True
            )
            self.reverse_fwd_thread.start()

    def _reverse_forward_thread(self):
        while self.running:
            try:
                to_read = self.serial_forward.in_waiting or 1
                data = self.serial_forward.read(to_read)
                if data:
                    self.serial0.write(data)
            except serial.SerialTimeoutException:
                pass
            except Exception:
                pass

    def _handle_console_command(self, cam, cmd):
        parts = cmd.strip().lower().split()

        i = 0
        while i < len(parts):
            direction = parts[i]

            if i + 1 < len(parts):
                value = float(parts[i + 1])
                i += 2
            else:
                value = 1
                i += 1

            if direction == "up":
                cam.move_vertical(-1 * value)
            elif direction == "down":
                cam.move_vertical(value)
            elif direction == "left":
                cam.move_horizontal(-1 * value)
            elif direction == "right":
                cam.move_horizontal(value)
            elif direction == "stop":
                with cam.lock():
                    cam.orientation_target = cam.orientation
            else:
                print(f"Unknown command: {direction}")

    def _read_packets(self):
        write_pos = 0
        buffer = bytearray(8)
        view = memoryview(buffer)

        while self.running:
            # read directly into buffer (FAST)
            n = self.serial0.readinto(view[write_pos:])
            if not n:
                continue

            write_pos += n

            i = 0

            while i <= write_pos - PACKET_SIZE:
                if buffer[i] != HEADER:
                    i += 1
                    continue

                chunk = view[i : i + PACKET_SIZE]

                calc_checksum = chunk[0] ^ chunk[1] ^ chunk[2]
                for b in chunk[4:8]:
                    calc_checksum ^= b

                if calc_checksum != chunk[3]:
                    i += 1
                    continue

                if self.flag:
                    try:
                        self.serial_forward.write(chunk)
                    except serial.SerialTimeoutException:
                        pass

                packet_data = FMT.unpack(chunk)

                self._handle_serial_command(self.cam, packet_data)

                i += PACKET_SIZE

            # compact remaining bytes
            remaining = write_pos - i
            buffer[:remaining] = buffer[i:write_pos]
            write_pos = remaining

    def _handle_serial_command(self, cam, cmd):

        (header, name, additional, checksum, value) = cmd
        match (name, additional):
            case (NAME.MOVE.value, x):
                cam.move(additional, value)
            case (NAME.STOP, _):
                cam.stop()

    def input_thread_serial(self, camera):
        self._read_packets()

    def input_thread_console(self, camera):
        while self.running:
            command = input()
            self._handle_console_command(camera, command)
