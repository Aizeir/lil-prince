#version 330 core

layout (location = 0) in vec2 vert;
layout (location = 1) in vec2 texcoord;
out vec2 uvs;

void main() {
	gl_Position = vec4(vert, 0.0, 1.0);
	uvs = texcoord;
}