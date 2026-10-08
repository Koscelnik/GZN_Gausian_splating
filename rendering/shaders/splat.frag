#version 330 core

in vec4 v_color;
in vec3 v_conic;   // (a_inv, b_inv, c_inv)
in float v_radius; // Polomer splatu v pixeloch

out vec4 fragColor;

void main() {
    // gl_PointCoord je v rozsahu [0, 1] x [0, 1]
    // Prevedieme ho na relatívny offset v pixeloch od stredu [-v_radius, +v_radius]
    vec2 offset = (gl_PointCoord * 2.0 - 1.0) * v_radius;

    // Gaussova kvadratická forma: 0.5 * (x^T * Sigma_2D^-1 * x)
    // P = 0.5 * (a * dx^2 + 2 * b * dx * dy + c * dy^2)
    float power = 0.5 * (v_conic.x * offset.x * offset.x + 
                         2.0 * v_conic.y * offset.x * offset.y + 
                         v_conic.z * offset.y * offset.y);

    // Ak sme mimo 3-sigma obálky, zahodíme pixel
    if (power > 4.5) {
        discard;
    }

    // Exponenciálny útlm (Gaussian Falloff)
    float alpha = v_color.a * exp(-max(0.0, power));

    if (alpha < 0.005) {
        discard;
    }

    fragColor = vec4(v_color.rgb, alpha);
}
