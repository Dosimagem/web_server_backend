from typing import Dict


PARAM_M = {
    'Y-90':   {'1 mm': 0.953, '2 mm': 1.304, '3 mm': 1.658},
    'P-32':   {'1 mm': 0.189, '2 mm': 0.275, '3 mm': 0.000},
    'Re-188': {'1 mm': 2.958, '2 mm': 4.468, '3 mm': 0.000},
    'Re-186': {'1 mm': 0.755, '2 mm': 0.000, '3 mm': 0.000},
    'Sm-153': {'1 mm': 1.956, '2 mm': 0.000, '3 mm': 0.000},
    'Lu-177': {'1 mm': 0.656, '2 mm': 0.000, '3 mm': 0.000},
}

PARAM_A = {
    'Y-90':   {'1 mm': 2.566, '2 mm': 3.825, '3 mm': 4.987},
    'P-32':   {'1 mm': 0.341, '2 mm': 0.539, '3 mm': 0.000},
    'Re-188': {'1 mm': 1.414, '2 mm': 3.059, '3 mm': 0.000},
    'Re-186': {'1 mm': 0.145, '2 mm': 0.000, '3 mm': 0.000},
    'Sm-153': {'1 mm': 6.120, '2 mm': 0.000, '3 mm': 0.000},
    'Lu-177': {'1 mm': 0.035, '2 mm': 0.000, '3 mm': 0.000},
}


def radiosysnoviorthesis(radionuclide: str, thickness: str, surface: float) -> Dict[float, float]:

    MBq = PARAM_M[radionuclide][thickness] * surface + PARAM_A[radionuclide][thickness]

    mCi = MBq / 37

    return {'MBq': round(MBq, 2), 'mCi': round(mCi, 2)}
