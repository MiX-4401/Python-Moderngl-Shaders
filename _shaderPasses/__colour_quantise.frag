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


    vec3  closestColours[2];
    float closestDistances[2];
    closestColours[0]   = uPallet[0];
    closestDistances[0] = distances[0];
    closestColours[1]   = uPallet[1];
    closestDistances[1] = distances[1];

    if (closestDistances[0] < disgtanc)

    for (int i=0; i<4; i++){
        if (distances[i] < closestDistances[0]){
            closestColours[1]   = closestColours[0];
            closestDistances[1] = closestDistances[0];
            closestColours[0]   = uPallet[i];
            closestDistances[0] = distances[i];
        } else if (distances[i] < closestDistances[1]){
            closestDistances[1] = distances[i];
            closestColours[1]   = uPallet[i];
        }
    }

    

    if (uCloseness == 0){
        colour.rgb = closestColours[0];
    } else {
        colour.rgb = closestColours[1];
    }

    fColour = vec4(colour.rgb, colour.a);

}