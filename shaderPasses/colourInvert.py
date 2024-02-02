
from __shaderPasses._lib import ShaderPass
import moderngl as mgl


class ColourInvert(ShaderPass):
    def __init__(self, ctx:mgl.Context):
        super().__init__(ctx=ctx)

        self.load_shaders(paths=(
            r"_shaderPasses\__colour_invert.frag",
        ))

        self.create_program(name="invert", vert=self.shaders["vert"]["_base_vert"], frag=self.shaders["frag"]["_colour_invert"])
        self.create_vao(name="invert", program=self.programs["invert"], buffer=self.buffers["base"], args=["2f 2f", "bPos", "bTexCoord"])

    def run(self, framebuffer:mgl.Framebuffer, **uniforms):
        return self.render_direct(program="invert", vao="invert", framebuffer=framebuffer)