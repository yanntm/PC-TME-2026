import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from matplotlib.backends.backend_pdf import PdfPages

# Read CSV from file or stdin
filename = 'benchmark.csv' if len(sys.argv) == 1 else sys.argv[1]
df = pd.read_csv(filename)

# Pivot for easier plotting (N as index, strategies as columns)
pivot_df = df.pivot(index='N', columns='Strategy', values='Time(us)')

# Define fitting functions
def quad_func(n, a):  # O(n²): a * n**2
    return a * n**2

def linear_func(n, b):  # O(n): b * n
    return b * n

# Fit curves (drop NaNs if any)
ns = np.array(pivot_df.index)

# Fit quadratic to naive
naive_data = pivot_df['naive'].dropna()
naive_data = naive_data[naive_data > 0]  # Exclude zeros
if len(naive_data) > 1:
    popt_quad, _ = curve_fit(quad_func, naive_data.index, naive_data)
    scale_quad = popt_quad[0]
    predicted_quad = quad_func(naive_data.index, scale_quad)
    r2_quad = r2_score(naive_data, predicted_quad)
else:
    scale_quad = 0
    r2_quad = np.nan

# Attempt linear fit on naive for comparison
if len(naive_data) > 1:
    popt_linear_naive, _ = curve_fit(linear_func, naive_data.index, naive_data)
    predicted_linear_naive = linear_func(naive_data.index, *popt_linear_naive)
    r2_linear_naive = r2_score(naive_data, predicted_linear_naive)
else:
    r2_linear_naive = np.nan

# Fit linear to builder_capacity
builder_capacity_data = pivot_df['builder_capacity'].dropna()
builder_capacity_data = builder_capacity_data[builder_capacity_data > 0]
if len(builder_capacity_data) > 1:
    popt_linear_capacity, _ = curve_fit(linear_func, builder_capacity_data.index, builder_capacity_data)
    b_capacity = popt_linear_capacity[0]
    predicted_capacity = linear_func(builder_capacity_data.index, b_capacity)
    r2_capacity = r2_score(builder_capacity_data, predicted_capacity)
else:
    b_capacity = 0
    r2_capacity = np.nan

# Fit linear to builder_default
builder_default_data = pivot_df['builder_default'].dropna()
builder_default_data = builder_default_data[builder_default_data > 0]
if len(builder_default_data) > 1:
    popt_linear_default, _ = curve_fit(linear_func, builder_default_data.index, builder_default_data)
    b_default = popt_linear_default[0]
    predicted_default = linear_func(builder_default_data.index, b_default)
    r2_default = r2_score(builder_default_data, predicted_default)
else:
    b_default = 0
    r2_default = np.nan

# Convert to ns
quad_a_ns = scale_quad * 1000  # us/N² to ns/N²
b_capacity_ns = b_capacity * 1000  # us/N to ns/N
b_default_ns = b_default * 1000  # us/N to ns/N

# Select points: N=10000, 100000, 300000 (assume present; adjust if not)
n_points = [10000, 100000, 300000]
n_labels = ['10⁴', '10⁵', '3×10⁵']

# Get times at points
def get_time(strategy, n):
    if n in pivot_df.index:
        return pivot_df[strategy].loc[n]
    return np.nan

# Effective ns/char = (time_us * 1000) / N
def effective_ns_per_char(time_us, n):
    return (time_us * 1000) / n if not np.isnan(time_us) and n > 0 else np.nan

# Collect effective ns/char
eff_naive = [effective_ns_per_char(get_time('naive', n), n) for n in n_points]
eff_default = [effective_ns_per_char(get_time('builder_default', n), n) for n in n_points]
eff_capacity = [effective_ns_per_char(get_time('builder_capacity', n), n) for n in n_points]

# Ratios
def ratio(a, b):
    return a / b if not np.isnan(a) and not np.isnan(b) and b > 0 else np.nan

ratio_naive_default = [ratio(get_time('naive', n), get_time('builder_default', n)) for n in n_points]
ratio_naive_capacity = [ratio(get_time('naive', n), get_time('builder_capacity', n)) for n in n_points]
ratio_default_capacity = [ratio(get_time('builder_default', n), get_time('builder_capacity', n)) for n in n_points]

