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

            fColour = vec4(colour.rgb, 1.0);
        }
    """

    def __init__(self, media:str, scale:int=1, caption:str="NA", swizzle:str="RGBA", flip:bool=False, components:int=4, method:str="nearest", fps:int=60):
        super().__init__(media=media, scale=scale, caption=caption, swizzle=swizzle, flip=flip, components=components, method=method, fps=fps)

        self.load_program()
        
        # Load Rain shaders
        self.create_program(title="new", vert=Main.vert, frag=ShaderProgram.rain_frag)
        self.create_vao(title="new", program="new", buffer="main", args=["2f 2f", "iPosition", "iTexCoord"])
        self.create_texture(title="new", size=self.textures["main"].size, components=4)
        self.create_framebuffer(title="new", attachments=[self.textures["new"]])

    def update(self):
        self.programs["new"]["utime"] = self.time
        self.programs["new"]["uResolution"] = self.screen.get_size()
        super().update()

    def draw(self):

        # Render rain shader
        self.framebuffers["new"].use()
        self.textures["main"].use(location=0)
        self.programs["new"]["uNoiseTexture"] = 0
        self.vaos["new"].render(mode=mgl.TRIANGLE_STRIP)

        self.textures["new"].use(location=0)
        self.programs["main"]["uTexture"] = 0
        super().draw()


if __name__ == "__main__":    
    shader_program: ShaderProgram = ShaderProgram(
        caption="Rain Effect",
        swizzle="RGBA",
        scale=0.74,
        flip=True,
        components=4,
        method="linear",
        media=r"_images\noise.png",
    ).run()



