import numpy as np
from scipy.optimize import brentq
from scipy.signal import cont2discrete

from .params import PhaseParams


class SinglePhaseEventDriven:
    """Exact event-driven model of one synchronous buck phase."""

    def __init__(self, params: PhaseParams):
        self.p = params

    def get_matrices(self, sw_state):
        """Return A (2x2) and B (2x3) for the input u = [Vin, i_load, Vf]^T."""
        l_h = self.p.l_h
        c_f = self.p.c_f
        esr_ohm = self.p.esr_ohm

        if sw_state == 'HIGH_SIDE':
            r_tot_ohm = self.p.dcr_ohm + self.p.r_on_h_ohm + esr_ohm
            b11, b13 = 1.0 / l_h, 0.0
        elif sw_state == 'LOW_SIDE':
            r_tot_ohm = self.p.dcr_ohm + self.p.r_on_l_ohm + esr_ohm
            b11, b13 = 0.0, 0.0
        elif sw_state == 'DEAD_TIME_POS':  # i_L > 0 (v_sw = -Vf - Rd*i_L)
            r_tot_ohm = self.p.dcr_ohm + self.p.r_d_ohm + esr_ohm
            b11, b13 = 0.0, -1.0 / l_h
        elif sw_state == 'DEAD_TIME_NEG':  # i_L < 0 (v_sw = Vin + Vf - Rd*i_L)
            r_tot_ohm = self.p.dcr_ohm + self.p.r_d_ohm + esr_ohm
            b11, b13 = 1.0 / l_h, 1.0 / l_h
        elif sw_state == 'DCM':  # i_L = 0: nothing conducts, v_C discharges into the load
            A = np.zeros((2, 2))
            B = np.array([
                [0.0,  0.0,      0.0],
                [0.0, -1.0 / c_f, 0.0]
            ])
            return A, B
        else:
            raise ValueError(f"unknown switching state {sw_state!r}")

        A = np.array([
            [-r_tot_ohm / l_h, -1.0 / l_h],
            [ 1.0 / c_f,        0.0       ]
        ])
        # Matrix B (2x3) -> inputs: [Vin, i_load, Vf]
        B = np.array([
            [b11,  esr_ohm / l_h, b13],
            [0.0, -1.0 / c_f,     0.0]
        ])
        return A, B

    def zoh_step(self, x0, dt_s, sw_state, i_load_a):
        """Exact evolution for a time dt in a fixed switching state."""
        A, B = self.get_matrices(sw_state)
        u = np.array([[self.p.v_in_v], [i_load_a], [self.p.v_f_v]])
        # C and D are dummy matrices: only the state x is needed
        C_dummy = np.eye(2)
        D_dummy = np.zeros(B.shape)

        sys_d = cont2discrete((A, B, C_dummy, D_dummy), dt_s, method="zoh")
        Ad, Bd = sys_d[0], sys_d[1]
        return Ad @ x0 + Bd @ u

    def evolve_interval(self, x0, dt_s, sw_state, i_load_a):
        """Analytically evolve x0 for a duration dt.

        Returns the new state x and the switching state at the end of dt
        (DEAD_TIME resolved to DEAD_TIME_POS, DEAD_TIME_NEG or DCM).
        """
        # Both switches off: the conducting body diode depends on the sign of i_L
        if sw_state == 'DEAD_TIME':
            if x0[0, 0] > 0:
                sw_state = 'DEAD_TIME_POS'
            elif x0[0, 0] < 0:
                sw_state = 'DEAD_TIME_NEG'
            else:
                sw_state = 'DCM'

        if dt_s <= 0:
            return x0, sw_state

        x_next = self.zoh_step(x0, dt_s, sw_state, i_load_a)

        # During a dead time i_L cannot cross zero: the diode turns off (DCM)
        crossed = ((sw_state == 'DEAD_TIME_POS' and x_next[0, 0] < 0) or
                   (sw_state == 'DEAD_TIME_NEG' and x_next[0, 0] > 0))
        if crossed:
            # Exact instant t_zero with i_L(t_zero) = 0 (i_L is monotonic here)
            t_zero_s = brentq(lambda t_s: self.zoh_step(x0, t_s, sw_state, i_load_a)[0, 0],
                              0.0, dt_s, xtol=1e-15)

            # 1. Evolution up to t_zero in the diode state
            x_at_zero = self.zoh_step(x0, t_zero_s, sw_state, i_load_a)
            x_at_zero[0, 0] = 0.0  # force i_L exactly to 0 A

            # 2. Evolution for the remaining time (dt - t_zero) in DCM
            return self.evolve_interval(x_at_zero, dt_s - t_zero_s, 'DCM', i_load_a)

        return x_next, sw_state

    def simulate_period(self, x_init, D, i_load_a, h_s=None):
        """Simulate one full switching period of the phase.

        H is on for exactly D*Tsw and both dead times are taken from the
        low-side (guide 9.4, Appendix B: -14 mV with i_L > 0).
        h_s=None: samples only at the edges. h_s=1e-9: also every h_s, for plots.
        Returns t, x and the switching state of the step ending at each t.
        """
        t_on_h_s = D * self.p.t_sw_s
        t_on_l_s = self.p.t_sw_s - t_on_h_s - self.p.t_df_s - self.p.t_dr_s

        history_x = [x_init]
        history_t_s = [0.0]
        history_state = ['HIGH_SIDE']
        x_curr = x_init
        t_cum_s = 0.0

        # The dead-time state is resolved inside evolve_interval,
        # from the current at the start of that interval
        events = [
            (t_on_h_s,      'HIGH_SIDE'),
            (self.p.t_df_s, 'DEAD_TIME'),
            (t_on_l_s,      'LOW_SIDE'),
            (self.p.t_dr_s, 'DEAD_TIME'),
        ]

        for dt_s, state in events:
            steps = [dt_s] if h_s is None else [h_s] * int(dt_s // h_s) + [dt_s % h_s]
            for step_s in steps:
                x_curr, state_now = self.evolve_interval(x_curr, step_s, state, i_load_a)
                t_cum_s += step_s
                history_t_s.append(t_cum_s)
                history_x.append(x_curr)
                history_state.append(state_now)

        return history_t_s, history_x, history_state

    def output_voltage(self, x, i_load_a):
        """v_o = v_C + ESR*(i_L - i_load), eq. 11.2. x can be (2,1) or (2,n)."""
        return x[1] + self.p.esr_ohm * (x[0] - i_load_a)

    def node_voltage(self, x, sw_state, i_load_a):
        """Switch-node voltage v_sw of eq. 9.2 for a resolved switching state."""
        i_l_a = x[0]
        if sw_state == 'HIGH_SIDE':
            return self.p.v_in_v - self.p.r_on_h_ohm * i_l_a
        if sw_state == 'LOW_SIDE':
            return -self.p.r_on_l_ohm * i_l_a
        if sw_state == 'DEAD_TIME_POS':
            return -self.p.v_f_v - self.p.r_d_ohm * i_l_a
        if sw_state == 'DEAD_TIME_NEG':
            return self.p.v_in_v + self.p.v_f_v - self.p.r_d_ohm * i_l_a
        if sw_state == 'DCM':  # nothing conducts: the node follows the output
            return self.output_voltage(x, i_load_a)
        raise ValueError(f"unknown switching state {sw_state!r}")

    def steady_state(self, D, i_load_a, x_guess, tol_a=1e-7, tol_v=1e-9, max_periods=30000):
        """Periodic steady state, by brute force: simulate one period after the
        other until the state at the end of a period stops changing."""
        x = np.array(x_guess, dtype=float).reshape(2, 1)
        for _ in range(max_periods):
            x_next = self.simulate_period(x, D, i_load_a)[1][-1]
            change = np.abs(x_next - x)
            x = x_next
            if change[0, 0] < tol_a and change[1, 0] < tol_v:
                return x
        raise RuntimeError(f"steady state not found (D={D}, i_load={i_load_a} A)")
