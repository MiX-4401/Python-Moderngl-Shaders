# version 460 core

uniform sampler2D uTexture;
uniform int  uCloseness;
uniform int  uPalletSize;
uniform vec3 uPallet[10];

in vec2 uvs;
out vec4 fColour;


float getDistance(vec3 c1, vec3 c2){
    // Return Euclidean Distance
    return sqrt(pow(c1.r-c2.r, 2) + pow(c1.g-c2.g, 2) + pow(c1.b-c2.b, 2));
}

void main(){

    vec4 colour = texture(uTexture, uvs).rgba;

    // --------------------
    //  Sorting Algorithm
    // --------------------
    float distColours[2]    = {1000.0, 1000.0};
    vec3  closestColours[2] = {vec3(0.0), vec3(1.0)};
    
    for (int i=0; i<uPalletSize; i++){

        // Get colour /- pallet distance
        float dist = getDistance(colour.rgb, uPallet[i]);

        // SelectionSort
        if (dist < distColours[0]){
            distColours[1]    = distColours[0];
            closestColours[1] = closestColours[0];
            distColours[0]    = dist;
            closestColours[0] = uPallet[i];
        } 
        else if (dist < distColours[1]){
            distColours[1]    = dist;
            closestColours[1] = uPallet[i];
        }
    }

    // Pick colour at closeness (0 or 1)
    if (uCloseness == 0){
        fColour = vec4(closestColours[0], colour.a);
    } else {
        fColour = vec4(closestColours[1], colour.a);
    }

}



