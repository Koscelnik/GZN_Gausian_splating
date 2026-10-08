#version 330 core

// Vstupné atribúty pre každý Gauss
layout(location = 0) in vec3 in_position;    // 3D stred (mean mu)
layout(location = 1) in vec4 in_color;       // Farba RGB + Opacity
layout(location = 2) in vec3 in_scale;       // Mierka polosí (s_x, s_y, s_z)
layout(location = 3) in vec4 in_rotation;    // Kvaternión [w, x, y, z]

// Uniformy z kamery a okna
uniform mat4 u_view;         // Pohľadová matica (World -> Camera)
uniform mat4 u_projection;   // Projekčná matica
uniform vec2 u_viewport;     // Rozlíšenie okna (šírka, výška v pixeloch)
uniform float u_focal;       // Ohnisková vzdialenosť v pixeloch
uniform float u_opacity_mult; // Násobiteľ priehľadnosti (1.0 = originál)

// Výstupy pre Fragment Shader
out vec4 v_color;
out vec3 v_conic;            // Prvky inverznej 2D kovariančnej matice (a, b, c)
out float v_radius;          // Polomer splatu v pixeloch

// Prevod jednotkového kvaterniónu na 3x3 rotačnú maticu
mat3 quatToMat3(vec4 q) {
    float w = q.x;
    float x = q.y;
    float y = q.z;
    float z = q.w;

    return mat3(
        1.0 - 2.0 * (y*y + z*z),  2.0 * (x*y + w*z),        2.0 * (x*z - w*y),
        2.0 * (x*y - w*z),        1.0 - 2.0 * (x*x + z*z),  2.0 * (y*z + w*x),
        2.0 * (x*z + w*y),        2.0 * (y*z - w*x),        1.0 - 2.0 * (x*x + y*y)
    );
}

void main() {
    v_color = vec4(in_color.rgb, clamp(in_color.a * u_opacity_mult, 0.0, 1.0));

    // 1. Transformácia stredu do priestoru kamery (Camera Space)
    vec4 p_cam = u_view * vec4(in_position, 1.0);

    // V OpenGL sa kamera pozerá v smere -Z, takže body pred kamerou majú p_cam.z < 0.
    // tz je kladná hĺbka pred kamerou.
    float tz = -p_cam.z;

    // Orezanie: ak je bod za kamerou alebo príliš blízko (bližšie než 0.1m)
    if (tz <= 0.1) {
        gl_Position = vec4(0.0, 0.0, 2.0, 1.0);
        gl_PointSize = 0.0;
        return;
    }

    // 2. Výpočet 3D kovariančnej matice Sigma = R * S * S^T * R^T
    mat3 R = quatToMat3(in_rotation);
    mat3 S = mat3(
        in_scale.x, 0.0, 0.0,
        0.0, in_scale.y, 0.0,
        0.0, 0.0, in_scale.z
    );
    mat3 M = R * S;
    mat3 Vrk = M * transpose(M); // 3D kovariancia vo World Space

    // Transformácia do Camera Space: Sigma_cam = W * Sigma * W^T
    mat3 W = mat3(u_view);
    mat3 Sigma_cam = W * Vrk * transpose(W);

    // 3. Jacobiho matica (Jacobian) projektívnej transformácie
    float fx = u_focal;
    float fy = u_focal;
    float tz2 = tz * tz;

    // J mapuje 3D kamerový priestor na 2D pixelový priestor
    mat3x2 J = mat3x2(
        fx / tz,   0.0,
        0.0,       fy / tz,
        -(fx * p_cam.x) / tz2, -(fy * p_cam.y) / tz2
    );

    // 4. Projekcia do 2D kovariancie: Sigma_2D = J * Sigma_cam * J^T
    mat2 Sigma_2D = J * Sigma_cam * transpose(J);

    // Anti-aliasing filter: prirátanie 0.3 px k rozptylu (nízkofrekvenčný filter)
    Sigma_2D[0][0] += 0.3;
    Sigma_2D[1][1] += 0.3;

    // 5. Inverzná matica (Conic) pre fragment shader
    float a = Sigma_2D[0][0];
    float b = Sigma_2D[0][1];
    float c = Sigma_2D[1][1];

    float det = a * c - b * b;
    if (det <= 0.0001) {
        gl_Position = vec4(0.0, 0.0, 2.0, 1.0);
        gl_PointSize = 0.0;
        return;
    }

    // Conic = Sigma_2D^-1 = (1/det) * [c, -b; -b, a]
    v_conic = vec3(c / det, -b / det, a / det);

    // 6. Výpočet ohraničujúcej obálky (3-sigma polomer v pixeloch)
    float mid = 0.5 * (a + c);
    float discr = max(0.0, mid * mid - det);
    float lambda1 = mid + sqrt(discr);
    float lambda2 = max(0.1, mid - sqrt(discr));
    float radius = ceil(3.0 * sqrt(max(lambda1, lambda2)));

    // Veľkosť bodu v pixeloch a finálna pozícia
    float psize = clamp(2.0 * radius, 2.0, 512.0);
    gl_PointSize = psize;
    v_radius = psize * 0.5;
    gl_Position = u_projection * p_cam;
}
