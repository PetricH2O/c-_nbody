#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

// 宣告其他cpp檔裡的函式
py::array_t<double> get_acc_impl(
    py::array_t<double> position_arr,
    py::array_t<double> mass_arr,
    double G,
    double softening
);
void check_collision_inplace_impl(
    py::array_t<double> mass_arr,
    py::array_t<double> position_arr,
    py::array_t<double> velocity_arr,
    double radius,
    double restitution
);

/*nbody_cpp(import nbody_cpp)*/
PYBIND11_MODULE(nbody_cpp, m) {
    m.doc() = "N-body C++ backend";

    //綁定加速度
    m.def(
        "get_acc",
        &get_acc_impl,
        py::arg("position"),
        py::arg("mass"),
        py::arg("G"),
        py::arg("softening"),
        "Compute acceleration for N-body system"
    );

    //綁定碰撞
    m.def(
        "check_collision_inplace",
        &check_collision_inplace_impl,
        py::arg("mass"),
        py::arg("position"),
        py::arg("velocity"),
        py::arg("radius"),
        py::arg("restitution") = 0.7,
        "Resolve collisions in-place"
    );
}