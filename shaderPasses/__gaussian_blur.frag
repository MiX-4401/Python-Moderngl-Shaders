# version 460 core

uniform sampler2D uTexture;
uniform bool horizontal;
uniform float weights[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

in vec2 uvs;
out vec4 fColour;

void main(){

    vec2 offset = 1.0 / textureSize(uTexture, 0);
    vec3 colour = texture(uTexture, uvs).rgb * weights[0];

    if (horizontal){
        for (int i=1; i<5; i++){
            colour += texture(uTexture, uvs + vec2(offset.x * i, 0.0)).rgb * weights[i];
            colour += texture(uTexture, uvs - vec2(offset.x * i, 0.0)).rgb * weights[i];
        }
    } else {
        for (int i=1; i<5; i++){
            colour += texture(uTexture, uvs + vec2(0.0, offest.y * i)).rgb * weights[i];
            colour += texture(uTexture, uvs - vec2(0.0, offest.y * i)).rgb * weights[i];
        }
    }

    fColour = vec4(colour.rgb, colour.a)

}