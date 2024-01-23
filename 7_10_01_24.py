"""
Author: Ethan.R
Date of Creation: 7th January 2025
Date of Release: NA
Name of Creation: SDF
"""


from _lib import Main
import moderngl as mgl
import pygame

class ShaderProgram(Main):
    program_frag: str = """
# version 460 core

uniform vec2 uResolution;
uniform vec2 uMousePos;

out vec4 fColour;

// SDF Functions
float sdfCircle(vec2 pos, float radius){
    return length(pos) - radius;
}

float sdfBox(vec2 pos, vec2 radius){
    vec2 distance = abs(pos) - radius;
    return length(max(distance, 0.0)) + min(max(distance.x, distance.y), 0.0);
}

float sdfSegment(vec2 p, vec2 point1, vec2 point2){
    vec2 pa = p - point1;
    vec2 ba = point2 - point1;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h);
}

void main(){

    vec2 uvs = gl_FragCoord.xy/uResolution.xy;
    vec2 mousePos = uMousePos/uResolution;

    // Create a Signed Distance Field Shape
    float distanceToShape = sdfCircle(uvs - mousePos, 0.1);
    //float distanceToShape = sdfBox(uvs - mousePos, vec2(0.2, 0.1));
    //float distanceToShape = sdfSegment(uvs - mousePos, vec2(0.1, 0.1), vec2(0.5, 0.1));


    vec3 colour = vec3(distanceToShape / 0.05);
    fColour = vec4(colour.rgb, 1.0);
}
"""

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, components:int=3, method:str="nearest", path:str="None", url:str="None", headless:bool=False):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle, components=components, method=method, headless=headless)

        self.load_program()

        # Load render target texture
        self.new_texture: mgl.Texture     = self.ctx.texture(size=self.my_texture.size, components=4)
        self.new_texture.filter: tuple    = (mgl.NEAREST, mgl.NEAREST)
        self.framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.new_texture])

        # Create shader program
        self.new_program: mgl.Program     = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.program_frag)
        self.new_vao:     mgl.VertexArray = self.ctx.vertex_array(self.new_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])

    @Main.d_update
    def update(self):
        
        self.new_program["uResolution"] = self.screen.get_size()
        self.new_program["uMousePos"]   = pygame.mouse.get_pos()

    def garbage_cleanup(self):
        super().garbage_cleanup() # A better way then using decorators in this context
        self.new_program.release()
        self.new_program.release()
        self.framebuffer.release()
        self.new_vao.release()
        self.new_texture.release()

    @Main.d_draw
    def draw(self):
        self.framebuffer.use()
        self.new_vao.render(mgl.TRIANGLE_STRIP)

        self.ctx.screen.clear(red=0.0, green=0.0, blue=0.0, alpha=1.0)
        self.ctx.screen.use()

        self.framebuffer.color_attachments[0].use(location=0)
        self.main_program["myTexture"] = 0


if __name__ == "__main__":
    shader_program: ShaderProgram = ShaderProgram(
        caption="NA",
        swizzle="RGBA",
        scale=1.0,
        flip=True,
        components=4,
        path=r"images\0NormalWall.png"
    ).run()