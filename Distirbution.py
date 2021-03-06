import pandas as pd
import scipy as sp
from scipy import interpolate
import numpy as np
import matplotlib.pyplot as plt
import blade_speed as bs


def txt_to_csv(file, name):
    read_file = pd.read_csv(file)
    read_file.to_csv("measurements/loads/" + name + ".csv", index=None)


def find_dist():
    data = np.genfromtxt("measurements/loads/dataset.csv", delimiter=",", skip_header=1, usecols=(1, 2, -1))
    CL_list = [CL for CL, CD, x in data]
    x_list = [x for CL, CD, x in data]
    CD_list = [CD for CL, CD, x in data]
    plt.subplot(1, 2, 1)
    plt.title("Lift Coefficient Along Span")
    plt.plot(x_list, CL_list, "r-")
    plt.xlabel("x[-]")
    plt.ylabel("CL[-]")
    plt.grid()
    plt.subplot(1, 2, 2)
    plt.title("Drag Coefficient Along Span")
    plt.plot(x_list, CD_list, "b-")
    plt.xlabel("x[-]")
    plt.ylabel("CD[-]")
    plt.grid()
    plt.show()
    L_tot_func = sp.interpolate.interp1d(x_list, CL_list, kind="nearest-up")
    D_tot_func = sp.interpolate.interp1d(x_list, CD_list, kind="nearest-up")

    return L_tot_func, D_tot_func


print(find_dist()[0](1))


def getForces():
    file = pd.read_csv("measurements/loads/no_grid.csv", header=None, usecols=[2, 5])
    # Bias that needs to be substracted
    bias = pd.read_csv("measurements/loads/bias.csv", header=None, usecols=[2, 5])
    print(bias.size)
    bias = bias.head(round(file.size / 2))
    print(bias.size)
    df = file.sub(bias)
    n = round(file.size / 2)

    x = pd.DataFrame(np.linspace(0, 20, n))

    df = pd.concat([df, x], axis=1, ignore_index=True)
    df.columns = ["Thrust", "Torque", "Time"]
    df.to_csv("measurements/loads/no_gridUPDATED.csv", index=None)


# Runs the no grid loads, updated
df = pd.read_csv("measurements/loads/no_gridUPDATED.csv")

fig, (ax1, ax2, ax3) = plt.subplots(3)
ax1.scatter(df["Time"], df["Thrust"])
ax2.scatter(df["Time"], df["Torque"])
ax3.scatter(df["Torque"], df["Thrust"])
plt.show()

Thrust_rms = np.sqrt(sum(df["Thrust"] ** 2) / df["Thrust"].size)

Torque_rms = np.sqrt(sum(df["Torque"] ** 2) / df["Torque"].size)


def cx(cl, cd, phi):
    """Input phi in degrees, everything as numpy array"""
    phi = phi * np.pi / 180
    return cl * np.sin(phi) - cd * np.cos(phi)


def cy(cl, cd, phi):
    """Input phi in degrees, everything as numpy array"""
    phi = phi * np.pi / 180
    return cl * np.cos(phi) + cd * np.sin(phi)


rho = 1.225


def Torque(r, cx_):
    """Per blade segment, cx is the return function of cx"""
    vtot, x, y = bs.bladeSection(r)
    c = bs.chord_poly(x)
    return 0.5 * rho * vtot ** 2 * c * cx_ * r


def Thrust(r, cy_):
    """per blade segment, cy is the return function of cy"""
    vtot, x, y = bs.bladeSection(r)
    c = bs.chord_poly(x)
    return 0.5 * rho * vtot ** 2 * c * cy_


df = pd.read_csv(r"measurements/loads/CP_data2.csv")

cx_ = cx(df["CL"], df["CD"], df["alpha"])
cy_ = cy(df["CL"], df["CD"], df["alpha"])

ThrustM = np.average(Thrust(df["r"], cy_))*.15
TorqueM = np.average(Torque(df["r"], cx_))*.15

print(f"Real values: {Thrust_rms}, {Torque_rms}\n Approx values: {ThrustM}, {TorqueM}")