# Print summary
print("Summary of Benchmark Data:\n")
print("Key:")
print("naive: String only")
print("default: StringBuilder()")
print("capacity: StringBuilder(n)\n")

print(f"Naive does not fit a linear regression (R²={r2_linear_naive:.2f}), but fits quadratic well (R²={r2_quad:.2f}).")
print(f"Linear regression fits default to {b_default_ns:.2f} ns/char (R²={r2_default:.2f}).")
print(f"Linear regression fits capacity to {b_capacity_ns:.2f} ns/char (R²={r2_capacity:.2f}).\n")

print("Speed of strategies in ns/char:")
print(f"naive: {eff_naive[0]:.2f} ns/char at {n_labels[0]}, {eff_naive[1]:.2f} ns/char at {n_labels[1]}, {eff_naive[2]:.2f} ns/char at {n_labels[2]}")
print(f"default: {eff_default[0]:.2f} ns/char at {n_labels[0]}, {eff_default[1]:.2f} ns/char at {n_labels[1]}, {eff_default[2]:.2f} ns/char at {n_labels[2]}")
print(f"capacity: {eff_capacity[0]:.2f} ns/char at {n_labels[0]}, {eff_capacity[1]:.2f} ns/char at {n_labels[1]}, {eff_capacity[2]:.2f} ns/char at {n_labels[2]}\n")

print("Ratios:")
print(f"naive/default: {ratio_naive_default[0]:.2f} at {n_labels[0]}, {ratio_naive_default[1]:.2f} at {n_labels[1]}, {ratio_naive_default[2]:.2f} at {n_labels[2]}")
print(f"naive/capacity: {ratio_naive_capacity[0]:.2f} at {n_labels[0]}, {ratio_naive_capacity[1]:.2f} at {n_labels[1]}, {ratio_naive_capacity[2]:.2f} at {n_labels[2]}")
print(f"default/capacity: {ratio_default_capacity[0]:.2f} at {n_labels[0]}, {ratio_default_capacity[1]:.2f} at {n_labels[1]}, {ratio_default_capacity[2]:.2f} at {n_labels[2]}")

# Create PDF with multiple pages
with PdfPages('benchmark.pdf') as pdf:

    # First page: All strategies
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    for strategy in pivot_df.columns:
        ax1.plot(pivot_df.index, pivot_df[strategy], label=strategy, marker='o')

    # Theoretical overlays: quad + default linear fit
    ax1.plot(ns, quad_func(ns, scale_quad), '--', label=f'O(n²) fit ({quad_a_ns:.3f} ns/N²)')
    ax1.plot(ns, linear_func(ns, b_default), '--', label=f'O(n) default fit ({b_default_ns:.2f} ns/char)')

    ax1.set_xlabel('N')
    ax1.set_ylabel('Time (us)')
    ax1.set_title('Execution Time vs. N for All Repeat Strategies')
    ax1.legend()
    ax1.grid(True)
    # ax1.set_xscale('log')
    # ax1.set_yscale('log')  # Uncomment if needed

    pdf.savefig(fig1)
    plt.close(fig1)

    # Second page: Only linear strategies
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    linear_strategies = ['builder_default', 'builder_capacity']
    for strategy in linear_strategies:
        if strategy in pivot_df.columns:
            ax2.plot(pivot_df.index, pivot_df[strategy], label=strategy, marker='o')

    # Theoretical overlays: capacity and default fits
    ax2.plot(ns, linear_func(ns, b_capacity), '--', label=f'O(n) capacity fit ({b_capacity_ns:.2f} ns/char)')
    ax2.plot(ns, linear_func(ns, b_default), '--', label=f'O(n) default fit ({b_default_ns:.2f} ns/char)')

    ax2.set_xlabel('N')
    ax2.set_ylabel('Time (us)')
    ax2.set_title('Execution Time vs. N for Linear Repeat Strategies')
    ax2.legend()
    ax2.grid(True)
    #ax2.set_xscale('log')
    # ax2.set_yscale('log')  # Uncomment if needed

    pdf.savefig(fig2)
    plt.close(fig2)

print("\nSuccessfully produced file benchmark.pdf")