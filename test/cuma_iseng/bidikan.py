import cv2
import numpy as np

scale = 10
width = 40 * scale  
height = 48 * scale 

img = np.zeros((height, width, 3), dtype=np.uint8) 

img.fill(255) 

def to_pixel_coords(x_cartesian, y_cartesian, scale):
    x_pixel = int(x_cartesian * scale + width / 2)
    y_pixel = int(-y_cartesian * scale + height / 2) 
    return x_pixel, y_pixel

S = 8  
line_color = (0, 255, 0)  
line_thickness = 2

x_min, x_max = -S/2, S/2  
y_min, y_max = -S/2, S/2  


pt1_pixel = to_pixel_coords(x_min, y_max, scale) 
pt2_pixel = to_pixel_coords(x_max, y_min, scale)


cv2.rectangle(img, pt1_pixel, pt2_pixel, line_color, line_thickness)


start_A = to_pixel_coords(0, S/2, scale)  
end_A = to_pixel_coords(0, 24, scale)      
cv2.line(img, start_A, end_A, line_color, line_thickness)


start_B = to_pixel_coords(0, -S/2, scale)    
end_B = to_pixel_coords(0, -24, scale)    
cv2.line(img, start_B, end_B, line_color, line_thickness)

start_K = to_pixel_coords(S/2, 0, scale)   
end_K = to_pixel_coords(20, 0, scale)     
cv2.line(img, start_K, end_K, line_color, line_thickness)


start_Ki = to_pixel_coords(-S/2, 0, scale)   
end_Ki = to_pixel_coords(-20, 0, scale)    
cv2.line(img, start_Ki, end_Ki, line_color, line_thickness)

cv2.imshow('Kotak dan Garis Memancar (Geometri Kartesius di OpenCV)', img)
cv2.waitKey(0)
cv2.destroyAllWindows()