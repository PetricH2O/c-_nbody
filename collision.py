#collision.py
#testgit
def check_collision(distance, radius, mass_list, position_list, velocity_list, using_cuda):
    """
    碰撞檢測與處理
    """
    if using_cuda:
        import cupy as cp
    else:
        import numpy as cp

    radius_sum = 2 * radius


    distance_tri = cp.triu(distance, k=1)
    distance_tri += cp.tril(cp.full(distance_tri.shape, cp.inf), k=-1)
    cp.fill_diagonal(distance_tri, cp.inf)

    collision_matrix = distance_tri - radius_sum


    collision_indices = cp.where(collision_matrix < 0)

    for i, j in zip(collision_indices[0], collision_indices[1]):

        mass1 = mass_list[i]
        mass2 = mass_list[j]
        pos1 = position_list[i]
        pos2 = position_list[j]
        v1 = velocity_list[i]
        v2 = velocity_list[j]


        v1_new, v2_new, pos1_new, pos2_new = calculate_collision_velocity(
            mass1, pos1, v1, mass2, pos2, v2, 0.7, radius, using_cuda
        )


        velocity_list[i] = v1_new
        velocity_list[j] = v2_new
        position_list[i] = pos1_new
        position_list[j] = pos2_new

    return velocity_list, position_list

def calculate_collision_velocity(mass1, pos1, v1, mass2, pos2, v2, restitution_coefficient, radius, using_cuda):
    if using_cuda:
        import cupy as cp
    else:
        import numpy as cp


    direction = pos2 - pos1
    distance = cp.linalg.norm(direction)
    if distance == 0:
        return v1, v2, pos1, pos2  # 避免除以零

    overlap = 2 * radius - distance
    s = direction / distance

    total_mass = mass1 + mass2


    pos1 -= s * (overlap * (mass2 / total_mass))
    pos2 += s * (overlap * (mass1 / total_mass))


    v1n = cp.dot(v1, s)
    v2n = cp.dot(v2, s)


    v1n_final = (
        (mass1 - restitution_coefficient * mass2) * v1n +
        (1 + restitution_coefficient) * mass2 * v2n
    ) / total_mass

    v2n_final = (
        (mass2 - restitution_coefficient * mass1) * v2n +
        (1 + restitution_coefficient) * mass1 * v1n
    ) / total_mass


    v1 += (v1n_final - v1n) * s
    v2 += (v2n_final - v2n) * s

    return v1, v2, pos1, pos2
