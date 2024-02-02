# version 460 core

uniform sampler2D uTexture;


in vec2 uvs;
out vec4 fragColour;

void main(){
    vec4 colour = texture(uTexture, uvs).rgba;
    vec4 fragColour = vec4(colour.rgb, colour.a);
}