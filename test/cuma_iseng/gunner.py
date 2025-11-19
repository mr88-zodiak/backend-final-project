import cv2
import numpy as np

RANGE = 30         
SIZE = 600         
LINE_COLOR = (0, 255, 0) # Tetap Hijau
THICKNESS = 2      
TICK_INTERVAL = 10 
TICK_LENGTH = 10   # Panjang tanda skala normal

# Definisikan panjang baru untuk kedua sumbu
NEW_X_TICK_LENGTH = 25  # Dari permintaan sebelumnya
NEW_Y_TICK_LENGTH = 25  # Dari permintaan saat ini

# Tentukan posisi target yang diperpanjang
TARGET_TICKS = [-20, 20] 

canvas = np.zeros((SIZE, SIZE, 3), dtype=np.uint8) 

def cartesian_to_pixel(x, y, range_val, size_val):
    """Mengkonversi koordinat Kartesius (dengan asal di tengah) ke koordinat piksel (dengan asal di kiri atas)."""
    norm_x = (x + range_val) / (2 * range_val)
    norm_y = (y + range_val) / (2 * range_val)
    px = int(norm_x * size_val)
    py = int(size_val - (norm_y * size_val)) 
    return (px, py)

# --- Menggambar Sumbu Utama (X dan Y) ---
x_start_cart = (-RANGE, 0)
x_end_cart = (RANGE, 0)
x_start_pix = cartesian_to_pixel(*x_start_cart, RANGE, SIZE)
x_end_pix = cartesian_to_pixel(*x_end_cart, RANGE, SIZE)
cv2.line(canvas, x_start_pix, x_end_pix, LINE_COLOR, THICKNESS)

y_start_cart = (0, -RANGE)
y_end_cart = (0, RANGE)
y_start_pix = cartesian_to_pixel(*y_start_cart, RANGE, SIZE)
y_end_pix = cartesian_to_pixel(*y_end_cart, RANGE, SIZE)
cv2.line(canvas, y_start_pix, y_end_pix, LINE_COLOR, THICKNESS)

# --- Menggambar Tanda Skala (Tick Marks) ---
for i in range(-RANGE + TICK_INTERVAL, RANGE, TICK_INTERVAL):
    
    # --- 1. Tanda Skala pada Sumbu X (Garis Vertikal Pendek) ---
    
    current_x_tick_len = TICK_LENGTH
    if i in TARGET_TICKS:
        current_x_tick_len = NEW_X_TICK_LENGTH
    
    x_pos_pix, y_center_pix = cartesian_to_pixel(i, 0, RANGE, SIZE)
    
    x_tick_start = (x_pos_pix, y_center_pix - current_x_tick_len // 2)
    x_tick_end = (x_pos_pix, y_center_pix + current_x_tick_len // 2)
    cv2.line(canvas, x_tick_start, x_tick_end, LINE_COLOR, THICKNESS)
    
    # --- 2. Tanda Skala pada Sumbu Y (Garis Horizontal Pendek) ---
    
    if i != 0: 
        current_y_tick_len = TICK_LENGTH
        if i in TARGET_TICKS: # Sama, periksa apakah i adalah -20 atau 20
            current_y_tick_len = NEW_Y_TICK_LENGTH

        x_center_pix, y_pos_pix = cartesian_to_pixel(0, i, RANGE, SIZE)
        
        y_tick_start = (x_center_pix - current_y_tick_len // 2, y_pos_pix)
        y_tick_end = (x_center_pix + current_y_tick_len // 2, y_pos_pix)
        cv2.line(canvas, y_tick_start, y_tick_end, LINE_COLOR, THICKNESS)

cv2.imshow('Diagram Kartesius', canvas)
cv2.waitKey(0) 
cv2.destroyAllWindows()