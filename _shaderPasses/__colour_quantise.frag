# version 460 core

uniform sampler2D uTexture;
uniform int uCloseness = 1;
uniform vec3 uPallet[10] = vec3[] (vec3(0.0, 0.0, 0.0), vec3(1.0, 1.0, 1.0), vec3(1.0, 1.0, 1.0), vec3(1.0, 1.0, 1.0), vec3(1.0, 1.0, 1.0), vec3(1.0, 1.0, 1.0), vec3(1.0, 1.0, 1.0), vec3(1.0, 1.0, 1.0), vec3(1.0, 1.0, 1.0), vec3(1.0, 1.0, 1.0));

in vec2 uvs;
out vec4 fColour;

void main(){

    // Sample texture
    vec4 colour = texture(uTexture, uvs).rgba;

    // ==========================================
    //             Find distances
    // ==========================================
    float distances[4];
    for (int i=0; i<4; i++){
        // Get euclidean distance between Colour and Pallet
        //distances[i] = length(colour.rgb, uPallet[i].rgb); 
        distances[i] = sqrt(
            pow(colour.r - uPallet[i].r, 2) +
            pow(colour.g - uPallet[i].g, 2) +
            pow(colour.b - uPallet[i].b, 2)
        ); 
    }

    // ==========================================
    // Sorting algorithm for two clostest colours
    // ==========================================
    float lowest  = distances[0];
    float highest = distances[1];
    int indexes[2] = {0, 1};

    // CHECK: Swap initial values
    if (highest < lowest){
        float temp = lowest;
        lowest  = highest;
        highest = temp;
        indexes[0] = 1;
        indexes[1] = 0;
    }

    // Sort for two closest
    for (int i=0; i<4; i++){
        if (distances[i] < lowest){
            highest = lowest;
            lowest  = distances[i];
            indexes[1] = indexes[0];
            indexes[0] = i;
        }
        else if (distances[i] < highest){
            highest = distances[i];
            indexes[1] = i;
        }
    }

    if (uCloseness == 0){
        colour.rgb = uPallet[indexes[0]];
    } else {
        colour.rgb = uPallet[indexes[1]];
    }

    fColour = vec4(colour.rgb, colour.a);

}