"""Constant-voltage speaker circuit dB loss and amplifier loading.
Source: NFPA 72-2025 A.18.3.7.2.1, annex, informative.
  dB loss = 20 * log10( Z_load / (Z_load + R_circuit) ),  Z_load = V^2 / P_taps.
Limit: NFPA 72-2025 18.3.7.2.1(1), 1.0 dB electrical loss; where adopted; AHJ to confirm.
Max length for target loss L (dB), solved from eq a: R_max = Z (10^(L/20) - 1); length = R_max / r_pair.
For L = 0.5 this gives the annex constant 59.25 per 1000 ft (A.18.3.7.2.1g).
Amp spare: 20% default is a screening value. Verify with the engineer of record."""
import math
def z_load(v, watts): return v * v / watts
def loss_db(v, watts, r_circuit): z = z_load(v, watts); return 20 * math.log10(z / (z + r_circuit))
def k_factor(target_db): return 1000 * (10 ** (target_db / 20) - 1)   # 0.5 dB -> 59.25
def max_len_ft(v, watts, r_pair_per_kft, target_db=1.0):
    return k_factor(target_db) * v * v / (r_pair_per_kft * watts)
def amp_check(load_w, rating_w, spare=0.20):
    cap = rating_w * (1 - spare); return load_w <= cap, cap
