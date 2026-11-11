# SPDX-FileCopyrightText: 2026 VRM4-HIL authors (see NOTICE)
# SPDX-License-Identifier: Apache-2.0

"""Checks of the single-phase reference model against the spec (guide 9.2-9.4,
Appendix B). These are the automatic tests requested by section 8.3 for
notebook 01_single_phase."""

import numpy as np
import pytest

from vrm4hil_model.params import load_params, phase_params
from vrm4hil_model.single_phase import SinglePhaseEventDriven

V_OUT_V = 0.80
SETTLE_PERIODS = 2000  # from a rough initial state to steady state


@pytest.fixture(scope="module")
def model():
    loaded_params = load_params()
    return SinglePhaseEventDriven(phase_params(loaded_params, 1, "M0"))


def duty(pp, i_avg_a):
    """Eq. 9.3 (dead time neglected)."""
    D0 = V_OUT_V / pp.v_in_v
    r_ph_ohm = pp.dcr_ohm + D0 * pp.r_on_h_ohm + (1 - D0) * pp.r_on_l_ohm
    return (V_OUT_V + r_ph_ohm * i_avg_a) / pp.v_in_v


def steady_period(model, D, i_load_a, i_start_a):
    """One period at steady state, sampled every 1 ns. Returns t_s, i_L_a, v_out_v."""
    x = np.array([[i_start_a], [V_OUT_V]])
    for _ in range(SETTLE_PERIODS):
        _, xs, _ = model.simulate_period(x, D, i_load_a)
        x = xs[-1]
    t_s, xs, _ = model.simulate_period(x, D, i_load_a, h_s=1e-9)
    X = np.hstack(xs)
    v_out_v = X[1] + model.p.esr_ohm * (X[0] - i_load_a)
    return np.array(t_s), X[0], v_out_v


def period_avg(t_s, y):
    return np.trapezoid(y, t_s) / (t_s[-1] - t_s[0])


def test_positive_current_dead_time_costs_14_mV(model):
    pp, i_load_a = model.p, 25.0
    t_s, i_L_a, v_out_v = steady_period(model, duty(pp, i_load_a), i_load_a, i_load_a - 5.0)
    expected_v = V_OUT_V - pp.v_f_v * (pp.t_dr_s + pp.t_df_s) * pp.f_sw_hz  # Appendix B: -14 mV
    assert period_avg(t_s, v_out_v) == pytest.approx(expected_v, abs=1.5e-3)
    assert period_avg(t_s, i_L_a) == pytest.approx(i_load_a, abs=0.05)


def test_phase_ripple_matches_eq_9_4(model):
    pp, i_load_a = model.p, 25.0
    D = duty(pp, i_load_a)
    _, i_L_a, _ = steady_period(model, D, i_load_a, i_load_a - 5.0)
    expected_a = (pp.v_in_v - V_OUT_V) * D / (pp.l_h * pp.f_sw_hz)
    assert np.ptp(i_L_a) == pytest.approx(expected_a, rel=0.02)


def test_negative_current_dead_time_adds_254_mV(model):
    pp, i_load_a = model.p, -10.0
    t_s, _, v_out_v = steady_period(model, duty(pp, i_load_a), i_load_a, i_load_a)
    gain_v = (pp.v_in_v + pp.v_f_v) * (pp.t_dr_s + pp.t_df_s) * pp.f_sw_hz  # Appendix B: +254 mV
    assert period_avg(t_s, v_out_v) == pytest.approx(V_OUT_V + gain_v, abs=3e-3)


@pytest.mark.parametrize("i_start_a", [+0.1, -0.5])
def test_current_stops_at_zero_in_dead_time(model, i_start_a):
    """A small current dies out within the dead time and must stay at 0 A.
    Slopes: about -10 A/us with i > 0 (-Vf - Vo), +80 A/us with i < 0 (Vin + Vf - Vo)."""
    x0 = np.array([[i_start_a], [V_OUT_V]])
    x, state = model.evolve_interval(x0, 20e-9, 'DEAD_TIME', i_load_a=0.0)
    assert x[0, 0] == 0.0
    assert state == 'DCM'


def test_dense_output_agrees_with_edge_output(model):
    """Sampling with h_s must not change the result (both are exact)."""
    pp, i_load_a = model.p, 25.0
    x0 = np.array([[i_load_a], [V_OUT_V]])
    _, edges, _ = model.simulate_period(x0, duty(pp, i_load_a), i_load_a)
    _, dense, _ = model.simulate_period(x0, duty(pp, i_load_a), i_load_a, h_s=1e-9)
    np.testing.assert_allclose(dense[-1], edges[-1], rtol=1e-9, atol=1e-9)


@pytest.mark.parametrize("D, i_load_a", [(0.0723, 25.0), (0.05, -10.0), (0.07, 5.0)])
def test_steady_state_is_a_fixed_point(model, D, i_load_a):
    """Steady state: one more period gives back the same state,
    and the inductor carries the load on average (CCM, valley at zero, DCM)."""
    x = model.steady_state(D, i_load_a, [[i_load_a], [D * model.p.v_in_v]])
    t_s, xs, _ = model.simulate_period(x, D, i_load_a, h_s=1e-9)
    np.testing.assert_allclose(xs[-1], x, rtol=0, atol=1e-6)
    assert period_avg(np.array(t_s), np.hstack(xs)[0]) == pytest.approx(i_load_a, abs=1e-3)


def test_dcm_holds_the_current_at_zero(model):
    """In DCM nothing conducts: i_L stays at 0 A and C alone feeds the load."""
    i_load_a, dt_s = 10.0, 100e-9
    x0 = np.array([[0.0], [V_OUT_V]])
    x, state = model.evolve_interval(x0, dt_s, 'DCM', i_load_a)
    assert state == 'DCM'
    assert x[0, 0] == 0.0
    assert x[1, 0] == pytest.approx(V_OUT_V - i_load_a * dt_s / model.p.c_f)


def test_large_current_does_not_stop_in_dead_time(model):
    """20 A cannot die out in 20 ns: the diode conducts for the whole interval."""
    x0 = np.array([[20.0], [V_OUT_V]])
    x, state = model.evolve_interval(x0, 20e-9, 'DEAD_TIME', i_load_a=20.0)
    assert state == 'DEAD_TIME_POS'
    assert 19.0 < x[0, 0] < 20.0


def test_low_side_current_goes_through_zero(model):
    """The low-side is a channel: unlike a diode it does not stop at 0 A."""
    x0 = np.array([[0.5], [V_OUT_V]])
    x, state = model.evolve_interval(x0, 200e-9, 'LOW_SIDE', i_load_a=0.0)
    assert state == 'LOW_SIDE'
    assert x[0, 0] < 0.0


def test_node_voltage_in_each_state(model):
    """Eq. 9.2 with no drop (i_L = 0 A) in the channels, and at 10 A on the diode."""
    pp = model.p
    x_zero = np.array([0.0, V_OUT_V])
    x_pos = np.array([10.0, V_OUT_V])
    assert model.node_voltage(x_zero, 'HIGH_SIDE', 0.0) == pp.v_in_v
    assert model.node_voltage(x_zero, 'LOW_SIDE', 0.0) == 0.0
    assert model.node_voltage(x_zero, 'DCM', 0.0) == V_OUT_V
    assert model.node_voltage(x_pos, 'DEAD_TIME_POS', 0.0) == pytest.approx(-pp.v_f_v - 10.0 * pp.r_d_ohm)
