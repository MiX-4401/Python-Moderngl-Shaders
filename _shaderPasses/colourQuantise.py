
from _shaderPasses._lib import ShaderPass
import moderngl as mgl


class ColourQuantise(ShaderPass):
    def __init__(self, ctx:mgl.Context, size:tuple, components:int=4):
        super().__init__(ctx=ctx)

        self.load_shaders(paths=(
            r"_shaderPasses\__colour_quantise.frag",
        ))

        self.create_program(name="quantise", vert=self.shaders["vert"]["__base_vert"], frag=self.shaders["frag"]["__colour_quantise"])
        self.create_vao(name="quantise", program="quantise", buffer="base", args=["2f 2f", "bPos", "bTexCoord"])

        self.create_texture(name="quantise", size=size, components=components)
        self.create_framebuffer(name="quantise", attachments=self.textures["quantise"])

    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, colours:list="None", **uniforms):


        texture.use(location=0)

        if type(colours) == list:
            self.render_direct(program="quantise", vao="quantise", framebuffer=self.framebuffers["quantise"], uTexture=0, uPallet=colours, uPalletSize=len(colours))
        else:
            self.render_direct(program="quantise", vao="quantise", framebuffer=self.framebuffers["quantise"], uTexture=0)

        # Write to output
        output.color_attachments[0].write(self.framebuffers["quantise"].color_attachments[0].read())
        self.close()





