
from _shaderPasses._lib import ShaderPass
import moderngl as mgl


class SobelFilter(ShaderPass):
    def __init__(self, ctx:mgl.Context, size:tuple, components:int=4):
        super().__init__(ctx=ctx)

        self.load_shaders(paths=(
            r"_shaderPasses\__contrast.frag",
        ))

        self.create_program(name="contrast", vert=self.shaders["vert"]["__base_vert"], frag=self.shaders["frag"]["__contrast"])
        self.create_vao(name="contrast", program="contrast", buffer="base", args=["2f 2f", "bPos", "bTexCoord"])

        self.create_texture(name="contrast", size=size, components=components)
        self.create_framebuffer(name="contrast", attachments=[self.textures["contrast"]])


    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, strength:float=1.0, threshold:float=1.0, **uniforms):

        # Added shennanigns
        texture.use(location=0)
        self.render_direct(program="contrast", vao="contrast", framebuffer=self.framebuffers["contrast"], uThreshold=threshold, uStrength=strength, uTexture=0)

        # Write to output
        output.color_attachments[0].write(data=self.framebuffers["contrast"].color_attachments[0].read())
        self.close()





