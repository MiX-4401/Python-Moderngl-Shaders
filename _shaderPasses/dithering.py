
from _shaderPasses._lib import ShaderPass
import moderngl as mgl

from _shaderPasses.colourQuantise import ColourQuantise

class Dithering(ShaderPass):
    def __init__(self, ctx:mgl.Context, size:tuple, components:int=4):
        super().__init__(ctx=ctx)
        self.size:     tuple = size
        self.components: int = components

        self.load_shaders(paths=(
            r"_shaderPasses\__ordered_dither.frag",
        ))

        self.create_program(name="dither", vert=self.shaders["vert"]["__base_vert"], frag=self.shaders["frag"]["__ordered_dither"])
        self.create_vao(name="dither", program="dither", buffer="base", args=["2f 2f", "bPos", "bTexCoord"])

        self.create_texture(name="dither",    size=size, components=components)
        self.create_texture(name="quantise1", size=size, components=components)
        self.create_texture(name="quantise2", size=size, components=components)
        self.create_framebuffer(name="dither",    attachments=[self.textures["dither"]])
        self.create_framebuffer(name="quantise1", attachments=[self.textures["quantise1"]])
        self.create_framebuffer(name="quantise2", attachments=[self.textures["quantise2"]])


    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, colours:list=[(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)], bayer:int=1, **uniforms):

        # Validation checks

        # Get closest colour quantised textures 
        texture.use(location=0)
        ColourQuantise(ctx=self.ctx, size=self.size, components=self.components).run(texture=texture, output=self.framebuffers["quantise1"], closeness=0, colours=colours, uResolution=texture.size)
        ColourQuantise(ctx=self.ctx, size=self.size, components=self.components).run(texture=texture, output=self.framebuffers["quantise2"], closeness=1, colours=colours, uResolution=texture.size)

        # Get dither texture
        self.sample_framebuffer(framebuffer="quantise1", location=1)
        self.sample_framebuffer(framebuffer="quantise2", location=2)
        self.render_direct(program="dither", vao="dither", framebuffer=self.framebuffers["dither"], uOriginal=0, uClosest=1, uSecond=2, uBayer=bayer)

        # Write to output
        output.color_attachments[0].write(self.framebuffers["dither"].color_attachments[0].read())
        self.close()





