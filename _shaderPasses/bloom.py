
from _shaderPasses._lib import ShaderPass
import moderngl as mgl

from _shaderPasses.gaussianBlur import GaussianBlur
from _shaderPasses.contrast import Contrast

class Bloom(ShaderPass):
    def __init__(self, ctx:mgl.Context, size:tuple, components:int=4):
        super().__init__(ctx=ctx)
        self.size:       tuple = size
        self.components: int   = components

        self.load_shaders(paths=(
            r"_shaderPasses\__bloom.frag",
        ))

        self.create_program(name="bloom", vert=self.shaders["vert"]["__base_vert"], frag=self.shaders["frag"]["__bloom"]) 
        self.create_vao(name="bloom", program="bloom", buffer="base", args=["2f 2f", "bPos", "bTexCoord"])

        self.create_texture(name="blur",       size=size, components=components)
        self.create_texture(name="contrast",   size=size, components=components)
        self.create_texture(name="bloom", size=size, components=components)

        self.create_framebuffer(name="blur",     attachments=[self.textures["blur"]])
        self.create_framebuffer(name="contrast", attachments=[self.textures["contrast"]])
        self.create_framebuffer(name="bloom",    attachments=[self.textures["bloom"]])

    def __name__(self):
        return "Bloom Program"

    def run(self, texture:mgl.Texture, output:mgl.Texture, strength:float=1.0, threshold:float=1.0, x:int=1, **uniforms):

        # Create blur/contrast textures
        Contrast(ctx=self.ctx, size=self.size, components=self.components).run(texture=texture, output=self.framebuffers["contrast"], strength=strength, threshold=threshold)
        GaussianBlur(ctx=self.ctx, size=self.size, components=self.components).run(texture=self.framebuffers["contrast"].color_attachments[0], output=self.framebuffers["blur"], x=x)

        # Create bloom texture
        texture.use(location=0)
        self.sample_framebuffer(framebuffer="blur", location=1)
        self.render_direct(program="bloom", vao="bloom", framebuffer=self.framebuffers["bloom"], uTexture=0, uBlur=1)

        # Write to output
        output.color_attachments[0].write(data=self.framebuffers["bloom"].color_attachments[0].read())





