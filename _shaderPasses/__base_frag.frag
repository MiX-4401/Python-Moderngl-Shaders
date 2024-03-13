# version 460 core

uniform sampler2D uTexture;


in vec2 uvs;
out vec4 fColour;

void main(){
    vec4 colour = texture(uTexture, uvs).rgba;
    fColour = vec4(colour.rgb, colour.a);
}