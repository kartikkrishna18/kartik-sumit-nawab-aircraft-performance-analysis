
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="Aircraft Performance Calculator",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Aircraft Performance Calculator")
st.write("Aircraft performance calculations based on your Sem5 notebook.")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("✈️ Input Parameters")

calculation = st.sidebar.selectbox(
    "Select Calculation",
    [
        "V-n Diagram",
        "Thrust Required vs Available",
        "Altitude Effect on Thrust Required",
        "Maximum Velocity (Vmax)",
        "Vmax at Different Altitudes",
        "Rate of Climb",
        "Power Required and Available"
    ]
)

st.sidebar.markdown("---")

# Common aircraft inputs
S = st.sidebar.number_input("Wing Area S (m²)", value=47.0)
W = st.sidebar.number_input("Aircraft Weight W (N)", value=103047.0)
CD0 = st.sidebar.number_input("Zero Lift Drag Coefficient CD₀", value=0.032)
AR = st.sidebar.number_input("Aspect Ratio AR", value=6.5)
e = st.sidebar.number_input("Oswald Efficiency Factor e", value=0.87)
T_SL = st.sidebar.number_input("Sea Level Thrust Available (N)", value=80596.0)

K = 1 / (np.pi * e * AR)

# --------------------------------------------------
# FUNCTIONS
# --------------------------------------------------

def isa_density(h):
    rho0 = 1.225
    T0 = 288.15
    L = 0.0065
    g = 9.80665
    R = 287.05

    T = T0 - L * h

    return rho0 * (T / T0) ** (g / (R * L) - 1)


def thrust_required(V, rho, S, W, CD0, K):

    q = 0.5 * rho * V**2

    TR = (
        q * S * CD0
        + K * W**2 / (q * S)
    )

    return TR


def find_vmax(V, TR, T_available):

    valid = np.where(TR <= T_available)[0]

    if len(valid) == 0:
        return None

    return V[valid[-1]]


# --------------------------------------------------
# 1. V-N DIAGRAM
# --------------------------------------------------

if calculation == "V-n Diagram":

    st.header("V-n Diagram")

    col1, col2 = st.columns(2)

    with col1:
        rho = st.number_input(
            "Air Density ρ (kg/m³)",
            value=1.006
        )

        CL_max = st.number_input(
            "Maximum Lift Coefficient CLmax",
            value=2.8
        )

    with col2:
        V_max = st.number_input(
            "Maximum Velocity Vmax (m/s)",
            value=300.0
        )

        n_positive = st.number_input(
            "Maximum Positive Load Factor",
            value=5.0
        )

        n_negative = st.number_input(
            "Maximum Negative Load Factor",
            value=-3.0
        )

    V = np.linspace(0, V_max, 500)

    n_up = (
        0.5 * rho * V**2 * S * CL_max / W
    )

    n_up = np.minimum(n_up, n_positive)

    n_down = (
        -0.5 * rho * V**2 * S * CL_max / W
    )

    n_down = np.maximum(n_down, n_negative)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        V,
        n_up,
        label="CL = CLmax (Pitch Up)",
        linewidth=2
    )

    ax.plot(
        V,
        np.full_like(V, n_positive),
        label=f"n = +{n_positive}",
        linewidth=2
    )

    ax.plot(
        [V_max, V_max],
        [n_negative, n_positive],
        label="V = Vmax",
        linewidth=2
    )

    ax.plot(
        V,
        np.full_like(V, n_negative),
        label=f"n = {n_negative}",
        linewidth=2
    )

    ax.plot(
        V,
        n_down,
        label="CL = CLmax (Pitch Down)",
        linewidth=2
    )

    ax.axhline(0)

    ax.set_xlabel("Velocity V (m/s)")
    ax.set_ylabel("Load Factor n")
    ax.set_title("V-n Diagram")

    ax.grid(True)
    ax.legend()

    st.pyplot(fig)


# --------------------------------------------------
# 2. THRUST REQUIRED VS AVAILABLE
# --------------------------------------------------

elif calculation == "Thrust Required vs Available":

    st.header("Thrust Required vs Thrust Available")

    V = np.linspace(10, 500, 500)

    # Original notebook equation
    TR = 0.02 * V**2 + 500000 / V

    TA = st.number_input(
        "Thrust Available TA (N)",
        value=80000.0
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        V,
        TR,
        label="Thrust Required (TR)"
    )

    ax.axhline(
        TA,
        linestyle="--",
        label="Thrust Available (TA)"
    )

    ax.set_xlabel("Velocity (m/s)")
    ax.set_ylabel("Thrust (N)")
    ax.set_title("Thrust Required vs Thrust Available")

    ax.grid()
    ax.legend()

    st.pyplot(fig)


# --------------------------------------------------
# 3. ALTITUDE EFFECT ON THRUST REQUIRED
# --------------------------------------------------

elif calculation == "Altitude Effect on Thrust Required":

    st.header("Effect of Altitude on Thrust Required")

    V = np.linspace(20, 500, 500)

    altitudes = {
        0: 1.225,
        3000: 0.909,
        6000: 0.660,
        9000: 0.466
    }

    fig, ax = plt.subplots(figsize=(10, 6))

    for h, rho in altitudes.items():

        TR = thrust_required(
            V,
            rho,
            S,
            W,
            CD0,
            K
        )

        ax.plot(
            V,
            TR,
            label=f"{h/1000:.0f} km"
        )

    ax.set_xlabel("Velocity (m/s)")
    ax.set_ylabel("Thrust Required (N)")
    ax.set_title("Effect of Altitude on TR")

    ax.grid()
    ax.legend()

    st.pyplot(fig)


