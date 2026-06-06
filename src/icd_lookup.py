# Key: SNOMED code (as string, matches Synthea output)
# Value: ICD-10 code
SNOMED_TO_ICD10 = {
    # ── CONFIRMED FROM AUTHORITATIVE SOURCES ──────────────────────────────
    "79586000":  "O00.10",  # Tubal pregnancy [AAPC + icd10data confirmed]
    "72892002":  "Z34.90",  # Normal pregnancy, unspecified trimester [icd10data confirmed]
    "68496003":  "K63.5",   # Polyp of colon [AAPC + icd10data confirmed]
    "10509002":  "J20.9",   # Acute bronchitis, unspecified [multiple sources confirmed]
    "713197008": "K62.1",   # Recurrent rectal polyp [AAPC confirmed]

    # ── CLINICALLY MAPPED (standard ICD-10 coding knowledge) ──────────────
    "1734006":   "S14.109A", # Vertebral fracture w/ spinal cord injury, initial encounter
    "16114001":  "S82.90XA", # Fracture of ankle, unspecified, initial encounter
    "30832001":  "S76.112A", # Rupture of patellar tendon, initial encounter
    "33737001":  "S22.39XA", # Fracture of rib, initial encounter
    "43878008":  "J02.0",    # Streptococcal pharyngitis
    "58150001":  "S42.009A", # Fracture of clavicle, unspecified, initial encounter
    "65966004":  "S52.90XA", # Fracture of forearm, unspecified, initial encounter
    "74400008":  "K37",      # Appendicitis, unspecified
    "86849004":  "T39.1X2A", # Deliberate self-poisoning (poisoning, intentional self-harm)
    "87433001":  "J43.9",    # Pulmonary emphysema, unspecified
    "93761005":  "C18.9",    # Primary malignant neoplasm of colon, unspecified
    "94260004":  "C78.5",    # Secondary malignant neoplasm of large intestine/rectum
    "109838007": "C18.8",    # Overlapping malignant neoplasm of colon
    "162573006": "R91.8",    # Suspected lung cancer (abnormal finding on lung imaging)
    "185086009": "J44.1",    # COPD with acute exacerbation
    "192127007": "F90.9",    # ADHD, unspecified type
    "195662009": "J02.9",    # Acute pharyngitis, unspecified (viral)
    "195967001": "J45.909",  # Asthma, unspecified, uncomplicated
    "233678006": "J45.909",  # Childhood asthma — same billing code
    "262574004": "S21.009A", # Bullet wound (open wound of thorax, unspecified)
    "263102004": "S62.009A", # Fracture subluxation of wrist, initial encounter
    "283371005": "S51.819A", # Laceration of forearm, initial encounter
    "283385000": "S71.119A", # Laceration of thigh, initial encounter
    "284549007": "S61.419A", # Laceration of hand, initial encounter
    "284551006": "S91.319A", # Laceration of foot, initial encounter
    "287182007": "T71.122A", # Attempted suicide by suffocation, initial encounter
    "287193009": "X74.01XA", # Suicide by firearm discharge, initial encounter
    "307731004": "S46.019A", # Injury of rotator cuff tendon, initial encounter
    "359817006": "S72.009A", # Closed fracture of hip, unspecified, initial encounter
    "363406005": "C18.9",    # Malignant tumor of colon (same as primary malignant)
    "370247008": "S01.419A", # Facial laceration, initial encounter
    "403192003": "T23.309A", # Third degree burn, unspecified, initial encounter
    "422968005": "C34.10",   # Non-small cell lung cancer, stage 3
    "423121009": "C34.10",   # Non-small cell lung cancer, stage 4 — use C34.10 + staging
    "424132000": "C34.10",   # Non-small cell lung cancer, stage 1
    "425048006": "C34.10",   # Non-small cell lung cancer, stage 2
    "444448004": "S83.419A", # Injury of medial collateral ligament of knee, initial
    "444470001": "S83.509A", # Injury of anterior cruciate ligament, initial encounter
    "67811000119102": "C34.11", # Small cell lung cancer, stage 1
    "67821000119109": "C34.11", # Small cell lung cancer, stage 2
    "67831000119107": "C34.11", # Small cell lung cancer, stage 3
    "67841000119103": "C34.11", # Small cell lung cancer, stage 4
    "368581000119106": "E11.40", # Diabetic neuropathy, type 2, unspecified
}

FALLBACK_ICD10 = "Z00.00"  # general adult medical exam

def get_icd10(snomed_code):
    return SNOMED_TO_ICD10.get(str(snomed_code), FALLBACK_ICD10)