"""
Author: Ethan.R
Date of Creation: 11th January 2024
Date of Release: NA
Name of Program: Interactive Rain Effect
"""


from _lib import Main
import moderngl as mgl
import pygame

class ShaderProgram(Main):
    program_rain_frag: str = """
# version 460 core

uniform sampler2D myTexture;
uniform float uTime;
uniform vec2 uResolution;

in  vec2 uvs;
out vec4 fColour;

float time = uTime * 0.004;
vec2 pixel_uv = floor(uvs * uResolution/4) / (uResolution/4);

vec4 colour1 = vec4(81.0/225.0, 179.0/225.0, 214.0/225.0, 1.0);
vec4 colour2 = vec4(70.0/225.0, 126.0/225.0, 214.0/225.0, 1.0);
vec4 colour3 = vec4(50.0/225.0, 82.0/225.0,  209.0/225.0, 1.0);
vec4 colour4 = vec4(29.0/225.0, 48.0/225.0,  122.0/225.0, 1.0);


void main(){

    vec3 displace = texture(myTexture, vec2(pixel_uv.x, (pixel_uv.y + time) * 0.05)).rgb;

    vec2 temp_uv = pixel_uv;
    temp_uv.y *= 0.1;
    temp_uv.y += time;
    vec4 colour = texture(myTexture, temp_uv + displace.xy);

    vec4 noise  = floor(colour * 10.0) / 5.0;
    vec4 bright = mix(colour1, colour2, uvs.y);
    vec4 dark   = mix(colour3, colour4, uvs.y);
    colour      = mix(dark, bright, noise);

    // Gradient 
    colour -= 0.45 * pow(pixel_uv.y, 8.0);
    colour += 0.5 * pow(1.0 - pixel_uv.y, 8.0);


    fColour = vec4(colour.rgb, colour.a);

}
"""

    warp_frag: str = """
# version 460 core

uniform sampler2D myTexture;
uniform vec2 uResolution;
uniform vec2 uMousePos;
uniform float uWarpStrength;

in vec2 uvs;
out vec4 fColour;

float sdfCircle(vec2 pos, float radius, float softness){
    return (length(pos) - radius / softness);
}

void main(){

    vec2 mousePos = uMousePos/uResolution;
    vec2 absUv = gl_FragCoord.xy/uResolution;

    float distance = sdfCircle(absUv - mousePos, 0.1, 0.05);

    vec2 warp = absUv + normalize(absUv - mousePos) * uWarpStrength * smoothstep(0.0, 0.05, abs(distance));
    
    vec4 colour = texture(myTexture, warp).rgba; 

    fColour = vec4(colour.rgb, colour.a);
    //fColour = vec4(uvs.x, uvs.y, 1.0, 1.0);
}

"""

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, components:int=3, method:str="nearest", path:str="None", url:str="None"):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle, components=components, method=method)

        self.load_program()

         # Load render target texture
        self.new_texture: mgl.Texture     = self.ctx.texture(size=self.my_texture.size, components=4)
        self.new_texture.filter: tuple    = (mgl.NEAREST, mgl.NEAREST)
        self.framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.new_texture])

        # Create shader program
        self.rain_program: mgl.Program     = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.program_rain_frag)
        self.rain_vao:     mgl.VertexArray = self.ctx.vertex_array(self.rain_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])

        self.warp_program:  mgl.Program     = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.warp_frag)
        self.warp_vao:      mgl.VertexArray = self.ctx.vertex_array(self.warp_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])



    @Main.d_update
    def update(self):
        self.rain_program["uTime"]       = self.time
        self.rain_program["uResolution"] = self.screen.get_size()
        self.warp_program["uResolution"] = self.screen.get_size()
        self.warp_program["uMousePos"]   = pygame.mouse.get_pos()
        self.warp_program["uWarpStrength"] = 0.1


    def garbage_cleanup(self):
        super().garbage_cleanup() # A better way then using decorators in this context
        self.rain_program.release()
        self.framebuffer.release()
        self.rain_vao.release()
        self.new_texture.release()
        self.warp_program.release()
        self.warp_vao.release()

    @Main.d_draw
    def draw(self):
        self.framebuffer.use()
        self.my_texture.use(location=0)
        self.rain_program["myTexture"] = 0
        self.rain_vao.render(mgl.TRIANGLE_STRIP)

        self.framebuffer.color_attachments[0].use(location=0)
        self.warp_program["myTexture"] = 0
        self.warp_vao.render(mgl.TRIANGLE_STRIP)

        self.ctx.screen.clear(red=0.0, green=0.0, blue=0.0, alpha=1.0)
        self.ctx.screen.use()

        self.framebuffer.color_attachments[0].use(location=0)
        self.main_program["myTexture"] = 0


if __name__ == "__main__":    
    shader_program: ShaderProgram = ShaderProgram(
        caption="Rain Effect",
        swizzle="RGBA",
        scale=0.5,
        flip=True,
        components=4,
        method="linear",
        url="https://ragingnexus.com/assets/86c5a3-e4598871c3b71818c250cbb80c6ce1c08fbf501dc381137e0ebedd4951f0e946d0ef90d16201c054be9f3dce44b7234b3dc7572973665b2b3945e2dce784ded7.png",
    ).run()