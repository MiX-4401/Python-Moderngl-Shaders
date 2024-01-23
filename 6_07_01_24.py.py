"""
Author: Ethan.R
Date of Creation: 7th January 2024
Date of Release: NA
Creation Name: Rain Effect
Source: https://shadered.org/view?s=6Gny24_ojD
"""


from _lib import Main
import moderngl as mgl
import pygame

class ShaderProgram(Main):
    rain_frag: str = """
# version 460 core

uniform sampler2D uNoiseTexture;
uniform sampler2D uSDFTexture;
uniform vec2 uResolution;
uniform float utime;

in vec2 uvs;
out vec4 fColour;

void main(){

    float time  = utime * 0.004;

    vec4 colour1 = vec4(81.0/225.0, 179.0/225.0, 214.0/225.0, 1.0);
    vec4 colour2 = vec4(70.0/225.0, 126.0/225.0, 214.0/225.0, 1.0);
    vec4 colour3 = vec4(50.0/225.0, 82.0/225.0,  209.0/225.0, 1.0);
    vec4 colour4 = vec4(29.0/225.0, 48.0/225.0,  122.0/225.0, 1.0);

    // Pixelate effect
    vec2 uv_pixel = floor(uvs * (uResolution/4)) / (uResolution/4);
    //uv_pixel = uvs;

    vec3 displace = texture(uNoiseTexture, vec2(uv_pixel.x, (uv_pixel.y + sin(time)) * 0.05)).rgb;
    //displace = texture(uNoiseTexture, vec2(uv_pixel.x, (uv_pixel.y))).rgb;


    vec2 uv_temp = uv_pixel;
    uv_temp.y *= 0.2;
	uv_temp.y += sin(time);
    vec4 baseColour  = texture(uNoiseTexture, uv_temp + displace.xy);
    
    vec4 noise  = floor(baseColour * 10.0) / 5.0;
    vec4 bright = mix(colour1, colour2, uvs.y);
    vec4 dark   = mix(colour3, colour4, uvs.y);
    vec4 colour = mix(dark, bright, noise);

    // Gradient 
    colour -= 0.45 * pow(uv_pixel.y, 8.0);
    colour += 0.5 * pow(1.0 - uv_pixel.y, 8.0);

    // Add sdf
    vec4 sdf = texture(uSDFTexture, uvs).rgba;
    colour.rgb += sdf.rgb;


    fColour = vec4(colour.rgb, 1.0);
}
"""

    sdf_frag: str = """
# version 460 core

uniform vec2 uResolution;
uniform vec2 uMousePos;
uniform float uTime;

in vec2 uvs;
out vec4 fColour;

float sdfCircle(vec2 pos, float radius, float sharpness){
    return clamp((length(pos) - radius) * sharpness, 0.0, 1.0);
}

void main(){

    vec2 mousePos = uMousePos/uResolution;
    float time = uTime * 0.04;

    float speed = 2.0;
    float freq  = 10.0;

    float distance = sdfCircle(uvs - mousePos, 0.001, 5.0);
    float shimmer  = sin(time * speed + distance * freq) * 0.1;

    fColour = vec4(vec3(shimmer), 1.0 - distance).rgba;
}

"""

    def __init__(self, caption:str, swizzle:str, scale:int, flip:bool=True, components:int=3, method:str="nearest", path:str="None", url:str="None", headless:bool=False):
        super().__init__(path=path, url=url, scale=scale, caption=caption, flip=flip, swizzle=swizzle, components=components, method=method, headless=headless)

        self.load_program()
        
        
        # Load Rain Textures
        self.rain_texture:     mgl.Texture     = self.ctx.texture(size=self.my_texture.size, components=4)
        self.rain_framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.rain_texture])

        # Load SDF Textures
        self.sdf_texture:     mgl.Texture     = self.ctx.texture(size=self.my_texture.size, components=4)
        self.sdf_texture.filter: tuple = (mgl.NEAREST, mgl.NEAREST)
        self.sdf_framebuffer: mgl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.sdf_texture])

        # Load Rain shaders
        self.rain_program: mgl.Program     = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.rain_frag)
        self.rain_vao:     mgl.VertexArray = self.ctx.vertex_array(self.rain_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])
        
        # Load SDF shaders
        self.sdf_program: mgl.Program = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=ShaderProgram.sdf_frag)
        self.sdf_vao: mgl.VertexArray = self.ctx.vertex_array(self.sdf_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])

        
    def garbage_cleanup(self):
        super().garbage_cleanup() # A better way then using decorators in this context
        self.rain_program.release()
        self.rain_vao.release()
        self.rain_texture.release()
        self.rain_framebuffer.release()
        self.sdf_program.release()
        self.sdf_vao.release()
        self.sdf_texture.release()
        self.sdf_framebuffer.release()

    @Main.d_update
    def update(self):
        self.sdf_program["uResolution"] = self.screen.get_size()
        self.sdf_program["uMousePos"]   = pygame.mouse.get_pos()
        self.sdf_program["uTime"]       = self.time
 
        self.rain_program["utime"] = self.time
        self.rain_program["uResolution"] = self.screen.get_size()

    @Main.d_draw
    def draw(self):

        # Render sdf shader
        self.sdf_framebuffer.clear()
        self.sdf_framebuffer.use()
        self.sdf_vao.render(mode=mgl.TRIANGLE_STRIP)

        # Render rain shader
        self.rain_framebuffer.use()
        self.my_texture.use(location=0)
        self.sdf_framebuffer.color_attachments[0].use(location=1)
        self.rain_program["uNoiseTexture"] = 0
        self.rain_program["uSDFTexture"]   = 1
        self.rain_vao.render(mode=mgl.TRIANGLE_STRIP)


        # Render main shader
        self.ctx.screen.clear()
        self.ctx.screen.use()

        self.rain_framebuffer.color_attachments[0].use(location=0)
        # self.sdf_framebuffer.color_attachments[0].use(location=0)
        self.main_program["myTexture"] = 0


if __name__ == "__main__":    
    shader_program: ShaderProgram = ShaderProgram(
        caption="Rain Effect",
        swizzle="RGBA",
        scale=0.5,
        flip=True,
        components=4,
        method="linear",
        path=r"images\noise.png",
    ).run()



