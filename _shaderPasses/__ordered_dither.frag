# version 460 core

uniform sampler2D uOriginal;

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
    0,  32, 8,  40, 2,  34, 10, 42,
    48, 16, 56, 24, 50, 18, 58, 26,
    12, 44, 4,  36, 14, 46, 6,  38,
    60, 28, 52, 20, 62, 30, 54, 22,
    3,  35, 11, 43, 1,  33, 9,  41,
    51, 19, 59, 27, 49, 17, 57, 25,
    15, 47, 7,  39, 13, 45, 5,  37,
    63, 31, 55, 23, 61, 29, 53, 21
};

float getBayer2(){
    int x = int(mod(gl_FragCoord.x, 2));
    int y = int(mod(gl_FragCoord.y, 2));
    return float(bayer2[(x + y) * 2]) / 4.0;
};
float getBayer4(){
    int x = int(mod(gl_FragCoord.x, 4));
    int y = int(mod(gl_FragCoord.y, 4));
    return float(bayer4[(x + y) * 4]) / 16.0;
};
float getBayer8(){
    int x = int(mod(gl_FragCoord.x, 8));
    int y = int(mod(gl_FragCoord.y, 8));
    return float(bayer8[(x + y) * 8]) / 64.0;
};

void main(){

    // Sample textures
    vec4 original = texture(uOriginal, uvs).rgba;
    
    float colours[2];
    colours[0] = (original.r < 0.5) ? 0.0 : 1.0;
    colours[1] = 1.0 - colours[0];
    float value = getBayer4();
    float dist  = abs(colours[0] - original.r);
    
    if (dist < value){
        fColour = vec4(vec3(0.0, 0.0, 0.0), original.a);
        
    } else {
        fColour = vec4(vec3(1.0, 1.0, 1.0), original.a);
    }
}