import glfw
import sys
from OpenGL.GL import *

from modelo import *  
from controlador import Controller
import grafica.text_renderer as tx

if __name__ == '__main__':

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 700
    height = 700

    window = glfw.create_window(width, height, 'Flappy cow', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controlador = Controller()

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controlador.on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline=es.SimpleTextureTransformShaderProgram()
    #texturePipeline = es.SimpleTextureShaderProgram()
    textPipeline = tx.TextureTextRendererShaderProgram()

    # Telling OpenGL to use our shader program
    #glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0, 0.8, 0, 1.0) #green

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # HACEMOS LOS OBJETOS
    background = BackgroundCreator()
    bird = Cow(pipeline)
    pipe = LogCreator()

    controlador.set_model(bird)
    controlador.set_pipe(pipe)

    t0 = 0
    t1 = 0

    while not glfw.window_should_close(window):  # Dibujando --> 1. obtener el input

        # Calculamos el dt
        ti = glfw.get_time()
        dt = ti - t0
        t0 = ti

        if controlador.pause or bird.counter(pipe)=='WIN':
            dt = 0.0
        elif ti>= t1+1.5:
            background.create_background(pipeline)
            pipe.create_log(pipeline)
            t1=ti

        # Using GLFW to check for input events
        glfw.poll_events()  # OBTIENE EL INPUT --> CONTROLADOR --> MODELOS

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        background.update(dt)
        pipe.update(0.6 * dt)  # 0.001
        bird.update(dt)
        
        # Reconocer la logica
        bird.collide(pipe)
        bird.counter(pipe)

        if bird.counter(pipe)=='WIN': dt= 0.0

        # Enabling transparencies
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(pipeline.shaderProgram)
        background.draw(pipeline)
        
        # DIBUJAR LOS MODELOS
        glUseProgram(pipeline.shaderProgram)
        bird.draw(pipeline)
        glUseProgram(pipeline.shaderProgram)
        pipe.draw(pipeline)


        ############# CONTADOR ##############
        glDisable(GL_BLEND)
        # Creating texture with all characters
        textBitsTexture = tx.generateTextBitsTexture()
        # Moving texture to GPU memory
        gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)

        headerText = bird.counter(pipe)
        headerCharSize = 0.1
        headerCenterX = 0
        headerShape = tx.textToShape(headerText, headerCharSize, headerCharSize)
        gpuHeader = es.GPUShape().initBuffers()
        textPipeline.setupVAO(gpuHeader)
        gpuHeader.fillBuffers(headerShape.vertices, headerShape.indices, GL_STATIC_DRAW)
        gpuHeader.texture = gpuText3DTexture
        headerTransform = tr.matmul([tr.translate(0, 0.5, 0)])

        glUseProgram(textPipeline.shaderProgram)
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 0,0,0,0)
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0,0.8,0,0)
        glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, headerTransform)
        textPipeline.drawCall(gpuHeader)

        ########################################

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()
