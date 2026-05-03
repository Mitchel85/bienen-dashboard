import sys

def mandelbrot(c, max_iter):
    z = 0
    for n in range(max_iter):
        if abs(z) > 2:
            return n
        z = z*z + c
    return max_iter

def draw_mandelbrot(width, height, max_iter):
    # Zeichen für verschiedene Dichten (von dunkel nach hell)
    chars = " .:-=+*#%@"
    
    result = []
    for y in range(height):
        row = ""
        for x in range(width):
            # Mappe Pixel-Koordinaten auf die komplexe Ebene
            # Fokus auf das Hauptgebiet der Mandelbrot-Menge
            re = (x - width / 1.5) * 3.0 / width
            im = (y - height / 2.0) * 2.0 / height
            c = complex(re, im)
            
            m = mandelbrot(c, max_iter)
            
            if m == max_iter:
                row += chars[-1]
            else:
                row += chars[m % (len(chars) - 1)]
        result.append(row)
    return "\n".join(result)

if __name__ == "__main__":
    # Konsolenfreundliche Dimensionen
    w, h = 60, 30
    print(draw_mandelbrot(w, h, 50))
