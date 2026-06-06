PRIOR_AUTH_RULES = {
    ("74177", "medi_cal_managed_care"):   True,
    ("74177", "commercial_ppo"):          True,
    ("72148", "medi_cal_managed_care"):   True,
    ("72148", "medicare_advantage"):      True,
    ("27447", "medi_cal_managed_care"):   True,
    ("93654", "commercial_ppo"):          True,
    ("99213", "medi_cal_managed_care"):   False,
    ("45378", "commercial_ppo"):          False,
    ("96413", "medi_cal_managed_care"):  True,   # chemo infusion
    ("96413", "commercial_ppo"):         True,
    ("96413", "medicare_advantage"):     True,
    ("71250", "medi_cal_managed_care"):  True,   # CT chest
    ("71250", "commercial_ppo"):         True,
    ("70553", "medi_cal_managed_care"):  True,   # MRI brain
    ("33533", "medi_cal_managed_care"):  True,   # coronary bypass
    ("27130", "medi_cal_managed_care"):  True,   # total hip replacement
    ("27447", "commercial_ppo"):         True,   # total knee replacement
    ("27447", "medicare_advantage"):     True,
}

def auth_required(cpt_code, payer_id):
    return PRIOR_AUTH_RULES.get((cpt_code, payer_id), False)