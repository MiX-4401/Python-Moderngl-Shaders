
from __shaderPasses._lib import ShaderPass
import moderngl as mgl


class myshader(ShaderPass):
    def __init__(self, ctx:mgl.Context):
        super().__init__(ctx=ctx)

        self.load_shaders(paths=(
            "",
        ))


    def run(self, framebuffer:mgl.Framebuffer, **uniforms):

        # Added shennanigns

        # Render
        return self.render_direct(program="", vao="", framebuffer=framebuffer)





