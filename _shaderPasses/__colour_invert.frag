# version 460 core

uniform sampler2D uTexture;

in vec2 uvs;
out vec4 fColour;

void main(){
    vec4 colour = texture(uTexture, uvs);
    fColour = vec4(1.0 - colour.rgb, colour.a);
}