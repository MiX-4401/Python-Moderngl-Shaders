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

    vec4 colour = texture(uTexture, uvs).rgba;

    // Get gradient intensity on the x-axis
    float gX = 0.0;
    float gY = 0.0;

    for (int i = -1; i <= 1; i++){
        for (int j = -1; j <= 1; j++){

            float x = (gl_FragCoord.x / uResolution.x) + float(i) / uResolution.x;
            float y = (gl_FragCoord.y / uResolution.y) + float(j) / uResolution.y;
            
            gX += texture(uTexture, vec2(x,y)).r * float(kernalX[i+1][j+1]);
            gY += texture(uTexture, vec2(x,y)).r * float(kernalY[i+1][j+1]);

        }
    }

    float g = sqrt(pow(gX, 2) + pow(gY, 2));

    if (g > uThreshold){
        fColour = vec4(1.0, 1.0, 1.0, 1.0);
    } else {
        fColour = vec4(0.0, 0.0, 0.0, 1.0);
    }
    
}