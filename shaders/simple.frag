#version 330 core

in vec2 fragmentTexure;

out vec4 outColor;

uniform sampler2D imageTexture;

void main()
{
    outColor = texture(imageTexture, fragmentTexure);
}
