
from _shaderPasses._lib import ShaderPass
import moderngl as mgl


class ColourInvert(ShaderPass):
    def __init__(self, ctx:mgl.Context):
        super().__init__(ctx=ctx)

        self.load_shaders(paths=(
            r"_shaderPasses\__colour_invert.frag",
        ))

        self.create_program(name="invert", vert=self.shaders["vert"]["__base_vert"], frag=self.shaders["frag"]["__colour_invert"])
        self.create_vao(name="invert", program=self.programs["invert"], buffer=self.buffers["base"], args=["2f 2f", "bPos", "bTexCoord"])
        self.create_framebuffer(name="invertColour")

    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, **uniforms):
        
        # Render
        self.render_direct(program="invert", vao="invert", framebuffer=self.framebuffers["invertColour"])
        
        # Write to output
        output.write(self.framebuffers["invertColour"].color_attachments[0].read())