import threading
import serial
import struct
from enum import IntEnum,auto
from Camera.Camera import DIRECTION 
from Camera.Camera import STOP
import os
HEADER = 0x55
PACKET_SIZE = 8
FORMAT = "<BBBBf"

class NAME(IntEnum):
   MOVE =  0
   STOP =  auto()
   reset_pos =  auto()

FMT = struct.Struct(FORMAT)

class Parser():
    def __init__(self,cam,device = "/tmp/virt",mode = "console"):
        self.running = False
        self.cam = cam
        if(mode == 'console'):
            self.input_thread = self.input_thread_console
        elif(mode == 'serial'):
            self.input_thread = self.input_thread_serial
            port = os.path.realpath(device)
            self.serial0 = serial.Serial(port=port,baudrate=115200,timeout=1)
            print(f"Starting serial ...")

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.input_thread,args=(self.cam,),daemon=True)
        self.thread.start()

    def _handle_console_command(self,cam, cmd):
        parts = cmd.strip().lower().split()

        i = 0
        while i < len(parts):
            direction = parts[i]

            if i + 1 < len(parts) :
                value = float(parts[i + 1])
                i += 2
            else:
                value = 1
                i += 1

            if direction == "up":
                cam.move_vertical( -1 * value)
            elif direction == "down":
                cam.move_vertical(value)
            elif direction == "left":
                cam.move_horizontal(-1 * value)
            elif direction == "right":
                cam.move_horizontal(value)
            elif direction == "stop":
                with cam.lock():
                    cam.orientation_target =  cam.orientation
            else:
                print(f"Unknown command: {direction}")
    

    def _read_packets(self):
        write_pos = 0 
        buffer = bytearray(4096)
        view = memoryview(buffer)
        
        while True:
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

                chunk = view[i:i + PACKET_SIZE]

                packet_data = FMT.unpack(chunk)

                self._handle_serial_command(self.cam,packet_data)
              
                i += PACKET_SIZE

            # compact remaining bytes
            remaining = write_pos - i
            buffer[:remaining] = buffer[i:write_pos]
            write_pos = remaining
                    


    def _handle_serial_command(self,cam,cmd):
        
        (header, name, additional, checksum, value ) = cmd
        print( (name,additional))
        match (name, additional):
            case (NAME.MOVE.value,x):
                print(f"moving camera {x} {value}")
                cam.move(additional,value)
            case (NAME.STOP,_):
                cam.stop()

    def input_thread_serial(self,camera):
        self._read_packets()

    def input_thread_console(self,camera):
        while True:
            command = input()
            self._handle_console_command(camera,command)


