#include <pybind11/numpy.h>
#include <cmath>
#include <vector>

namespace py = pybind11;


/* 加速度nbody_cpp.get_acc(position, mass, G, softening)
參數：
    position_arr: shape = (N, 3)
    mass_arr: shape = (N,)
    G:
    softening:
=> shape = (N, 3) 的加速度陣列 */

py::array_t<double> get_acc_impl(
    py::array_t<double> position_arr,
    py::array_t<double> mass_arr,
    double G,
    double softening
) {
    auto pos = position_arr.unchecked<2>();
    auto mass = mass_arr.unchecked<1>();

    py::ssize_t N = pos.shape(0);

    std::vector<py::ssize_t> shape = {N, 3};
    py::array_t<double> acc(shape);
    auto acc_buf = acc.mutable_unchecked<2>();

    for (py::ssize_t i = 0; i < N; ++i) {
        double ax = 0.0;//初始化a
        double ay = 0.0;
        double az = 0.0;

        for (py::ssize_t j = 0; j < N; ++j) {
            if (i == j) continue;//省略自己

            double dx = pos(j, 0) - pos(i, 0);
            double dy = pos(j, 1) - pos(i, 1);
            double dz = pos(j, 2) - pos(i, 2);

            double r2 = dx * dx + dy * dy + dz * dz + softening * softening;
            if (r2 <= 0.0) continue;

            double inv_r = 1.0 / std::sqrt(r2);
            double inv_r3 = inv_r * inv_r * inv_r;

            ax += G * dx * inv_r3 * mass(j);
            ay += G * dy * inv_r3 * mass(j);
            az += G * dz * inv_r3 * mass(j);
        }

        acc_buf(i, 0) = ax;
        acc_buf(i, 1) = ay;
        acc_buf(i, 2) = az;
    }

    return acc;
}