
from __shaderPasses._lib import ShaderPass
import moderngl as mgl


class GaussianBlur(ShaderPass):
    def __init__(self, ctx:mgl.Context, size:tuple, data, components:int=4):
        super().__init__(ctx=ctx)

        self.load_shaders(paths=(
            r"_shaderPasses\__gaussian_blur.frag",
        ))


        self.create_program(name="guassianBlur", vertex_shader=self.shaders["vert"]["base"], fragment_shader=self.shaders["frag"]["_gaussian_blur"])
        self.create_vao(name="gaussianBlur", program=self.programs["gaussianBlur"], buffer=self.buffers["base"], args=["2f 2f", "bPos", "bTexCoord"])

        self.create_texture(name="ping", size=size, components=components, data=data)
        self.create_texture(name="pong", size=size, components=components)
        self.create_framebuffer(name="ping", attachments=[self.textures["ping"]])
        self.create_framebuffer(name="pong", attachments=[self.textures["pong"]])


    def run(self, framebuffer:mgl.Framebuffer, **uniforms):

        # Added shennanigns
        self.sample_framebuffer(framebuffer="ping")
        self.framebuffers["pong"] = self.render_direct(program="guassianBlur", vao="guassianBlur", framebuffer=self.framebuffers["ping"], uTexture=0, horizontal=True)

        self.sample_framebuffer(framebuffer="pong")
        self.framebuffers["ping"] = self.render_direct(program="gaussianBlur", vao="gaussianBlur", framebuffer=self.framebuffers["pong"], uTexture=0, horizontal=False)

        # Render
        return self.render_direct(program="", vao="", framebuffer=framebuffer)





