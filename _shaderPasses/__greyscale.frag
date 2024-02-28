# version 460 core

uniform sampler2D uTexture;

in vec2 uvs;
out vec4 fColour;


void main(){

    vec4 colour = texture(uTexture, uvs).rgba;

    // Convert to greyScale
    float luminence = dot(colour.rgb, vec3(0.2126, 0.7152, 0.0722));

    fColour = vec4(vec3(luminence), 1.0);
}