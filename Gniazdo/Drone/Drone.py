import cv2
import threading
from time import sleep
class Drone():

    def __init__(self):
        self.base_image = cv2.imread("./Drone/drone.png",cv2.IMREAD_UNCHANGED)
        self._position = [0,1600]
        self.scale = 0.1
        self.image = cv2.resize(self.base_image,None, fx= self.scale, fy = self.scale)
        self.check_points = [(1000,1600,2),(900,1850,3),(1500,2000,4)]
        self.lock = threading.Lock()
        self.current_check_point = 0 

    @property
    def position(self):
        with self.lock:
            return tuple(self._position) 

    @position.setter
    def position(self, value):
        with self.lock:
            self._position = list(value)

    def update_position(self, dx, dy):
        with self.lock:
            self._position[0] += dx
            self._position[1] += dy
            
    def start(self):
        self.thread = threading.Thread(target=self.follow_positions, daemon=True)
        self.thread.start()

    def follow_positions(self):
        self.position = [self.check_points[0][0], self.check_points[0][1]]
        dt = 1 / 24 
        while True:
            last_checkpoint = self.check_points[self.current_check_point]
            next_checkpoint = self.check_points[(self.current_check_point + 1 )% len(self.check_points)]
            v = [ (next_checkpoint[0] - last_checkpoint[0]) / next_checkpoint[2], (next_checkpoint[1] - last_checkpoint[1]) / next_checkpoint[2] ] 
            for axis in range(2):
                if abs(self.position[axis] - next_checkpoint[axis]) > 0.1:
                    if axis == 0:
                        self.update_position(v[0] * dt, 0)
                    else:
                        self.update_position(0, v[1] * dt)
                else:
                    self.current_check_point  = (self.current_check_point + 1)  % len(self.check_points)
                    break
            sleep(dt)
            # print(f"{self.position=} {v=}")


if __name__ == "__main__":
    d = Drone()

    d.follow_positions()