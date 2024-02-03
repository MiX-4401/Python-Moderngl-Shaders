# version 460 core

uniform sampler2D uTexture;
uniform bool  uHorizontal;
uniform int   uXStrength = 5;
uniform int   uYStrength = 5;
uniform float uWeights[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

in vec2 uvs;
out vec4 fColour;

void main(){

    vec2 offset = 1.0 / textureSize(uTexture, 0);
    vec4 colour = texture(uTexture, uvs).rgba;
    colour.rgb *= uWeights[0];

    if (uHorizontal){
        for (int i=1; i<uXStrength; i++){
            colour.rgb += texture(uTexture, uvs + vec2(offset.x * i, 0.0)).rgb * uWeights[i];
            colour.rgb += texture(uTexture, uvs - vec2(offset.x * i, 0.0)).rgb * uWeights[i];
        }
    } else {
        for (int i=1; i<uYStrength; i++){
            colour.rgb += texture(uTexture, uvs + vec2(0.0, offset.y * i)).rgb * uWeights[i];
            colour.rgb += texture(uTexture, uvs - vec2(0.0, offset.y * i)).rgb * uWeights[i];
        }
    }

    fColour = vec4(colour.rgb, colour.a);

}