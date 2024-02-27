
from _shaderPasses._lib import ShaderPass
import moderngl as mgl


class SobelFilter(ShaderPass):
    def __init__(self, ctx:mgl.Context, size:tuple, components:int=4):
        super().__init__(ctx=ctx)

        self.load_shaders(paths=(
            r"_shaderPasses\__sobel_filter.frag",
        ))

        self.create_program(name="sobel", vert=self.shaders["vert"]["__base_vert"], frag=self.shaders["frag"]["__sobel_filter"])
        self.create_vao(name="sobel", program="sobel", buffer="base", args=["2f 2f", "bPos", "bTexCoord"])

        self.create_texture(name="sobel", size=size, components=components)
        self.create_framebuffer(name="sobel", attachments=[self.textures["sobel"]])


    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, **uniforms):

        # Added shennanigns
        texture.use(location=0)
        self.render_direct(program="sobel", vao="sobel", framebuffer=self.framebuffers["sobel"], uTexture=0)

        # Write to output
        output.color_attachments[0].write(data=self.framebuffers["sobel"].color_attachments[0].read())
        self.close()





