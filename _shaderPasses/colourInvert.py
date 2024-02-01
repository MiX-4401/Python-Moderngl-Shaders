
from _shaderPasses._lib import ShaderPass
import moderngl as mgl


class ColourInvert(ShaderPass):
    def __init__(self, ctx:mgl.Context, **uniforms):
        super().__init__(ctx=ctx, uniforms=uniforms)

        self.load_shaders(paths=(
            r"_shaderPasses\_colour_invert.frag",
        ))

        self.create_program(name="invert", vert=self.shaders["vert"]["_base_vert"], frag=self.shaders["frag"]["_colour_invert"])
        self.create_vao(name="invert", program=self.programs["invert"], buffer=self.buffers["base"], args=["2f 2f", "bPos", "bTexCoord"])


    def run(self, framebuffer:mgl.Framebuffer):
        return self.render_direct(program="invert", vao="invert", framebuffer=target)