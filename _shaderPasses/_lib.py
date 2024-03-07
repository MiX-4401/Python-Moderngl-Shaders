
import moderngl as mgl
import numpy

class ShaderPass:
    def __init__(self, ctx: mgl.Context):
        self.ctx: mgl.Context = ctx

        self.shaders: dict = {
            "vert": {},
            "frag": {}
        }

        self.programs: dict = {

        }

        self.vaos: dict = {

        }

        self.buffers: dict = {

        }

        self.framebuffers: dict = {

        }

        self.textures: dict = {

        }

        self.renderbuffers: dict = {

        }

        self.shader_passes: dict = {

        }

        self.load_shaders(paths=(
            r"_shaderPasses\__base_vert.vert",
            r"_shaderPasses\__base_frag.frag"
        ))

        self.load_base_shader()

    def __name__(self):
        return "ShaderPass Program"

    def load_shaders(self, paths:tuple):

        for path in paths:            
            
            name: str; extension: str
            name, extension = path.split("\\")[-1].split(".")
            if extension not in ["vert", "frag"]: raise BaseException("extension not compatible")

            with open(file=path, mode="r") as f:
                data = f.read()
                self.shaders[extension].update({name: data})    

    def load_base_shader(self):
        self.programs.update({
            "base": self.ctx.program(vertex_shader=self.shaders["vert"]["__base_vert"], fragment_shader=self.shaders["frag"]["__base_frag"])
        })
        self.buffers.update({
            "base": self.ctx.buffer(data=numpy.array([-1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, 0.0, 1.0, 1.0, -1.0, 1.0, 1.0], dtype="f4"))
        })
        self.vaos.update({
            "base": self.ctx.vertex_array(self.programs["base"], [(self.buffers["base"], "2f 2f", "bPos", "bTexCoord")])
        })

    def garbage_collection(self):
        for program in self.programs:
            self.programs[program].release()
        for vao in self.vaos:
            self.vaos[vao].release()
        for buffer in self.buffers:
            self.buffers[buffer].release()
        for framebuffer in self.framebuffers:
            self.framebuffers[framebuffer].release()
        for texture in self.textures:
            self.textures[texture].release()
        for program in self.shader_passes:
            self.shader_passes[program].close()

    def create_program(self, name:str, vert: str, frag:str):
        program: mgl.Program = self.ctx.program(vertex_shader=vert, fragment_shader=frag)
        self.programs.update({name: program})

    def create_vao(self, name:str, program:str, buffer:mgl.Buffer, args):
        vao: mgl.VertexArray = self.ctx.vertex_array(self.programs[program], [(self.buffers[buffer], *args)])
        self.vaos.update({name: vao})

    def create_buffer(self, name, array: numpy.array):
        buffer: mgl.Buffer = self.ctx.buffer(data=array)
        self.buffers.update({name: buffer})

    def create_framebuffer(self, name:str, attachments:list=[]):
        framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=attachments)
        self.framebuffers.update({name: framebuffer})

    def create_texture(self, name:str, size:tuple, components:int=4, filter:tuple=(mgl.LINEAR, mgl.LINEAR), data:list="None"):
        texture: mgl.Texture = self.ctx.texture(size=size, components=components)
        texture.filter: tuple = filter
        if data != "None": texture.write(data=data)
        self.textures.update({name: texture})

    def create_renderbuffer(self, name:str, size:tuple, components:int=4):
        renderbuffer: mgl.Texture = self.ctx.renderbuffer(size=size, components=components)
        self.renderbuffers.update({name: renderbuffer})

    def add_shaderpass(self, name:str, shader):
        self.shader_passes[name] = shader(ctx=self.ctx, size=self.size, components=self.components)

    def sample_texture(self, texture:str, location:int=0):
        """
            Sets the sample location for a texture
        """

        self.textures[texture].use(location=location)
        
    def sample_framebuffer(self, framebuffer:str, attachment:int=0, location:int=0):
        """
            Sets the sample location for a framebuffer
        """

        self.framebuffers[framebuffer].color_attachments[attachment].use(location=location)

    def render_direct(self, program:str, vao:str, framebuffer:mgl.Framebuffer, **uniforms):
        """
            Renders the shader directly to the framebuffer
        """

        # Ready framebuffer
        framebuffer.use()
        # self.framebuffers[framebuffer].clear()

        # Set uniforms
        for uniform in uniforms:
            self.programs[program][uniform] = uniforms[uniform]
        
        # Render
        self.vaos[vao].render(mgl.TRIANGLE_STRIP)

        return framebuffer

    def close(self):
        self.garbage_collection()

    def __del__(self):
        self.garbage_collection()






