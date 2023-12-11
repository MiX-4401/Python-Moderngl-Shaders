import pygame, moderngl, numpy
from sys import exit


class Main():
    main_vertex: str = """
# version 460 core

in vec2 aPosition;
in vec2 aTexCoord;
out vec2 uvs;

void main(){

    uvs = vec2(aTexCoord.x, 1.0 - aTexCoord.y);
    //uvs = aTexCoord;
    gl_Position = vec4(aPosition, 0.0, 1.0);
}

"""
    main_frag: str = """
# version 460 core

uniform sampler2D myTexture;
in vec2 uvs;
out vec4 fColour;

void main(){

    vec3 colour = vec3(texture(myTexture, uvs).rgb); 
    fColour = vec4(colour.rgb, 1.0);
}
"""

    bloom_seperate_frag: str = """
# version 460 core

layout (location = 0) out vec4 fColour;
layout (location = 1) out vec4 bColour;

uniform sampler2D myTexture;
in vec2 uvs;

void main(){

    // Get frag colour of myTexture
    vec3 colour = texture(myTexture, uvs).rgb; 
    
    // Calculate brightness of frag
    float brightness = dot(colour, vec3(0.2126, 0.7152, 0.0722));
    
    // Set bColour depending on brightness
    if (brightness > 0.9){ // Change this value for contrast
        bColour = vec4(colour, 1.0);
    } else {
        bColour = vec4(0.0, 0.0, 0.0, 1.0);
    }

    fColour = vec4(colour, 1.0);
}
"""

    gausssian_blur_frag: str = """
# version 460 core

uniform sampler2D myTexture;
uniform bool horizontal;
uniform float weight[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

in vec2 uvs;
out vec4 fColour;

void main(){

    vec2 tOffset = 1.0 / textureSize(myTexture, 0);
    vec3 colour  = texture(myTexture, uvs).rgb * weight[0];

    if (horizontal){
        for (int i = 1; i < 5; i++){
            colour += texture(myTexture, uvs + vec2(tOffset.x * i, 0.0)).rgb * weight[i];
            colour += texture(myTexture, uvs - vec2(tOffset.x * i, 0.0)).rgb * weight[i];
        }
    } 
    else {
        for (int i = 1; i < 5; i++){
            colour += texture(myTexture, uvs + vec2(0.0, tOffset.x * i)).rgb * weight[i];
            colour += texture(myTexture, uvs - vec2(0.0, tOffset.x * i)).rgb * weight[i];
        }
    }

    fColour = vec4(colour.rgb, 1.0);
}
"""

    blend_frag: str = """
# version 460 core

uniform sampler2D sceneImage;
uniform sampler2D bloomImage;
uniform float exposure;

in  vec2 uvs;
out vec4 fColour;

void main(){

    float a = exposure;
    vec3 sceneTexture = texture(sceneImage, uvs).rgb;
    vec3 bloomTexure  = texture(bloomImage, uvs).rgb;
    sceneTexture += bloomTexure; // Additive blending

    //vec3 colour = vec3(1.0) - exp(-sceneTexture * exposure);
    //colour = pow(colour, vec3(1.0 / 2.2));
    vec3 colour = sceneTexture;
    fColour = vec4(colour, 1.0);
}

"""

    def __init__(self):

        # Pygame boilerplate
        self.clock:  pygame.time.Clock = pygame.time.Clock()
        self.screen: pygame.Surface    = pygame.display.set_mode((800, 500), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("Bloom Shader")
        self.fps: int = 60
        
        # Moderngl boilerplate
        self.ctx: moderngl.Context = moderngl.create_context()
        self.main_program: moderngl.Program = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=Main.main_frag)
        self.quad_buffer:  moderngl.Buffer  = self.ctx.buffer(data=numpy.array([-1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, 0.0, 1.0, 1.0, -1.0, 1.0, 1.0], dtype="f4"))
        self.main_vao: moderngl.VertexArray = self.ctx.vertex_array(self.main_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])

        # Create texture
        self.my_texture: Texture = Texture(ctx=self.ctx, filepath=r"04Projects\ShaderBloom\image_5.jpg")
        self.my_texture.load_texture()

        # Create screen texture
        self.screen_texture:    moderngl.Texture     = self.ctx.texture(size=self.my_texture.size, components=4)
        self.blend_framebuffer: moderngl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.screen_texture])

        # Create seperation buffers
        self.colour_renderbuffer:   moderngl.Renderbuffer = self.ctx.renderbuffer(size=self.my_texture.size, components=4)
        self.contrast_renderbuffer: moderngl.Renderbuffer = self.ctx.renderbuffer(size=self.my_texture.size, components=4)
        self.seperate_framebuffer:  moderngl.Framebuffer  = self.ctx.framebuffer(color_attachments=[self.colour_renderbuffer, self.contrast_renderbuffer])
        
        # Create blur buffers
        self.blur_framebuffer_1: moderngl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.ctx.texture(size=self.my_texture.size, components=4)])
        self.blur_framebuffer_2: moderngl.Framebuffer = self.ctx.framebuffer(color_attachments=[self.ctx.texture(size=self.my_texture.size, components=4)])

        # Create bloom seperate shader programs
        self.bloom_seperate_program: moderngl.Program   = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=Main.bloom_seperate_frag)
        self.bloom_seperate_vao:   moderngl.VertexArray = self.ctx.vertex_array(self.bloom_seperate_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])

        # Create bloom blue shader programs
        self.bloom_gaussian_blur_program: moderngl.Program = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=Main.gausssian_blur_frag)
        self.bloom_gaussian_blur_vao: moderngl.VertexArray = self.ctx.vertex_array(self.bloom_gaussian_blur_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])

        # Create bloom blend shader programs
        self.bloom_blend_program: moderngl.Program = self.ctx.program(vertex_shader=Main.main_vertex, fragment_shader=Main.blend_frag)
        self.bloom_blend_program_vao: moderngl.VertexArray = self.ctx.vertex_array(self.bloom_blend_program, [(self.quad_buffer, "2f 2f", "aPosition", "aTexCoord")])

        # Render framebuffer for seperation (colour/contrast renderbuffers)
        self.seperate_framebuffer.use()
        self.my_texture.surface.use(location=0)
        self.bloom_seperate_program["myTexture"] = 0
        self.bloom_seperate_vao.render(mode=moderngl.TRIANGLE_STRIP)

        # Render framebuffer for gaussian blue
        first_iteration: bool = True; horizontal: bool = True
        render_targets:  list = [self.blur_framebuffer_1, self.blur_framebuffer_2]
        for i in range(10):

            # Bind framebuffer
            render_targets[horizontal].use()

            # Bind texture
            if first_iteration: 
                texture: moderngl.Texture = self.ctx.texture(size=self.my_texture.size, components=4, data=self.seperate_framebuffer.read(attachment=1, components=4))
                texture.use(location=0)
            else:
                texture: moderngl.Texture = render_targets[False if horizontal else True].color_attachments[0]
                texture.use(location=0)

            # Set uniforms
            self.bloom_gaussian_blur_program["horizontal"] = horizontal
            self.bloom_gaussian_blur_program["myTexture"]  = 0

            # Render program
            self.bloom_gaussian_blur_vao.render(mode=moderngl.TRIANGLE_STRIP)

            # Swap horizontal and first_iteration values
            horizontal      = True  if horizontal      == False else False
            first_iteration = False if first_iteration == True  else False
            
        texture.release()

        # Blend blured texture with colour texture
        self.blend_framebuffer.use()

        self.my_texture.surface.use(location=0)
        self.blur_framebuffer_1.color_attachments[0].use(location=1)

        self.bloom_blend_program["sceneImage"] = 0
        self.bloom_blend_program["bloomImage"] = 1
        self.bloom_blend_program["exposure"]   = 0.1

        self.bloom_blend_program_vao.render(mode=moderngl.TRIANGLE_STRIP)

        # Copy bloom renderbuffer to screen texture
        # self.screen_texture.write(data=self.blur_framebuffer_1.read(attachment=0, components=4))
        
        # Set location of screen_texture
        self.screen_texture.use(location=0)
        self.main_program["myTexture"] = 0

    def update_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.garbage_cleanup()
                pygame.quit()
                exit()

    def garbage_cleanup(self):
        self.ctx.release()
        self.main_program.release()
        self.quad_buffer.release()
        self.main_vao.release()

        self.my_texture.release()

        self.blend_framebuffer.release()
        self.screen_texture.release()

        self.colour_renderbuffer.release()
        self.contrast_renderbuffer.release()
        self.seperate_framebuffer.release()

        self.blur_framebuffer_1.release()
        self.blur_framebuffer_2.release()

        self.bloom_gaussian_blur_program.release()
        self.bloom_gaussian_blur_vao.release()

        self.bloom_seperate_program.release()
        self.bloom_seperate_vao.release()

        self.bloom_blend_program.release()
        self.bloom_blend_program_vao.release()

    def update(self):
        pass

    def draw(self):

        # Render Main Screen
        self.ctx.screen.use()
        self.ctx.clear(0.0, 0.0, 0.0)
        self.main_vao.render(mode=moderngl.TRIANGLE_STRIP)
        pygame.display.flip()

    def run(self):
        while True:
            self.update_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)


class Texture():
    def __init__(self, ctx:moderngl.Context, filepath:str):
        self.ctx:     moderngl.Context = ctx
        self.surface: moderngl.Texture = None 

        self.filepath: str = filepath

        self.size: tuple = None

    def load_texture(self):

        # Load surface
        pygame_surface: pygame.Surface   = pygame.transform.flip(surface=pygame.image.load(self.filepath).convert_alpha(), flip_x=False, flip_y=True)
        self.surface:   moderngl.Texture = self.ctx.texture(size=pygame_surface.get_size(), components=4, data=pygame_surface.get_view("1"))
        self.surface.swizzle = "BGRA" 

        # Add size to 
        self.size: tuple = self.surface.size
    
    def write(self, data:bytes):
        self.surface.write(data=data)

    def read(self):
        return self.surface.read()

    def release(self):
        self.surface.release()
        

if __name__ == "__main__":
    main: Main = Main()
    main.run()

