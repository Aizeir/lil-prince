#version 330 core

in vec2 uvs;
out vec4 FragColor;
uniform sampler2D surface;
uniform vec2 resolution;
uniform float time;

vec3 star(vec2 uv) {
    uv = (uv * 2.0 - 1.0) * vec2(resolution.x / resolution.y, 1.0);
    float d = length(uv);
    float glow = exp(-d * 2) * .5;
    return vec3(1.0, 0.9, 0.8) * glow;
}

void main() {
	// Texture
	vec4 tex = texture2D(surface, uvs);
	if (tex.rgb != vec3(0,0,0)) FragColor = tex;
	else FragColor = vec4(star(uvs),1);
}