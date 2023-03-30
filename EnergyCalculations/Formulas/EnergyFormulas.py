from math import log, exp

def _Toff(t: float, beta: float, Tmax: float, Tout: float) -> float:
    """Function of time representing the temperature drop when the central HVAC system is off

    Args:
        t (float): time, t=0 outputs the temperature immediately after the system shut off
        beta (float): cooling coefficient
        Tmax (float): maximum temperature the system reaches before turning off, also equals the Toff at t=0
        Tout (float): outside temperature

    Returns:
        float: temperature at time t
    """
    return exp(-beta*t + log(Tmax - Tout)) + Tout

def EnergyContinuous(tcd: float, Tt: float, sigma: float, Tout: float, beta: float):
    """Calculates the energy usage per unit time of a normal HVAC system

    Args:
        tcd (float): system delay in recognizing target temperature has been reached/dropped below (time system is over/undershooting)
        Tt (float): target temperature
        Ts (float): start temperature
        sigma (float): heating coefficient from alpha=sigma*louver_position
        Tout (float): outside temperature
        beta (float): cooling coefficient from background heat loss equation

    Returns:
        float: energy usage per unit time of a normal (continuous) system
    """
    Tmax = Tt + sigma*tcd
    tTOoff = log((Tt - Tout) / (Tmax - Tout)) / -beta
    tTUoff = tcd
    toff = tTOoff + tTUoff
    TE = _Toff(toff, beta, Tmax, Tout)
    TS = TE
    tTUon = (Tt - TS) / sigma
    tTOon = tcd
    ton = tTOon + tTUon

    print(f'Ec Tmax: {Tmax}')
    print(f'Ec TE: {TE}')
    return ton / (ton + toff)

def EnergySmartVents(td:float, Tt: float, TS: float, sigma: float, Tout: float, beta: float, p: float):
    """Calculates the energy usage per unit time of the "Smart Vents" system

    Args:
        td (float): time-step for the system
        Tt (float): target temperature  
        Ts (float): start temperature
        sigma (float): heating coefficient from alpha=sigma*louver_position
        Tout (float): outside temperature
        beta (float): cooling coefficient from background heat loss equation
        p (float): louver position 0<=p<=1

    Returns:
        float: energy usage per unit time of the "Smart Vents" system
    """
    alpha = sigma * p
    tTUon = ((Tt - TS) // (sigma*td)) * td + ((Tt - TS) % (sigma*td)) / alpha
    tTOon = td - (tTUon % td)
    Tmax = Tt + alpha*tTOon
    tTOoff = log((Tt - Tout) / (Tmax - Tout)) / -beta
    tTUoff = td - (tTOoff % td)
    ton = tTOon + tTUon
    toff = tTOoff + tTUoff
    TE = _Toff(toff, beta, Tmax, Tout)

    print(f'Ed Tmax: {Tmax}')
    print(f'Ed TE: {TE}')
    return ton / (ton + toff)

def main():
    tcd = 0.5
    Tt = 72
    sigma = 1
    Tout = 50
    beta = 0.01

    Ts = 71
    td = 0.5
    p = 1

    print(EnergyContinuous(tcd, Tt, sigma, Tout, beta))
    print(EnergySmartVents(td, Tt, Ts, sigma, Tout, beta, p))

if __name__ == "__main__":
    main()