import cv2
import numpy as np
import threading
from enum import IntEnum,auto
from time import sleep,monotonic

class Frame:
    def __init__(self, width = 1920, height = 1080):
        self.shape = [width,height]
        self.width = self.shape[0]
        self.height = self.shape[1]

class DIRECTION(IntEnum):
   LEFT =  0
   RIGHT =  auto()
   UP =  auto()
   DOWN = auto()

class STOP(IntEnum):
   HOR =  0
   VERT =  auto()
   BOTH =  auto()


class Camera:
    def __init__(self,scene):
        self.orientation = [0, 90]
        self.orientation_target = self.orientation.copy()
        self.scene = scene
        self.frame = Frame()
        self.a = [20,20]
        self.v = [0,0]
        self.axis_ranges = [360,180]
        self.lock = threading.Lock()
        self.running = False

        self.scene.extend_image_for_fast_wrap(self.frame.width)


    def move(self, direction: int , deg: int) -> None:
        match direction:

            case DIRECTION.LEFT:
                 self.orientation_target[0] = (self.orientation_target[0] + deg) % 360
            case DIRECTION.RIGHT:
                 self.orientation_target[0] = (self.orientation_target[0] - deg) % 360
            case DIRECTION.UP:
                 self.orientation_target[1] = (self.orientation_target[1] - deg) % 180 
            case DIRECTION.DOWN:
                 self.orientation_target[1] = (self.orientation_target[1] + deg) % 180 

    def stop(self)->None:
        with self.lock:
            self.orientation_target = self.orientation
            self.v = [0,0]

    def move_horizontal(self,deg: int )-> None:
        self.orientation_target[0] =  (self.orientation[0] + deg) % 360

    def move_vertical(self,deg: int )-> None:
        self.orientation_target[1] =  (self.orientation[1] + deg) % 180
        
    def _resolve_orientation(self):
        with self.lock:
            self.b_y = 0 if self.orientation[1] == 0 else int( self.orientation[1] / 180 * (self.scene.image_height - self.frame.height))
            self.b_x = 0 if self.orientation[0] == 0 else  int( self.orientation[0] /360 * self.scene.image_width)
        # print(f"{self.b_x=}, {self.b_y=}")
        return [self.b_x, self.b_y]

    def get_frame_resolve_drone_offset(self, drone_position) -> ([], [int,int]):
        table = self._resolve_orientation()
        offset = []
        frame0 = self.scene.get_frame(self.b_x,self.b_y,self.frame.width,self.frame.height) 
        for axis in range(2):
            offset.append((drone_position[axis]- table[axis])  % self.scene.image_width )
            print(drone_position, table, offset)
            if not offset[axis] <= table[axis] + self.frame.shape[axis] or not offset[axis] > 0:
                return (frame0,[-1,-1])    
        return (frame0, [y/2 - x for x,y in zip(offset, self.frame.shape)])


    def get_frame(self):

        table = self._resolve_orientation()
        frame0 = self.scene.get_frame(self.b_x,self.b_y,self.frame.width,self.frame.height) 
        return frame0

# MOVEMENT CONTROLLER 

    def start(self ,fps=90):
        self.running = True
        self.thread = threading.Thread(target=self._loop,  args=(fps,), daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def _move_camera(self, dt:int):
        with self.lock:
            orientation_delta = [a - b for a,b in zip( self.orientation ,self.orientation_target)]
            # How close to destination is okay to stop 
            for axis in range(2):
                if abs(orientation_delta[axis]) > 0.1:
                    #Determine which way is closer left or right
                    direction = 1 if (orientation_delta[axis] % self.axis_ranges[axis] < self.axis_ranges[axis]/2) else -1
                    distance_to_be_covered = (abs(self.v[axis] / self.a[axis]) * self.v[axis] / 2)
                    acceleration_dir = 1 if abs(self.orientation[axis] + distance_to_be_covered  - self.orientation_target[axis]) < 0.5 else -1
                    self.v[axis] += direction * acceleration_dir * self.a[axis] * dt
                    # print(f" {distance_to_be_covered=:.2f} {self.v[axis]=:.2f} {orientation_delta=} {self.orientation=}" )
                    self.orientation[axis] += self.v[axis] * dt
                    self.orientation[axis] %= self.axis_ranges[axis]
                else :
                    self.v[axis] =0 
            
    def _loop(self, fps):
        timestamp = monotonic()
        while self.running:
            dt = monotonic() - timestamp
            self._move_camera(dt)
            timestamp = monotonic()
            sleep(0.001)

if __name__ == '__main__':
    cam = Camera()
    cam.start()
    while True:
        sleep(1)
        cv2.imwrite("cam1.png",cam.get_frame())
