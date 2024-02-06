# version 460 core

uniform sampler2D uTexture;
uniform int uCloseness;
uniform int uPalletSize = 2;
uniform vec3 uPallet[2] = vec3[] (vec3(0.0, 0.0, 0.0), vec3(1.0, 1.0, 1.0));

in vec2 uvs;
out vec4 fColour;

void main(){

    vec4 colour = texture(uTexture, uvs).rgba;

    float r1 = colour.r;
    float g1 = colour.g;
    float b1 = colour.b;

    // FOR each colour pallet
    float lowest = 1000.0; 
    float index  = 0.0;
    int distances[uCloseness];
    for (int i=0; i<uPalletSize; i++){
        float r2 = uPallet[i].r;
        float g2 = uPallet[i].g;
        float b2 = uPallet[i].b;

        // Get Euclidean Distance between sample colour and pallets
        float dist = sqrt(pow(r1-r2, 2) + pow(g1-g2, 2) + pow(b1-b2, 2));
        
        // Set the lowest 
        if (dist < lowest){
            lowest = dist;
            index  = i;
        }
    }

    // Set the colour to nearest to the colour pallet
    colour.rgb = uPallet[int(index)];

    // Release the finalColour
    fColour = vec4(colour.rgb, colour.a); 

}