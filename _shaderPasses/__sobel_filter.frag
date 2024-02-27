# version 460 core

uniform sampler2D uTexture;

in vec2 uvs;
out vec4 fColour;

// int GradientX[9] = {
//     -1, 0, 1,
//     -2, 0, 2,
//     -1, 0, 1
// };

// int GradientY[9] = {
//     -1, -2, -1,
//     0, 0, 0,
//     1, 2, 1
// };

void main(){
    vec4 colour = texture(uTexture, uvs).rgba;

    // Convert texture to greyscale
    // float greyScale = dot(colour.rgb, vec3(0.2126, 0.7152, 0.0722));

    vec4 fColour = vec4(colour);
}