# --------------------------------------------------
# 4. MAXIMUM VELOCITY
# --------------------------------------------------

elif calculation == "Maximum Velocity (Vmax)":

    st.header("Maximum Velocity (Vmax)")

    col1, col2 = st.columns(2)

    with col1:
        rho = st.number_input(
            "Air Density ρ (kg/m³)",
            value=1.225
        )

    with col2:
        T_available = st.number_input(
            "Thrust Available (N)",
            value=30000.0
        )

    V = np.linspace(20, 500, 10000)

    TR = thrust_required(
        V,
        rho,
        S,
        W,
        CD0,
        K
    )

    Vmax = find_vmax(
        V,
        TR,
        T_available
    )

    if Vmax is not None:

        st.success(
            f"Vmax = {Vmax:.2f} m/s"
        )

        st.info(
            f"Vmax = {Vmax * 3.6:.2f} km/h"
        )

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(
            V,
            TR,
            label="Thrust Required"
        )

        ax.axhline(
            T_available,
            linestyle="--",
            label="Thrust Available"
        )

        ax.axvline(
            Vmax,
            linestyle="--",
            label=f"Vmax = {Vmax:.1f} m/s"
        )

        ax.set_xlabel("Velocity (m/s)")
        ax.set_ylabel("Thrust (N)")

        ax.grid()
        ax.legend()

        st.pyplot(fig)

    else:
        st.error(
            "No Vmax found for the selected parameters."
        )


# --------------------------------------------------
# 5. VMAX AT DIFFERENT ALTITUDES
# --------------------------------------------------

elif calculation == "Vmax at Different Altitudes":

    st.header("Vmax at Different Altitudes")

    T_available = st.number_input(
        "Thrust Available (N)",
        value=30000.0
    )

    V = np.linspace(20, 500, 10000)

    altitudes = {
        0: 1.225,
        3000: 0.909,
        6000: 0.660,
        9000: 0.466
    }

    results = []

    for h, rho in altitudes.items():

        TR = thrust_required(
            V,
            rho,
            S,
            W,
            CD0,
            K
        )

        Vmax = find_vmax(
            V,
            TR,
            T_available
        )

        if Vmax is not None:

            results.append({
                "Altitude (m)": h,
                "Density (kg/m³)": rho,
                "Vmax (m/s)": round(Vmax, 2),
                "Vmax (km/h)": round(Vmax * 3.6, 2)
            })

        else:

            results.append({
                "Altitude (m)": h,
                "Density (kg/m³)": rho,
                "Vmax (m/s)": "Not Found",
                "Vmax (km/h)": "Not Found"
            })

    st.dataframe(results, use_container_width=True)


# --------------------------------------------------
# 6. RATE OF CLIMB
# --------------------------------------------------

elif calculation == "Rate of Climb":

    st.header("Rate of Climb vs True Airspeed")

    V = np.arange(10, 301)

    alts = [0, 3000]

    rho0 = 1.225

    fig, ax = plt.subplots(figsize=(10, 6))

    results = []

    for h in alts:

        rho = isa_density(h)

        TR = thrust_required(
            V,
            rho,
            S,
            W,
            CD0,
            K
        )

        TA = T_SL * rho / rho0

        ROC = (
            (TA - TR) * V / W
        )

        max_index = np.argmax(ROC)

        max_roc = ROC[max_index]

        max_roc_velocity = V[max_index]

        results.append({
            "Altitude": f"{h/1000:.0f} km",
            "Maximum ROC (m/s)": round(max_roc, 2),
            "Velocity at Max ROC (m/s)": int(max_roc_velocity)
        })

        ax.plot(
            V,
            ROC,
            label=f"{h/1000:.0f} km"
        )

    ax.axhline(
        0,
        linestyle="--"
    )

    ax.set_xlabel("True Airspeed (m/s)")
    ax.set_ylabel("Rate of Climb (m/s)")
    ax.set_title("Rate of Climb vs True Airspeed")

    ax.grid()
    ax.legend()

    st.pyplot(fig)

    st.subheader("Results")
    st.dataframe(results, use_container_width=True)


# --------------------------------------------------
# 7. POWER REQUIRED AND AVAILABLE
# --------------------------------------------------

elif calculation == "Power Required and Available":

    st.header("Power Required and Power Available")

    V = np.arange(10, 301, 10)

    alts = [0, 3000]

    rho0 = 1.225

    fig, ax = plt.subplots(figsize=(10, 6))

    results = []

    for h in alts:

        rho = isa_density(h)

        TR = thrust_required(
            V,
            rho,
            S,
            W,
            CD0,
            K
        )

        PR = TR * V / 1e6

        PA = (
            T_SL * (rho / rho0) * V / 1e6
        )

        Vmp = (
            4 * K * W**2 /
            (
                3 *
                rho**2 *
                S**2 *
                CD0
            )
        ) ** 0.25

        PRmin = np.interp(
            Vmp,
            V,
            PR
        )

        results.append({
            "Altitude": f"{h/1000:.0f} km",
            "Vmp (m/s)": round(Vmp, 2),
            "Minimum PR (MW)": round(PRmin, 3)
        })

        ax.plot(
            V,
            PR,
            marker="o",
            label=f"PR {h/1000:.0f} km"
        )

        ax.plot(
            V,
            PA,
            linestyle="--",
            label=f"PA {h/1000:.0f} km"
        )

    ax.set_xlabel("True Airspeed (m/s)")
    ax.set_ylabel("Power (MW)")
    ax.set_title("Power Required and Power Available")

    ax.grid()
    ax.legend()

    st.pyplot(fig)

    st.subheader("Results")
    st.dataframe(results, use_container_width=True)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption("Aircraft Performance Calculator | Sem5 Project")
