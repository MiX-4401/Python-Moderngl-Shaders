"""
Author: Ethan.R
Date: 14th November 2023
"""

from _lib import Main
import moderngl as mgl

class ShaderProgram(Main):

    program_frag: str = """
    # version 460 core

    uniform sampler2D myTexture;
    in vec2 uvs; 
    out vec4 fColour;

    void main(){

        vec4 colour = texture(myTexture, uvs).rgba;
        
        fColour = vec4(uvs.x, uvs.y, 1.0, colour.a);
    }
"""

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, components:int=3, method:str="nearest", path:str="None", url:str="None"):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle, components=components, method=method)

        self.load_program()
        
        # Create shader program
        self.new_program: mgl.Program     = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.program_frag)
        self.new_vao:     mgl.VertexArray = self.ctx.vertex_array(self.new_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])
        self.new_texture: mgl.Texture     = self.ctx.texture(size=self.my_texture.size, components=4)
        self.framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.new_texture])

        # Render shader
        self.framebuffer.use()
        self.my_texture.use(location=0)
        self.new_program["myTexture"] = 0
        self.new_vao.render(mgl.TRIANGLE_STRIP)

        self.framebuffer.color_attachments[0].use(location=0)
        self.main_program["myTexture"] = 0

    @Main.d_garbage_cleanup
    def garbage_cleanup(self):
        self.new_texture.release()
        self.framebuffer.release()
        self.new_program.release()
        self.new_vao.release()

ShaderProgram(
    url=r"https://images.fineartamerica.com/images/artworkimages/medium/1/a-kittens-helping-hand-on-a-transparent-background-terri-waters-transparent.png",
    caption="15/11/23",
    swizzle="RGBA",
    scale=1
).run()