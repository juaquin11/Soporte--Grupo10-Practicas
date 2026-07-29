import cv2
import os

#directorio donde estan las imagenes tipo .jpg
directorio = "."
formato ="{:03d}.jpeg"
cantidad = 3


imagenes = []
for i in range (cantidad):
    path = os.path.join(directorio, formato.format(i))
    img = cv2.imread(path)
    if img is None:
        print(f"no se pudo cargar : {path}")
        continue
    imagenes.append(img)

if len(imagenes) < 2:
    print ("se necesitan al menos dos imagenes para hacer stitching")
    exit()

#usa el modulo de stitcher (opencv 4+)
stitcher = cv2.Stitcher_create()
estado, pano = stitcher.stitch(imagenes)

if estado == cv2.Stitcher_OK:
    print ("stitching completado con exito")
    cv2.imshow("panorama", pano)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print(f"error en stitching codigo de estado: {estado}")