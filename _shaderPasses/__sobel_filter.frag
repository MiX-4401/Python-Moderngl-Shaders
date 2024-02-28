# version 460 core

uniform sampler2D uTexture;
uniform vec2 uResolution;
uniform float uThreshold;

in vec2 uvs;
out vec4 fColour;

mat3 kernalY = mat3(
    -1, 0, 1,
    -2, 0, 2,
    -1, 0, 1
); 
mat3 kernalX = mat3(
    -1, -2, -1,
    0, 0, 0,
    1, 2, 1
);

void main(){

    // Get gradient intensity on the x-axis
    float gX = 0.0;
    float gY = 0.0;

    // x & y axies kernal pass
    for (int i = -1; i <= 1; i++){
        for (int j = -1; j <= 1; j++){

            // Calculate the uvs coords of surrounding fragments
            float x = (gl_FragCoord.x / uResolution.x) + float(i) / uResolution.x;
            float y = (gl_FragCoord.y / uResolution.y) + float(j) / uResolution.y;
            
            // Add to the gradient intensites on the x & y axies
            gX += texture(uTexture, vec2(x,y)).r * float(kernalX[i+1][j+1]);
            gY += texture(uTexture, vec2(x,y)).r * float(kernalY[i+1][j+1]);

        }
    }

    // Calculate the magnitude of gradient intensity
    float g = sqrt(pow(gX, 2) + pow(gY, 2));

    // Thresholding for black and white outputs
    if (g > uThreshold){
        fColour = vec4(1.0, 1.0, 1.0, 1.0);
    } else {
        fColour = vec4(0.0, 0.0, 0.0, 1.0);
    }
}