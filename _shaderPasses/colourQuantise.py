
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

    def __name__(self):
        return "Colour Quantisation Program"

    def normalise(self, colour:tuple) -> tuple:
        return (colour[0]/225, colour[1]/225, colour[2]/225)

    def run(self, texture:mgl.Texture, output:mgl.Framebuffer, closeness:int=0, colours:list=[(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)], **uniforms):

        """
            Returns a colour quantised texture based on the texture input.
            Closeness represents how close new colours will be to the colour pallet (either 0 or 1)
            Closeness defaults to range of 1, therefore uses the closest colour

            Colours   respresent a list of colours contains in tuples in the 0.0 to 1.0 range
            Colours   defaults to 1Bit colour range: white/black 
        """

        normalised_colours: list = [self.normalise(colour=c) for c in colours]

        texture.use(location=0)
        self.render_direct(program="quantise", vao="quantise", framebuffer=self.framebuffers["quantise"], uTexture=0, uCloseness=closeness, uPallet=normalised_colours, uPalletSize=len(colours))

        # Write to output
        output.color_attachments[0].write(self.framebuffers["quantise"].color_attachments[0].read())





