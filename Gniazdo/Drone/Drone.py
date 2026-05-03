import threading
from time import sleep

import cv2


class Drone:
    def __init__(self,sim):
        self.base_image = cv2.imread("./Drone/drone.png",cv2.IMREAD_UNCHANGED)
        self._position = [0,1600]
        self.scale = 0.1
        self.image = cv2.resize(self.base_image, None, fx=self.scale, fy=self.scale)
        self.lock = threading.Lock()
        self.current_check_point = 0
        self.sim = sim
        self.check_points = [(600,2000,3), (-500 % self.sim.Scene.image_width,2000,3)]

    @property
    def position(self):
        with self.lock:
            return tuple(self._position) 

    @position.setter
    def position(self, value):
        with self.lock:
            self._position = list(value)

    def update_position(self, delta, axis):
        with self.lock:
            self._position[axis] += delta 
            if axis == 0 :
                self._position[axis] %= self.sim.Scene.image_width      

    def start(self):
        self.thread = threading.Thread(target=self.follow_positions, daemon=True)
        self.thread.start()

    def follow_positions(self):
        self.position = [self.check_points[0][0], self.check_points[0][1]]
        dt = 1 / 24 
        while True:
            completed_counter = 0
            last_checkpoint = self.check_points[self.current_check_point]
            next_checkpoint = self.check_points[
                (self.current_check_point + 1) % len(self.check_points)
            ]
            v = [
                
                ((( next_checkpoint[0] - last_checkpoint[0] + self.sim.Scene.image_width/2) % self.sim.Scene.image_width) - self.sim.Scene.image_width/2 ) / next_checkpoint[2],
                (next_checkpoint[1] - last_checkpoint[1]) / next_checkpoint[2],
            ]
            print(v[0])
            axies = [0,1]
            not_at_goal = True
            while axies != []:
                # print(self.position)
                for axis in axies:
                    if abs(self.position[axis] - next_checkpoint[axis]) > 10:
                        self.update_position(v[axis] * dt, axis)
                    else:
                        axies.remove(axis)
                sleep(dt)
            self.current_check_point = (self.current_check_point + 1) % len(self.check_points)
            # print(f"{self.position=} {v=} {self.check_points[self.current_check_point]}")


if __name__ == "__main__":
    d = Drone()

    d.follow_positions()
