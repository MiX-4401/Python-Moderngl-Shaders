
from _shaderPasses._lib import ShaderPass
import moderngl as mgl


class GaussianBlur(ShaderPass):
    def __init__(self, ctx:mgl.Context, size:tuple, components:int=4):
        super().__init__(ctx=ctx)

        self.load_shaders(paths=(
            r"_shaderPasses\__gaussian_blur.frag",
        ))


        self.create_program(name="gaussianBlur", vert=self.shaders["vert"]["__base_vert"], frag=self.shaders["frag"]["__gaussian_blur"])
        self.create_vao(name="gaussianBlur", program="gaussianBlur", buffer="base", args=["2f 2f", "bPos", "bTexCoord"])

        self.create_texture(name="ping", size=size, components=components, filter=(mgl.NEAREST, mgl.NEAREST))
        self.create_texture(name="pong", size=size, components=components, filter=(mgl.NEAREST, mgl.NEAREST))
        self.create_framebuffer(name="ping", attachments=[self.textures["ping"]])
        self.create_framebuffer(name="pong", attachments=[self.textures["pong"]])

    def __name__(self):
        return "Gaussian Program"

    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, x_strength:int=5, y_strength:int=5, x:int=1, **uniforms):

        """
            2-Pass Gaussian Blur Shader Pass
            Using ping-pong framebuffers/textures to create blur on the xy axies
        """

        # Initial sample
        self.textures["pong"].write(texture.read())
        
        for x in range(x):
            self.sample_framebuffer(framebuffer="pong")
            self.render_direct(program="gaussianBlur", vao="gaussianBlur", framebuffer=self.framebuffers["ping"], uTexture=0, uHorizontal=True, uXStrength=x_strength, uYStrength=y_strength)

            # Rebound sample 
            self.sample_framebuffer(framebuffer="ping")
            self.render_direct(program="gaussianBlur", vao="gaussianBlur", framebuffer=self.framebuffers["pong"], uTexture=0, uHorizontal=False, uXStrength=x_strength, uYStrength=y_strength)

        # Write to output
        output.color_attachments[0].write(self.framebuffers["pong"].color_attachments[0].read())




