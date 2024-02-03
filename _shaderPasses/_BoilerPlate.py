
from _shaderPasses._lib import ShaderPass
import moderngl as mgl


class myshader(ShaderPass):
    def __init__(self, ctx:mgl.Context):
        super().__init__(ctx=ctx)

        self.load_shaders(paths=(
            "",
        ))


    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, **uniforms):

        # Added shennanigns

        # Write to output
        output.color_attachments[0].write(self.framebuffers[""].color_attachments[0].read())
        self.close()





