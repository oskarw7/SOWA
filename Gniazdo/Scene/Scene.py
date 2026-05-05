import cv2
import numpy as np
import threading
import math
class Scene():
    def __init__(self,sim):
        self.image = cv2.imread("./bernd-dittrich-j5pUj4Kmg_Q-unsplash.jpg")
        self.sim =sim
        self.image2 = self.image.copy() 
        self.image_width = np.size(self.image,1)
        self.image_height = np.size(self.image,0)
        self.lock = threading.Lock()
        self._under_last_blit = None
        self._last_blit_x = None
        self._last_blit_y = None
        self._last_blit_w = None
        self._last_blit_h = None
        self._is_Extended = False
        self._extension_pixels = 0

    def extend_image_for_fast_wrap(self,frame_width):
        self._is_Extended = True
        self._extension_pixels = frame_width
        with self.lock:
            #we are adding an overlap so that the left most part of the image is also on the end of the array so that we dont reach 
            #over the last index of array when generating frames around that area
            self.image = np.concatenate([self.image,self.image[:,:frame_width,:]],axis=1)


    def get_frame(self,x,y,w,h):
        with self.lock:
            frame = self.image[y : y + h ,x : x + w]
            return frame.copy()


    def overlay_object(self, object_to_overlay):
        # print(object_to_overlay.position)
        scale = 30/ object_to_overlay.position[2]
        object_to_overlay.image = cv2.resize(object_to_overlay.base_image, None, fx=scale , fy=scale)
        cv2.imwrite("./test.jpg",object_to_overlay.image)
        self.overlay_image(object_to_overlay.image,*object_to_overlay.position)




    def overlay_image(self, overlay, x, y,z):
        x += overlay.shape[0]/2
        y += overlay.shape[1]/2
        x = int(x) % self.image_width
        y = int(y)
        #             x+w < sciana  pelen obrazek tu i tu   |     x mniejsze      |      
        with self.lock:
            
            if self._last_blit_x:
                self.image[self._last_blit_y:self._last_blit_y+self._last_blit_h,self._last_blit_x:self._last_blit_x+self._last_blit_w] = self._under_last_blit
                if self._last_blit_x + self._last_blit_w< self._extension_pixels :

                    self.image[self._last_blit_y:self._last_blit_y+self._last_blit_h,self.image_width + self._last_blit_x:self.image_width + self._last_blit_x+self._last_blit_w] = self._under_last_blit
                elif self._last_blit_x < self._extension_pixels:
                    shrinked_w = self._extension_pixels - self._last_blit_x
                    self.image[self._last_blit_y:self._last_blit_y+self._last_blit_h,self.image_width + self._last_blit_x:self.image_width + self._last_blit_x+ shrinked_w] = self._under_last_blit[:,:shrinked_w]

            h, w = overlay.shape[:2]

            # Frame boundaries
            fh, fw = self.image_height,self.image_width 

            # Clip overlay if it goes outside frame
            if x >= fw or y >= fh:
                return  # completely outside

            w = min(w, fw - x)
            h = min(h, fh - y)

            overlay = overlay[:h, :w]

            roi = self.image[y:y+h, x:x+w]


            if overlay.shape[2] == 4:
                overlay_rgb = overlay[:, :, :3].astype(float)
                alpha = overlay[:, :, 3:] / 255.0
            else:
                overlay_rgb = overlay.astype(float)
                alpha = 1.0

            roi_float = roi.astype(float)

            blended = alpha * overlay_rgb + (1 - alpha) * roi_float
            self._under_last_blit = self.image[y:y+h, x:x+w].copy()
            self._last_blit_x = x
            self._last_blit_y = y
            self._last_blit_w = w
            self._last_blit_h = h
            self.image[y:y+h, x:x+w] = blended.astype("uint8")
            if x + w < self._extension_pixels :
                self.image[y:y+h, self.image_width + x: self.image_width + x +w] = blended.astype("uint8")
            elif x < self._extension_pixels:
                w = self._extension_pixels - x
                overlay = overlay[:h, w:]

                roi = self.image[y:y+h, x:x+w]


                if overlay.shape[2] == 4:
                    overlay_rgb = overlay[:, :, :3].astype(float)
                    alpha = overlay[:, :, 3:] / 255.0
                else:
                    overlay_rgb = overlay.astype(float)
                    alpha = 1.0

                roi_float = roi.astype(float)

                blended = alpha * overlay_rgb + (1 - alpha) * roi_float     
                          
                