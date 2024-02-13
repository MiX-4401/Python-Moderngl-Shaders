# version 460 core

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