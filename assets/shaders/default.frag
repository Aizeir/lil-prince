#version 330 core

in vec2 uvs;
out vec4 FragColor;
uniform sampler2D surface;
uniform vec2 resolution;
uniform float time;

uniform vec2 offset;

uniform vec4 planets[16];
uniform int planet_num;

// IL FAUT UTILISER TOUTES LES VARIABLES > sinon elles sont discard par le compilatur et c'est comme si elles existent pas > keyerror
// LES LISTES DOIVENT TJRS AVOIR LE BON NM D'ELEMENTS > invalid uniform size
// Les tableax ne peuvent pas etre initalisée directement (dabord etre declarés -_-) > OpenGL does not allow C style initializers
// Division par flottant pas entier (a verif)

vec4 star(vec2 uv) {
    uv = (uv * 2.0 - 1.0) * vec2(resolution.x / resolution.y, 1.0);
    float d = length(uv);
    float glow = exp(-d * 2) * .5;
    return vec4(vec3(1.0, 0.9, 0.8) * glow, 1);
}

const vec4 colors[8] = vec4[](
    vec4(0.165, 0.141, 0.169, 1.0),
    vec4(0.275, 0.251, 0.251, 1.0),
    vec4(0.467, 0.357, 0.357, 1.0),
    vec4(0.800, 0.439, 0.282, 1.0),
    vec4(0.843, 0.710, 0.314, 1.0),
    vec4(0.408, 0.659, 0.671, 1.0),
    vec4(0.565, 0.835, 0.612, 1.0),
    vec4(1.000, 1.000, 0.698, 1.0)
);

vec3 randomGradient(vec3 p) {
    float a = fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453123) * 6.2831853;
    float b = fract(sin(dot(p, vec3(269.5, 183.3, 246.1))) * 43758.5453123) * 6.2831853;
    return vec3(cos(a), sin(a) * cos(b), sin(b));
}

float perlinNoise(vec3 uvs) {
    vec3 p = floor(uvs), f = fract(uvs);
    vec3 g000 = randomGradient(p), g100 = randomGradient(p + vec3(1, 0, 0));
    vec3 g010 = randomGradient(p + vec3(0, 1, 0)), g110 = randomGradient(p + vec3(1, 1, 0));
    vec3 g001 = randomGradient(p + vec3(0, 0, 1)), g101 = randomGradient(p + vec3(1, 0, 1));
    vec3 g011 = randomGradient(p + vec3(0, 1, 1)), g111 = randomGradient(p + vec3(1, 1, 1));
    
    float d000 = dot(g000, f), d100 = dot(g100, f - vec3(1, 0, 0));
    float d010 = dot(g010, f - vec3(0, 1, 0)), d110 = dot(g110, f - vec3(1, 1, 0));
    float d001 = dot(g001, f - vec3(0, 0, 1)), d101 = dot(g101, f - vec3(1, 0, 1));
    float d011 = dot(g011, f - vec3(0, 1, 1)), d111 = dot(g111, f - vec3(1, 1, 1));
    
    vec3 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(d000, d100, u.x), mix(d010, d110, u.x), u.y),
               mix(mix(d001, d101, u.x), mix(d011, d111, u.x), u.y), u.z);
}

float noise(vec3 uvs) {
	float sum = 0, amp = .5;

    for (int i = 0; i < 4; i++) {
        sum += perlinNoise(uvs) * amp;
        uvs *= 2.0; amp *= 0.5;
    }
    return sum;
}
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float starfield(vec2 uv) {
    vec3 stars_direction = normalize(vec3(uv * 2. - 1., 1.)); // could be view vector for example
	float stars_threshold = 8.; // modifies the number of stars that are visible
	float stars_exposure = 200.; // modifies the overall strength of the stars
	float stars = pow(clamp(perlinNoise(stars_direction * 200.), 0., 1.), stars_threshold) * stars_exposure;
	return stars * mix(0.4, 1.4, noise(stars_direction * 100. + vec3(time))); // time based flickering
}




void main() {
	// Texture
	vec4 tex = texture2D(surface, uvs);
	if (tex.rgb != vec3(0,0,0)) FragColor = tex;
	else {
		FragColor = vec4(vec3(starfield(uvs)),1) + star(uvs);
		vec2 pos = (vec2(uvs.x * resolution.x, uvs.y * resolution.y) + offset);

		for (int i=0; i<planet_num; i++) {
			vec4 p = planets[i]; float rad = p.z;

			if (distance(pos, p.xy) <= rad) {
				float z = pow(1 - pow((p.x-pos.x)/rad, 2) - pow((p.y-pos.y)/rad, 2), .2) * rad;
				float val = (noise(vec3(pos.x,pos.y,z+time/100) / 100)); // entre -1 et 1
				val = (val+1) / 2.;

				if (p[3] == 0) {
					if (val < .4) FragColor = colors[4];
					else if (val < .5) FragColor = colors[3];
					else FragColor = colors[2];
				}
				else if (p[3] == 1) {
					if (val < .2) FragColor = colors[1];
					else if (val < .45) FragColor = colors[5];
					else if (val < .5) FragColor = colors[6];
					else FragColor = colors[1];
				}
				else if (p[3] == 2) {
					if (val < .2) FragColor = colors[0];
					else if (val < .5) FragColor = colors[1];
					else FragColor = colors[2];
				}
				

				break;
			}
		}
	}
}