# version 460 core

uniform sampler2D uOriginal;
uniform sampler2D uQuantise1;
uniform sampler2D uQuantise2;
uniform int uBayerLevel;
int a = uBayerLevel;
uniform vec2 uSize;

in vec2 uvs;
out vec4 fColour;

const int bayer2[2 * 2] = {
    0, 2,
    3, 1
};

const int bayer4[4 * 4] = {
    0,  8,  2,  10,
    12, 4,  14, 6,
    3,  11, 1,  9,
    15, 7,  13, 5
};

const int bayer8[8 * 8] = {
    0,  32, 8,  4,  2,  34, 10, 42,
    18, 16, 56, 24, 50, 18, 58, 25,
    12, 44, 4,  36, 14, 46, 6,  38,
    60, 28, 52, 20, 62, 30, 54, 22,
    3,  35, 11, 43, 1,  33, 9,  41,
    51, 19, 59, 27, 49, 17, 57, 25,
    15, 47, 7,  39, 13, 45, 5,  37,
    63, 31, 55, 23, 61, 29, 53, 21
};

float getBayer2(int x, int y){
    return float(bayer2[(x % 2) * 2 + (y % 2)]) * (1.0 / 4.0);
};
float getBayer4(int x, int y){
    return float(bayer4[(x % 4) * 4 + (y % 4)]) * (1.0 / 16.0);
};
float getBayer8(int x, int y){
    return float(bayer8[(x % 8) * 8 + (y % 8)]) * (1.0 / 64.0);
};

void main(){

    // Sample textures
    vec4 original = texture(uOriginal, uvs).rgba;
    vec3 quantise1 = texture(uQuantise1, uvs).rgb;
    vec3 quantise2 = texture(uQuantise2, uvs).rgb;
    
    // Extract colours
    float r1 = original.r;
    float g1 = original.g;
    float b1 = original.b;

    float r2 = quantise1.r;
    float g2 = quantise1.g;
    float b2 = quantise1.b;

    float r3 = quantise2.r;
    float g3 = quantise2.g;
    float b3 = quantise2.b;

    // Get texture coordinates
    int x = int(round(uvs.x * uSize.x));
    int y = int(round(uvs.y * uSize.y));

    // Get bayer matrix value
    float bayerValues[3] = {0.0, 0.0, 0.0};
    bayerValues[0] = getBayer2(x, y);
    bayerValues[1] = getBayer4(x, y);
    bayerValues[2] = getBayer8(x, y);

    // Find ecualidian distance between two colours
    float dist1 = sqrt(pow(r1-r2, 2) + pow(g1-g2, 2) + pow(b1-b2, 2));
    float dist2 = sqrt(pow(r2-r3, 2) + pow(g2-g3, 2) + pow(b2-b3, 2));

    // Normalise original dist to closest by the distance between both quantised colours
    float normalised = dist1 / dist2;

    // Choose either first quantised or second quantised colour
    if (normalised < bayerValues[0]){
        fColour = vec4(quantise1.rgb, original.a);
    } else {
        fColour = vec4(quantise2.rgb, original.a);
    }
}