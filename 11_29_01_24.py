"""
Author: Ethan.R
Date of Creation: 29th January 2024
Date of Release: NA
Name of Program: Hiding Bilby
"""


from _lib import Main
import moderngl as mgl
import pygame

class ShaderProgram(Main):
    program_frag: str = """
# version 460 core

uniform sampler2D uTexture;
uniform sampler2D uCoverTexture;
uniform vec2 uResolution;
uniform vec2 uMousePos;
uniform float uTime;

in vec2 uvs;
out vec4 fColour;

float sdfCircle(vec2 pos, float radius, float hardness){
    return (length(pos) - radius) * hardness;
}

void main(){
    vec2 uv = gl_FragCoord.xy/uResolution;
    vec2 mousePos = uMousePos/uResolution;

    vec3 colour      = texture(uTexture, uvs).rgb;
    vec3 coverColour = texture(uCoverTexture, uvs).rgb;

    float distance = sdfCircle(uv - mousePos, 0.1, 10.0);

    if (distance < 1.0){
        colour.r += uvs.y * (sin(uTime * 0.004)  * coverColour.r);
        colour.g += uvs.x * (sin(uTime * 0.008)  * coverColour.g);
        colour.b += uvs.x * (sin(uTime * 0.0012) * coverColour.b);
    }
    
    fColour = vec4(colour.rgb, 1.0);
}
"""

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, components:int=3, method:str="nearest", path:str="None", url:str="None"):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle, components=components, method=method)

        self.load_program()

        # Load render target texture
        self.final_texture: mgl.Texture     = self.ctx.texture(size=self.my_texture.size, components=4)
        self.final_texture.filter: tuple    = (mgl.NEAREST, mgl.NEAREST)
        self.framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.final_texture])

        self.cover_texture: mgl.Texture  = self.get_texture_from_data(image_data=self.get_image_from_file(path=r"images\3TextureBilby.png", scale=0.25, flip=True))
        self.cover_texture.filter: tuple = (mgl.NEAREST, mgl.NEAREST)

        # Create shader program
        self.new_program: mgl.Program     = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.program_frag)
        self.new_vao:     mgl.VertexArray = self.ctx.vertex_array(self.new_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])

    @Main.d_update
    def update(self):
        self.new_program["uResolution"] = self.screen.get_size()
        self.new_program["uMousePos"]   = pygame.mouse.get_pos()
        self.new_program["uTime"]   = self.time

    def garbage_cleanup(self):
        super().garbage_cleanup() # A better way then using decorators in this context
        self.new_program.release()
        self.new_program.release()
        self.framebuffer.release()
        self.new_vao.release()
        self.final_texture.release()
        self.cover_texture.release()

    @Main.d_draw
    def draw(self):
        self.framebuffer.use()

        self.my_texture.use(location=0)
        self.cover_texture.use(location=1)
        self.new_program["uTexture"]      = 0
        self.new_program["uCoverTexture"] = 1
        self.new_vao.render(mgl.TRIANGLE_STRIP)

        self.ctx.screen.clear(red=0.0, green=0.0, blue=0.0, alpha=1.0)
        self.ctx.screen.use()

        self.framebuffer.color_attachments[0].use(location=0)
        self.main_program["myTexture"] = 0


if __name__ == "__main__":
    shader_program: ShaderProgram = ShaderProgram(
        caption="Hiding Bilby",
        swizzle="RGBA",
        scale=1,
        flip=False,
        components=4,
        path=r"images\0TextureWall.png"
    ).run()