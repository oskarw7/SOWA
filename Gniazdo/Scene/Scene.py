import cv2
import numpy as np
import threading
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
        self._last_wrap_w = None
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




    def overlay_image(self, overlay, x, y, _z):
        x += overlay.shape[1] / 2
        y += overlay.shape[0] / 2
        x = int(x) % self.image_width
        y = int(y)

        def blend(src, dst):
            if src.shape[2] == 4:
                overlay_rgb = src[:, :, :3].astype(float)
                alpha = src[:, :, 3:] / 255.0
            else:
                overlay_rgb = src.astype(float)
                alpha = 1.0
            roi_float = dst.astype(float)
            return (alpha * overlay_rgb + (1 - alpha) * roi_float).astype("uint8")

        with self.lock:
            if self._under_last_blit is not None:
                self.image[
                    self._last_blit_y : self._last_blit_y + self._last_blit_h,
                    self._last_blit_x : self._last_blit_x + self._last_blit_w,
                ] = self._under_last_blit["main"]
                if self._under_last_blit.get("extended") is not None:
                    self.image[
                        self._last_blit_y : self._last_blit_y + self._last_blit_h,
                        self.image_width + self._last_blit_x : self.image_width + self._last_blit_x + self._last_blit_w,
                    ] = self._under_last_blit["extended"]
                self._under_last_blit = None

            fh, fw = self.image_height, self.image_width
            if y >= fh or y + overlay.shape[0] <= 0:
                return

            h = min(overlay.shape[0], fh - y)
            if h <= 0:
                return
            overlay = overlay[:h, :]

            main_w = min(overlay.shape[1], fw - x)
            wrap_w = max(0, overlay.shape[1] - main_w)

            overlay_main = overlay[:, :main_w]
            overlay_wrap = overlay[:, main_w : main_w + wrap_w] if wrap_w > 0 else None

            under_main = self.image[y : y + h, x : x + main_w].copy()
            # Backup extended region (for duplication/wrapping)
            under_extended = None
            if main_w <= self._extension_pixels - x:
                under_extended = self.image[
                    y : y + h,
                    self.image_width + x : self.image_width + x + main_w,
                ].copy()

            self._under_last_blit = {"main": under_main, "extended": under_extended}
            self._last_blit_x = x
            self._last_blit_y = y
            self._last_blit_w = main_w
            self._last_blit_h = h

            # Blend main overlay
            self.image[y : y + h, x : x + main_w] = blend(
                overlay_main, self.image[y : y + h, x : x + main_w]
            )
            # Duplicate to extended region if entire main part fits within extension range
            if main_w <= self._extension_pixels - x:
                self.image[
                    y : y + h,
                    self.image_width + x : self.image_width + x + main_w,
                ] = self.image[y : y + h, x : x + main_w]
            
            # Handle wrap-around overflow
            if wrap_w > 0:
                self.image[
                    y : y + h,
                    self.image_width : self.image_width + wrap_w,
                ] = blend(overlay_wrap, self.image[y : y + h, self.image_width : self.image_width + wrap_w])

                          
                