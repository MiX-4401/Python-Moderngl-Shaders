# version 460

uniform sampler2D uTexture;
uniform float uThreshold = 1.0;
uniform float uStrength  = 1.0;

in vec2 uvs;
out vec4 fColour;

void main(){
    vec4 contrast = texture(uTexture, uvs).rgba;

    float brightness = dot(contrast.rgb, vec3(0.2126, 0.7152, 0.0722));
    if (brightness > uThreshold){
        fColour = vec4(contrast.rgb * uStrength, contrast.a);
    } else {
        fColour = vec4(0.0, 0.0, 0.0, 1.0);
    }
}