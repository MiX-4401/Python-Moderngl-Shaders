# version 460

uniform sampler2D uTexture;
uniform sampler2D uBlur;

in vec2 uvs;
out vec4 fColour;

void main(){
    vec4 colour     = texture(uTexture, uvs).rgba;
    vec4 bloomBlur  = texture(uBlur, uvs).rgba;

    colour += bloomBlur;

    fColour = vec4(colour.rgb, colour.a);
}