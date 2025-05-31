import pygame as pg
from GLWindow import *

MIN_ROTATION_SPEED = 0.01
MAX_ROTATION_SPEED = 0.1
CAMERA_ROTATION_SPEED = 0.03

def main():
	""" The main method where we create and setup our PyGame program """

	running = True
	window = OpenGLWindow()
	window.initGL()

	while running:

		for event in pg.event.get(): # Grab all of the input events detected by PyGame
			if event.type == pg.QUIT:  # This event triggers when the window is closed
				running = False
			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_q:  # This event triggers when the q key is pressed down
					running = False
				elif event.key == pg.K_a:
					if window.earthRotationSpeed > MIN_ROTATION_SPEED:
						window.earthRotationSpeed -= 0.01
				elif event.key == pg.K_s:
					if window.earthRotationSpeed < MAX_ROTATION_SPEED:
						window.earthRotationSpeed += 0.01
				elif event.key == pg.K_z:
					if window.moonRotationSpeed > MIN_ROTATION_SPEED:
						window.moonRotationSpeed -= 0.01
				elif event.key == pg.K_x:
					if window.moonRotationSpeed < MAX_ROTATION_SPEED:
						window.moonRotationSpeed += 0.01
				elif event.key == pg.K_SPACE:
					if window.earthRotationSpeed != 0.0:
						window.earthRotationSpeed = 0.0
					else:
						window.earthRotationSpeed = 0.01
					if window.moonRotationSpeed != 0.0:
						window.moonRotationSpeed = 0.0
					else:
						window.moonRotationSpeed = 0.01

		keys = pg.key.get_pressed()
		if keys[pg.K_j]:
			window.cameraXRotationSpeed = CAMERA_ROTATION_SPEED
		if keys[pg.K_k]:
			window.cameraYRotationSpeed = CAMERA_ROTATION_SPEED
		if keys[pg.K_l]:
			window.cameraZRotationSpeed = CAMERA_ROTATION_SPEED
		
		window.render()

	pg.quit()


if __name__ == "__main__":
	main()