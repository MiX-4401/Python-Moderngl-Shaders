# version 460 core

in vec2 bPos;
in vec2 bTexCoord;
out vec2 uvs;

void main(){
    uvs = bTexCoord;
    gl_Position = vec4(bPos, 0.0, 1.0);
}