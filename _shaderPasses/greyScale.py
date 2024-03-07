
from _shaderPasses._lib import ShaderPass
import moderngl as mgl


class GreyScale(ShaderPass):
    def __init__(self, ctx:mgl.Context, size:tuple, components:int=4):
        super().__init__(ctx=ctx)

        self.load_shaders(paths=(
            r"_shaderPasses\__greyscale.frag",
        ))

        self.create_program(name="greyscale", vert=self.shaders["vert"]["__base_vert"], frag=self.shaders["frag"]["__greyscale"])
        self.create_vao(name="greyscale", program="greyscale", buffer="base", args=["2f 2f", "bPos", "bTexCoord"])

        self.create_texture(name="greyscale", size=size, components=components)
        self.create_framebuffer(name="greyscale", attachments=[self.textures["greyscale"]])

    def __name__(self):
        return "GreyScale Program"

    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, **uniforms):

        # Added shennanigns
        texture.use(location=0)
        self.render_direct(program="greyscale", vao="greyscale", framebuffer=self.framebuffers["greyscale"], uTexture=0)

        # Write to output
        output.color_attachments[0].write(data=self.framebuffers["greyscale"].color_attachments[0].read())





