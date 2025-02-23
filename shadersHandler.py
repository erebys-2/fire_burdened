import pygame
import sys

import moderngl
from array import array #standard python lib for arrays

#goals:
#1. use pygame normally to make surfaces
#2. turn the final surface into an opengl texture
#3. render the texture w/ shaders
#4. take the w

class modernGL_handler():
    def __init__(self):
        self.ctx = moderngl.create_context()#creating context!
        #f is for float in the array
        quad_buffer = self.ctx.buffer(data = array('f', [#creates 2 right triangles to form a rectangle
            #pos (x,y), uv coords (x,y)
            -1.0, 1.0, 0.0, 0.0,    #top left
            1.0, 1.0, 1.0, 0.0,     #top right, there's a flip in the UV coords?
            -1.0, -1.0, 0.0, 1.0,   #bottom left
            1.0, -1.0, 1.0, 1.0,     #bottom right
        ]))

        #shaders written in glsl, but it gets loaded via string from python
        vert_shader = '''
        #version 330 core

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(vert, 0.0, 1.0);
        }
        '''
        #generates geometry to be filled in by fragment shader
        # vert_shader = ''' annotated
        # #version 330 core

        # in vec2 vert; #these are the inputs
        # in vec2 texcoord;
        # out vec2 uvs; #this is what it returns

        # void main() {
        #     uvs = texcoord;
        #     gl_Position = vec4(vert.x, vert.y, 0,0, 1.0); #vec 4: tuple of 4, 3rd number: z, last number: math stuff/homogenous coord
        # }
        # '''

        frag_shader = '''
        #version 330 core

        uniform sampler2D tex;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            f_color = vec4(texture(tex, uvs).rgb, 1.0);
        }
        '''
        #runs for every pixel on screen
        # frag_shader = ''' annotated
        # #version 330 core

        # uniform sampler2D tex; #value sustained per cycle, samples value from a texture

        # in vec2 uvs;  #new for every cycle
        # out vec f_color;

        # void main() { #sample texture w/ coordinates then use color from texture to apply to output coor
        #     f_color = vec4(textures(tex, uvs).rgb. 1.0) #.rgb or .xyz formats into 3 variables
        # }
        # '''
        self.program = ''
        self.render_object = ''
        self.set_render_obj(quad_buffer, vert_shader, frag_shader)
        
        
    def set_render_obj(self, quad_buffer, vert_shader, frag_shader):
        #shader program, has the shaders
        self.program = self.ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)

        #create render obj
            #2nd arg is the array, the 2f2f is saying vert is 2f and texcoord is 2f, basically how to interpret
            # vert and texcoord need to match the names in the shader
        self.render_object = self.ctx.vertex_array(self.program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')]) 

    def surf_to_texture(self, surface):
        tex = self.ctx.texture(surface.get_size(), 4)#scaling
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)#
        tex.swizzle = 'BGRA' #pygame maps colors differently
        tex.write(surface.get_view('1')) #generates a lower level output for surface, 1 is a format
        return tex
                
            
    