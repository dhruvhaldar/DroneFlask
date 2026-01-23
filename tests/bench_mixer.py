
import timeit
import numpy as np

# Constants
kF = 8.875e-6
kM = 1.203e-7
L = 0.25

# Pre-computed inverse constants
MIXER_F = 1.0 / (4 * kF)
MIXER_PHI = 1.0 / (2 * L * kF)
MIXER_THETA = 1.0 / (2 * L * kF)
MIXER_PSI = 1.0 / (4 * kM)

def mixer_original(F_total, tau_phi, tau_theta, tau_psi):
    term_F = F_total / (4*kF)
    term_phi = tau_phi / (2*L*kF)
    term_theta = tau_theta / (2*L*kF)
    term_psi = tau_psi / (4*kM)

    w1_sq = term_F - term_theta - term_psi
    w2_sq = term_F - term_phi   + term_psi
    w3_sq = term_F + term_theta - term_psi
    w4_sq = term_F + term_phi   + term_psi
    return w1_sq, w2_sq, w3_sq, w4_sq

def mixer_optimized(F_total, tau_phi, tau_theta, tau_psi):
    term_F = F_total * MIXER_F
    term_phi = tau_phi * MIXER_PHI
    term_theta = tau_theta * MIXER_THETA
    term_psi = tau_psi * MIXER_PSI

    w1_sq = term_F - term_theta - term_psi
    w2_sq = term_F - term_phi   + term_psi
    w3_sq = term_F + term_theta - term_psi
    w4_sq = term_F + term_phi   + term_psi
    return w1_sq, w2_sq, w3_sq, w4_sq

def run_benchmark():
    # Inputs
    F_total = 10.0
    tau_phi = 0.1
    tau_theta = -0.1
    tau_psi = 0.05

    # Verify correctness
    res_orig = mixer_original(F_total, tau_phi, tau_theta, tau_psi)
    res_opt = mixer_optimized(F_total, tau_phi, tau_theta, tau_psi)

    assert np.allclose(res_orig, res_opt), "Results do not match!"

    # Benchmark
    iterations = 1000000

    t_orig = timeit.timeit(lambda: mixer_original(F_total, tau_phi, tau_theta, tau_psi), number=iterations)
    t_opt = timeit.timeit(lambda: mixer_optimized(F_total, tau_phi, tau_theta, tau_psi), number=iterations)

    print(f"Original: {t_orig:.4f} s")
    print(f"Optimized: {t_opt:.4f} s")
    print(f"Speedup: {t_orig/t_opt:.2f}x")

if __name__ == "__main__":
    run_benchmark()
