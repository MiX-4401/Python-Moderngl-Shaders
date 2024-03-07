
from _shaderPasses._lib import ShaderPass
import moderngl as mgl

from _shaderPasses.greyScale import GreyScale
from _shaderPasses.gaussianBlur import GaussianBlur

class SobelFilter(ShaderPass):
    def __init__(self, ctx:mgl.Context, size:tuple, components:int=4):
        super().__init__(ctx=ctx)
        self.size:     tuple = size
        self.components: int = components

        self.load_shaders(paths=(
            r"_shaderPasses\__sobel_filter.frag",
        ))

        self.create_program(name="sobel", vert=self.shaders["vert"]["__base_vert"], frag=self.shaders["frag"]["__sobel_filter"])
        self.create_vao(name="sobel", program="sobel", buffer="base", args=["2f 2f", "bPos", "bTexCoord"])

        self.create_texture(name="sobel",     size=size, components=components)
        self.create_texture(name="greyscale", size=size, components=components)
        self.create_texture(name="gaussian",  size=size, components=components)
        self.create_framebuffer(name="sobel",     attachments=[self.textures["sobel"]])
        self.create_framebuffer(name="greyscale", attachments=[self.textures["greyscale"]])
        self.create_framebuffer(name="gaussian",  attachments=[self.textures["gaussian"]])

        self.add_shaderpass("greyscale", GreyScale)
        self.add_shaderpass("gaussian", GaussianBlur)

    def __name__(self):
        return "SobelFilter Program"

    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, threshold:float=1.0, blur_strength:tuple=(1,3,3), **uniforms):

        # Added shennanigns
        texture.use(location=0)
        self.shader_passes["greyscale"].run(
            texture=texture,
            output=self.framebuffers["greyscale"]
        )

        self.sample_framebuffer(framebuffer="greyscale", location=0)
        self.shader_passes["gaussian"].run(
            texture=self.textures["greyscale"],
            output=self.framebuffers["gaussian"],
            x_strength=blur_strength[1], y_strength=blur_strength[2], x=blur_strength[0]
        )

        self.sample_framebuffer(framebuffer="gaussian", location=0)
        self.render_direct(program="sobel", vao="sobel", framebuffer=self.framebuffers["sobel"], uTexture=0, uResolution=texture.size, uThreshold=float(threshold))

        # Write to output
        output.color_attachments[0].write(data=self.framebuffers["sobel"].color_attachments[0].read())
        




