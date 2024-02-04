
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

        self.create_texture(name="dither", size=size, components=components)
        self.crete_texture(name="quantise", size=size, components=components)
        self.create_framebuffer(name="dither", attachments=[self.textures["dither"]])
        self.create_framebuffer(name="quantise", attachments=[self.textures["quantised"]])


    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, colours:list="None", **uniforms):

        texture.use(location=0)
        ColourQuantise(size=self.size, components=self.components).run(texture=texture, output=self.framebuffers["quantise"], colours=colours)

        texture.use(location=0)
        self.sample_framebuffer(framebuffer="quantise", location=1)
        self.render_direct(program="dither", vao="dither", framebuffer=self.framebuffers["dither"], uOriginal=0, uQuantised=1)

        # Write to output
        output.color_attachments[0].write(self.framebuffers["dither"].color_attachments[0].read())
        self.close()





