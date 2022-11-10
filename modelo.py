from re import L
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.assets_path import getAssetPath
from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES
import numpy as np
from OpenGL.GL import *

import random
from typing import List


def create_gpu(shape, pipeline):
    gpu = GPUShape().initBuffers()
    pipeline.setupVAO(gpu)
    gpu.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpu


class Cow(object):
    
    def __init__(self, pipeline):
        # Figuras básicas
        gpu_cow = create_gpu(bs.createTextureQuad(1, 1), pipeline)
        gpu_cow.texture = es.textureSimpleSetup(
                getAssetPath("vaquitaup.png"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

        cow = sg.SceneGraphNode('cow')
        cow.transform = tr.matmul([tr.scale(0.3, 0.3, 0), tr.translate(-1.5, 0, 0)])
        cow.childs += [gpu_cow]

        cow_tr = sg.SceneGraphNode('cowTR')
        cow_tr.childs += [cow]

        self.model = cow_tr
        self.pos = 0
        self.xi = -0.2
        self.xd = -0.7
        self.vy = 0
        self.y = 0
        self.alive = True

    def draw(self, pipeline):
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')

    def modifymodel(self):
        self.model.transform = tr.translate(0, self.y, 0)

    def update(self, dt):
        g = 1.5
        self.vy += -g*dt
        self.y += self.vy*dt + 0.5*g*dt*dt
        # modificar de manera constante al modelo
        # aqui deberia llamar a tr.translate
        self.modifymodel()

    def jump(self):
        if not self.alive:
            return
        self.vy=1
        image = "vaquitaup.png"

    def collide(self, log: 'LogCreator'):
        if not log.on:  #si el jugador perdió no detecta colisiones
            return

        deleted_log = []
        for l in log.log:
            if l.pos_y==-1:
                if (-1 <= self.y-0.15 <= l.yf and self.xd<=l.pos_x<=self.xi) or self.y <= -0.85:
                #colisiona con la tuberia o con el suelo
                    log.die()
                    self.alive = False #uwu
            elif l.pos_y==1:
                if (l.yf <= self.y+0.15 <= 1 and self.xd<=l.pos_x<=self.xi) or self.y <= -0.85:
                    log.die()
                    self.alive = False 
            elif -0.28 >= l.pos_x >= -0.3 and self.pos != l.pos_y:
                #no colisiona
                deleted_log.append(l)
        log.delete(deleted_log)

    def counter(self, log: 'LogCreator'):
        N=int(sys.argv[1])
        count=0
        if not log.on: return
        for l in log.log:
            if self.alive and self.xd>l.pos_x:
                count+=1
            elif count!='WIN' and not self.alive: count='GAME OVER'
            elif count==N:
                count='WIN'
                break
        return str(count)

class Log(object):

    def __init__(self, pipeline):
        gpu_log = create_gpu(bs.createTextureQuad(1, 1), pipeline) # verde
        gpu_log.texture = es.textureSimpleSetup(
            getAssetPath("dirttt.png"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

        log = sg.SceneGraphNode('log')
        L=random.uniform(1,2.5) #largo de la tubería
        log.transform = tr.scale(0.2, L, 1)
        log.childs += [gpu_log]

        log_tr = sg.SceneGraphNode('logTR')
        log_tr.childs += [log] 

        self.pos_x = 1
        self.pos_y = random.choice([-1, 1])  #aparece una tubería arriba o una abajo
        if self.pos_y==-1:
            if L<2: self.yf=-1+L/2   #posicion en y de una tuberia que aparece abajo
            else: self.yf=-1+L/2
        if self.pos_y== 1:
            if L<2: self.yf= 1-L/2   #posicion en y de una tuberia que aparece arriba
            else: self.yf=1-L/2
        self.model = log_tr

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos_x, self.pos_y, 0)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")

    def update(self, dt):
        self.pos_x -= dt


class LogCreator(object):
    log: List['Log']

    def __init__(self):
        self.log = []
        self.on = True

    def die(self):
        glClearColor(0.8, 0.6, 0, 1)  # el fondo cambia al color de los bloques

    def create_log(self, pipeline):
        self.log.append(Log(pipeline))

    def draw(self, pipeline):
        for k in self.log:
            k.draw(pipeline)

    def update(self, dt):
        for k in self.log:
            k.update(dt)

    def delete(self, d):
        if len(d) == 0:
            return
        remain_log = []
        for k in self.log:  # recorre todas las tuberias
            if k not in d:  # si no se elimina, se añade a la lista de tuberias que quedan
                remain_log.append(k)
        self.log = remain_log  # actualiza la lista

class Background(object):
    def __init__(self,pipeline):
        # Creating shapes on GPU memory
        gpuBackground = create_gpu(bs.createTextureQuad(1,1),pipeline)
        gpuBackground.texture = es.textureSimpleSetup(
            getAssetPath("grass2.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

        background = sg.SceneGraphNode('background')
        background.transform = tr.matmul([tr.scale(2, 2, 1)])
        background.childs += [gpuBackground]

        background_tr = sg.SceneGraphNode('backgroundTR')
        background_tr.childs += [background] 

        self.pos = 0
        self.model = background_tr

    def draw(self, pipeline):
        self.model.transform = tr.translate(self.pos+2, 0, 0)
        sg.drawSceneGraphNode(self.model,pipeline,"transform")

    def update(self,dt):
        self.pos -= 0.6 * dt

class BackgroundCreator(object):
    background: List['Background']

    def __init__(self):
        self.background = []
        self.on = True

    def die(self):
        glClearColor(0.8, 0.6, 0, 1)  # el fondo cambia al color de los bloques

    def create_background(self, pipeline):
        self.background.append(Background(pipeline))

    def draw(self, pipeline):
        for k in self.background:
            k.draw(pipeline)

    def update(self, dt):
        for k in self.background:
            k.update(dt)