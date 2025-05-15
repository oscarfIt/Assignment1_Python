import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import pyrr

from Geometry import *
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

        colorLoc = glGetUniformLocation(self.shader, "objectColor")
        glUniform3f(colorLoc, 1.0, 1.0, 1.0)    # Triangle color, may need to do something different here for getting different colored planets

        glBindVertexArray(self.sunVao)
        self.sun = Sun('./resources/sphere-fixed.txt')
        glBindVertexArray(self.earthVao)
        self.earth = Earth('./resources/sphere-fixed.txt')
        glBindVertexArray(self.moonVao)
        self.moon = Moon('./resources/sphere-fixed.txt')

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
        self.clock.tick(60)

        glBindVertexArray(self.sunVao)
        self.positionGeometry(self.sun)
        glDrawArrays(GL_TRIANGLES, 0, self.sun.vertexCount)

        self.earth.rotationAngle += self.earthRotationSpeed
        glBindVertexArray(self.earthVao)
        self.updateEarthPosition()
        self.positionGeometry(self.earth)
        glDrawArrays(GL_TRIANGLES, 0, self.earth.vertexCount)

        self.moon.rotationAngle += self.moonRotationSpeed
        glBindVertexArray(self.moonVao)
        self.updateMoonPosition()
        self.positionGeometry(self.moon)
        glDrawArrays(GL_TRIANGLES, 0, self.moon.vertexCount)

        # Swap the front and back buffers on the window, effectively putting what we just "drew"
        # Onto the screen (whereas previously it only existed in memory)
        pg.display.flip()


    def positionGeometry(self, geometry):
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        model_transform = pyrr.matrix44.multiply(
            m1 = model_transform,
            m2 = pyrr.matrix44.create_from_scale(
                scale=geometry.scale,
                dtype=np.float32
            )
        )

        model_transform = pyrr.matrix44.multiply(
            m1 = model_transform,
            m2 = pyrr.matrix44.create_from_translation(
                vec=geometry.position,
                dtype=np.float32
            )
        )

        glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_transform)


    def updateEarthPosition(self):
        orbit_offset = 0.5
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
        self.sun.cleanup()
        self.earth.cleanup()
        self.moon.cleanup()
