import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr

from Geometry import *
from Texture import *

class OpenGLWindow:

    def __init__(self):
        self.clock = pg.time.Clock()
        self.earthRotationSpeed = 0.03
        self.moonRotationSpeed = 0.06

    def loadShaderProgram(self, vertex, fragment):
        with open(vertex, 'r') as f:
            vertex_src = f.readlines()

        with open(fragment, 'r') as f:
            fragment_src = f.readlines()

        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))

        return shader

    def initGL(self, screen_width=640, screen_height=480):
        pg.init()

        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 2)

        pg.display.set_mode((screen_width, screen_height), pg.OPENGL | pg.DOUBLEBUF)

        glEnable(GL_DEPTH_TEST)
        # Uncomment these two lines when perspective camera has been implemented
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glClearColor(0, 0, 0, 1)

        self.sunVao = glGenVertexArrays(1)
        self.earthVao = glGenVertexArrays(1)
        self.moonVao = glGenVertexArrays(1)

        # Note that this path is relative to your working directory when running the program
        # You will need change the filepath if you are running the script from inside ./src/

        self.shader = self.loadShaderProgram("./shaders/simple.vert", "./shaders/simple.frag")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
        self.sunTexture = Texture(SUN_TEXTURE)
        self.earthTexture = Texture(EARTH_TEXTURE)
        self.moonTexture = Texture(MOON_TEXTURE)

        glBindVertexArray(self.sunVao)
        self.sun = Sun('./resources/sphere.txt')

        glBindVertexArray(self.earthVao)
        self.earth = Earth('./resources/sphere.txt')

        glBindVertexArray(self.moonVao)
        self.moon = Moon('./resources/sphere.txt')

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy=45,
            aspect=screen_width / screen_height,
            near=0.1,
            far=10,
            dtype=np.float32
        )

        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"),
            1, GL_FALSE, projection_transform
        )

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")

        print("Setup complete!")


    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shader)  # You may not need this line
        colorLoc = glGetUniformLocation(self.shader, "objectColor")
        self.clock.tick(60)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.sunTexture.texture)
        glUniform3f(colorLoc, 1.0, 1.0, 0.0)
        glBindVertexArray(self.sunVao)
        self.positionGeometry(self.sun)
        glDrawArrays(GL_TRIANGLES, 0, self.sun.vertexCount)

        self.earth.rotationAngle += self.earthRotationSpeed
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.earthTexture.texture)
        glUniform3f(colorLoc, 0.0, 0.5, 1.0)
        glBindVertexArray(self.earthVao)
        self.updateEarthPosition()
        self.positionGeometry(self.earth)
        glDrawArrays(GL_TRIANGLES, 0, self.earth.vertexCount)

        self.moon.rotationAngle += self.moonRotationSpeed
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.moonTexture.texture)
        glUniform3f(colorLoc, 0.7, 0.7, 0.7)
        glBindVertexArray(self.moonVao)
        self.updateMoonPosition()
        self.positionGeometry(self.moon)
        glDrawArrays(GL_TRIANGLES, 0, self.moon.vertexCount)

        # Swap the front and back buffers on the window, effectively putting what we just "drew"
        # Onto the screen (whereas previously it only existed in memory)
        pg.display.flip()


    def positionGeometry(self, geometry):
        transform_matrix = pyrr.matrix44.create_identity(dtype=np.float32)
        transform_matrix = pyrr.matrix44.multiply(
            m1 = transform_matrix,
            m2 = pyrr.matrix44.create_from_scale(
                scale=geometry.scale,
                dtype=np.float32
            )
        )

        transform_matrix = pyrr.matrix44.multiply(
            m1=transform_matrix,
            m2=pyrr.matrix44.create_from_z_rotation(
                theta=np.radians(180),
                dtype=np.float32
            )
        )

        transform_matrix = pyrr.matrix44.multiply(
            m1 = transform_matrix,
            m2 = pyrr.matrix44.create_from_translation(
                vec=geometry.position,
                dtype=np.float32
            )
        )

        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, transform_matrix)


    def updateEarthPosition(self):
        orbit_offset = 0.6
        self.earth.position[0] = np.sin(self.earth.rotationAngle) * orbit_offset + self.sun.position[0]
        self.earth.position[1] = np.cos(self.earth.rotationAngle) * orbit_offset + self.sun.position[1]
        self.earth.position[2] = -3.0

    def updateMoonPosition(self):
        orbit_offset = 0.2
        self.moon.position[0] = np.sin(self.moon.rotationAngle) * orbit_offset + self.earth.position[0]
        self.moon.position[1] = np.cos(self.moon.rotationAngle) * orbit_offset + self.earth.position[1]
        self.moon.position[2] = -3.0

    def cleanup(self):
        glDeleteVertexArrays(1, (self.sunVao,))
        glDeleteVertexArrays(1, (self.earthVao,))
        self.sunTexture.cleanup()
        self.earthTexture.cleanup()
        self.moonTexture.cleanup()
        self.sun.cleanup()
        self.earth.cleanup()
        self.moon.cleanup()
