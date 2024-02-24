
from _shaderPasses._lib import ShaderPass
import moderngl as mgl


class CannyEdgeDetection(ShaderPass):
    def __init__(self, ctx:mgl.Context):
        super().__init__(ctx=ctx)

        self.load_shaders(paths=(
            r"_shaderPasses\__canny_edge.frag",
        ))


    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, **uniforms):

        # Added shennanigns

        # Write to output
        output.color_attachments[0].write(self.framebuffers[""].color_attachments[0].read())
        self.close()





