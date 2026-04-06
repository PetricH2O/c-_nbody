#include <pybind11/numpy.h>
#include <cmath>

namespace py = pybind11;

/*碰撞，直接修改position_arr和velocity_arr*/
void check_collision_inplace_impl(
    py::array_t<double> mass_arr,
    py::array_t<double> position_arr,
    py::array_t<double> velocity_arr,
    double radius,
    double restitution
) {
    auto mass = mass_arr.unchecked<1>();
    auto pos = position_arr.mutable_unchecked<2>();
    auto vel = velocity_arr.mutable_unchecked<2>();

    py::ssize_t N = mass.shape(0);
    double radius_sum = 2.0 * radius;

    for (py::ssize_t i = 0;i<N; i++) {
        for (py::ssize_t j = i + 1; j <N; j++) {
            double dx =pos(j, 0) - pos(i, 0);
            double dy =pos(j, 1) - pos(i, 1);
            double dz =pos(j, 2) - pos(i, 2);

            double dist2 = dx * dx + dy * dy + dz * dz;
            double dist = std::sqrt(dist2);

            if (dist >= radius_sum) continue;

            if (dist == 0.0) continue;

            double m1 = mass(i);
            double m2 = mass(j);
            double total_mass = m1 + m2;

            //碰撞法向量 s= (pos2-pos1)/distance
            double sx = dx / dist;
            double sy = dy / dist;
            double sz = dz / dist;
            //重疊修正
            double overlap = radius_sum - dist;

            pos(i, 0) -=sx*(overlap *(m2 / total_mass));
            pos(i, 1) -=sy * (overlap * (m2 / total_mass));
            pos(i, 2) -= sz*(overlap * (m2 / total_mass));

            pos(j, 0) +=sx*(overlap *(m1 / total_mass));
            pos(j, 1) +=sy * (overlap * (m1 / total_mass));
            pos(j, 2) += sz*(overlap * (m1 / total_mass));
            //法向量速度分量
            double v1n = vel(i, 0) * sx + vel(i, 1) * sy + vel(i, 2) * sz;
            double v2n = vel(j, 0) * sx + vel(j, 1) * sy + vel(j, 2) * sz;
            //碰撞後法向速度
            double v1n_final =
                ((m1 - restitution * m2) * v1n +
                 (1.0 + restitution) * m2 * v2n) / total_mass;
            double v2n_final =
                ((m2 - restitution * m1) * v2n +
                 (1.0 + restitution) * m1 * v1n) / total_mass;
            // 更新速度
            double dv1= v1n_final - v1n;
            double dv2 = v2n_final - v2n;

            vel(i,0)+= dv1 * sx;
            vel(i,1)+= dv1 * sy;
            vel(i,2)+= dv1 * sz;

            vel(j,0) += dv2 * sx;
            vel(j, 1) += dv2 * sy;
            vel(j, 2) += dv2 * sz;
        }
    }
}