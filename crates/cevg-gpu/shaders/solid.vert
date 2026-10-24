#version 450
// One shader for everything in a viewport. `light.w` 0: positions are in
// scene space and get the view-projection and Lambert shading. 1: positions
// are already in clip space (lines, arrowheads, discs expanded on the CPU)
// and pass straight through, unlit.
//
// 128 bytes of push constants, the minimum every Vulkan device offers.

layout(push_constant) uniform Push {
    mat4 view_proj;  // scene to clip
    vec4 light;      // xyz: light direction in eye space; w: mode
    vec4 view0;      // the three columns of the scene-to-eye rotation
    vec4 view1;
    vec4 view2;
} push;

layout(location = 0) in vec3 in_pos;
layout(location = 1) in vec3 in_normal;
layout(location = 2) in vec4 in_color;

layout(location = 0) out vec4 v_color;

void main() {
    if (push.light.w < 0.5) {
        gl_Position = push.view_proj * vec4(in_pos, 1.0);
        mat3 view = mat3(push.view0.xyz, push.view1.xyz, push.view2.xyz);
        vec3 n = normalize(view * in_normal);
        float tone = 0.34 + 0.66 * abs(dot(n, normalize(push.light.xyz)));
        v_color = vec4(in_color.rgb * tone, in_color.a);
    } else {
        gl_Position = vec4(in_pos, 1.0);
        v_color = in_color;
    }
}
