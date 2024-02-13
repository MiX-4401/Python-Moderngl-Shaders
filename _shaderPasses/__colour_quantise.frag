# version 460 core

uniform sampler2D uTexture;
uniform int  uPalletSize = 10;
uniform vec3 uPallet[10];

in vec2 uvs;
out vec4 fColour;

float getDistance(vec3 c1, vec3 c2){
    return sqrt(pow(c1.r-c2.r, 2) + pow(c1.g-c2.g, 2) + pow(c1.b-c2.b, 2));
}

void main(){

    vec4 colour = texture(uTexture, uvs).rgba;

    // Get distances
    float distances[int(uPalletSize)];
    for (int i=0; i<uPalletSize; i++){
        distances[i] = getDistance(colour.rgb, uPallet[i]);
    }

    // Sorting Algorithm
    float distColours[2]    = {1000.0, 1000.0};
    vec3  closestColours[2] = {vec3(0.0), vec3(0.0)};
    
    for (int i=0; i<uPalletSize; i++){
        if (distances[i] < distColours[0]){
            distColours[1]    = distColours[0];
            closestColours[1] = closestColours[0];
            distColours[0]    = distances[i];
            closestColours[0] = uPallet[i];
        } else if (distances[i] < distColours[1]){
            distColours[1]    = distances[i];
            closestColours[1] = uPallet[i];
        }
    }

    fColour = vec4(closestColours[1], colour.a);

}