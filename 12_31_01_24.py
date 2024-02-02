"""
Author: Ethan.R
Date of Creation: 31st January 2024
Date of Release: NA
Name of Program: NA
"""


from _lib import Main
import moderngl as mgl
import pygame

from shaderPasses.gaussianBlur import GaussianBlur

class ShaderProgram(Main):
    program_frag: str = """
# version 460 core

uniform sampler2D myTexture;


in vec2 uvs;
out vec4 fColour;

void main(){
    vec4 colour = texture(myTexture, uvs).rgba;

    fColour = vec4(colour.rgb, colour.a);
}
"""

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, components:int=3, method:str="nearest", path:str="None", url:str="None"):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle, components=components, method=method)

        self.load_program()

        # Load render target texture
        self.new_texture: mgl.Texture     = self.ctx.texture(size=self.start_texture.size, components=4)
        self.new_texture.filter: tuple    = (mgl.NEAREST, mgl.NEAREST)
        self.framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.new_texture])

        # Create shader program
        self.my_program: mgl.Program     = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.program_frag)
        self.my_vao:     mgl.VertexArray = self.ctx.vertex_array(self.my_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])

    
    def garbage_cleanup(self):
        super().garbage_cleanup() # A better way then using decorators in this context
        self.my_program.release()
        self.my_vao.release()
        self.framebuffer.release()
        self.new_texture.release()

    @Main.d_update
    def update(self):
        pass

    @Main.d_draw
    def draw(self):
        
        # Ready render target
        self.framebuffer.use()
        
        # Set uniforms
        self.start_texture.use(location=0)
        self.my_program["myTexture"] = 0
        
        # Render start_texture with my_program to final_texture
        self.my_vao.render(mgl.TRIANGLE_STRIP)

        # Shader pass
        self.framebuffer = ColourInvert(ctx=self.ctx).run(framebuffer=self.framebuffer)

        # Clear screen
        self.ctx.screen.clear(red=0.0, green=0.0, blue=0.0, alpha=1.0)
        self.ctx.screen.use()

        # Render final_texture to screen
        self.framebuffer.color_attachments[0].use(location=0)
        self.main_program["myTexture"] = 0

if __name__ == "__main__":
    shader_program: ShaderProgram = ShaderProgram(
        caption="NA",
        swizzle="RGBA",
        scale=1,
        flip=False,
        components=4,
        path=r"_images\0NormalWall.png"
    ).run()