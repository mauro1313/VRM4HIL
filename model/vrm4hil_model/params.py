"""Load model/params.yaml and build the parameters of one phase.

    from vrm4hil_model.params import load_params, phase_params
    p  = load_params()                    # plain dict, same layout as the YAML
    ph = phase_params(p, 2, "M1")         # phase 2, with the M1 mismatches
"""

from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "params.yaml"


def load_params(path=DEFAULT_PATH) -> dict:
    """Read the YAML and check that every number was parsed as a number."""
    with open(path, encoding="utf-8") as f:
        p = yaml.safe_load(f)
    _check_numbers(p)
    return p


def _check_numbers(node, where=""):
    # PyYAML reads 150e-9 or 5.0e5 as strings: catch it here, not in a notebook
    if isinstance(node, dict):
        for key, value in node.items():
            _check_numbers(value, f"{where}.{key}" if where else key)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            _check_numbers(value, f"{where}[{i}]")
    elif isinstance(node, str):
        try:
            float(node)
        except ValueError:
            return
        raise ValueError(f"{where} = {node!r} read as a string: write it as 1.5e-7, 5.0e+5")


@dataclass(frozen=False)
class PhaseParams:
    """What one phase model needs. SI units."""
    v_in_v: float
    l_h: float
    dcr_ohm: float
    r_on_h_ohm: float
    r_on_l_ohm: float
    v_f_v: float
    r_d_ohm: float
    c_f: float
    esr_ohm: float
    f_sw_hz: float
    t_dr_s: float
    t_df_s: float
    pulse_extension_s: float = 0.0
    @property
    def t_sw_s(self):
        return 1.0 / self.f_sw_hz


def phase_params(p: dict, phase: int = 1, mismatch_set: str = "M0",
                 output_share: bool = False) -> PhaseParams:
    """Parameters of one phase (1..4, numbered as in the spec).

    The mismatch set overrides the nominal values it lists (table 3.3).
    output_share=True gives the phase 1/N of the output network (C/N, N*ESR),
    to be used with i_load = I_out/N.
    """
    ps = p["power_stage"]
    ms = p["mismatch_sets"][mismatch_set]
    n = ps["N_phases"]
    if not 1 <= phase <= n:
        raise ValueError(f"phase must be 1..{n}, got {phase}")
    k = phase - 1
    share = n if output_share else 1

    return PhaseParams(
        v_in_v=ps["Vin"]["nominal"],
        l_h=ms.get("L", [ps["L"]] * n)[k],
        dcr_ohm=ms.get("DCR", [ps["DCR"]] * n)[k],
        r_on_h_ohm=ps["Ron_H"],
        r_on_l_ohm=ps["Ron_L"],
        v_f_v=ps["body_diode"]["Vf"],
        r_d_ohm=ps["body_diode"]["Rd"],
        c_f=ps["C"] / share,
        esr_ohm=ps["ESR"] * share,
        f_sw_hz=ps["f_sw"],
        t_dr_s=ps["dead_time"]["t_dr"]["nominal"],
        t_df_s=ps["dead_time"]["t_df"]["nominal"],
        pulse_extension_s=ms.get("pulse_extension", [0.0] * n)[k],
    )