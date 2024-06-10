
from _shaderPasses._lib import ShaderPass
import moderngl as mgl


class CannyEdgeDetection(ShaderPass):
    def __init__(self, ctx:mgl.Context):
        super().__init__(ctx=ctx)

        self.load_shaders(paths=(
            r"_shaderPasses\__canny_edge.frag",
        ))

        self.create_program(name="canny", vert=self.shaders["vert"]["__base_vert"], frag=self.shaders["frag"]["__canny_edge"])
        self.create_vao(name="canny", program="canny", buffer="base", args=["2f 2f", "bPos", "bTexCoord"])

        self.create_texture(name="canny", size=size, components=components)
        self.create_framebuffer(name="canny", attachments=self.textures["canny"])


    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, **uniforms):

        # Added shennanigns
        

        # Write to output
        output.color_attachments[0].write(self.framebuffers["canny"].color_attachments[0].read())
        self.close()





