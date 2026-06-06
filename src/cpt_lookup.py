# Key: SNOMED code (as string, matches Synthea output)
# Value: CPT code
SNOMED_TO_CPT = {
    # ── CONFIRMED FROM AUTHORITATIVE SOURCES ──────────────────────────────
    "73761001":  "45378",   # Colonoscopy [HEDIS/CMS confirmed]
    "52734007":  "27130",   # Total hip replacement [CMS confirmed]
    "609588000": "27447",   # Total knee replacement [CMS/AMA confirmed]
    "22523008":  "55250",   # Vasectomy [AAPC confirmed]
    "287664005": "58600",   # Bilateral tubal ligation [AAPC confirmed]
    "65200003":  "58300",   # IUD insertion [Medicaid fee schedule confirmed]
    "68254000":  "58301",   # IUD removal [Medicaid fee schedule confirmed]
    # ── CLINICALLY MAPPED (standard coding knowledge) ─────────────────────
    "399208008": "71046",   # Chest X-ray, 2 views
    "127783003": "94010",   # Spirometry
    "23426006":  "94010",   # Measurement of respiratory function (same as spirometry)
    "173160006": "31622",   # Diagnostic bronchoscopy
    "91602002":  "32554",   # Thoracentesis
    "312681000": "77080",   # Bone density scan (DEXA)
    "80146002":  "44970",   # Appendectomy (laparoscopic)
    "43075005":  "44140",   # Partial colectomy
    "76164006":  "45380",   # Colonoscopy with biopsy
    "274031008": "45315",   # Rectal polypectomy
    "232717009": "33533",   # Coronary artery bypass (arterial)
    "415070008": "92928",   # Percutaneous coronary intervention (PCI)
    "447365002": "33249",   # Biventricular ICD insertion
    "18286008":  "93654",   # Catheter ablation of heart tissue
    "88039007":  "32851",   # Lung transplant
    "429609002": "32491",   # Lung volume reduction surgery
    "432231006": "32400",   # Fine needle aspiration biopsy of lung
    "698354004": "70553",   # MRI brain with contrast
    "418891003": "74178",   # CT chest and abdomen
    "387685009": "23655",   # Manipulation of shoulder joint
    "699253003": "27570",   # Manipulation of knee joint
    "274474001": "29125",   # Bone immobilization/splinting
    "288086009": "12001",   # Suture open wound (simple repair)
    "76601001":  "96372",   # Intramuscular injection
    "313191000": "96372",   # Injection of adrenaline (same billing code)
    "384700001": "90714",   # Tetanus injection
    "180256009": "95117",   # Subcutaneous immunotherapy
    "395142003": "95004",   # Allergy skin testing
    "90407005":  "90791",   # Psychiatric diagnostic evaluation
    "88848003":  "90792",   # Psychiatric follow-up (with medical services)
    "228557008": "90837",   # Cognitive behavioral therapy (60 min)
    "15081005":  "94625",   # Pulmonary rehabilitation (physician supervised)
    "169553002": "11981",   # Subcutaneous contraceptive insertion (Nexplanon)
    "301807007": "11982",   # Subcutaneous contraceptive removal
    "755621000000101": "11983",  # Subcutaneous contraceptive replacement
    "46706006":  "58301",   # IUD replacement — bill removal; insertion billed separately
    "112790001": "31231",   # Nasal sinus endoscopy
    "117015009": "87880",   # Throat culture (rapid strep)
    "167995008": "87210",   # Sputum microscopy (wet mount)
    "269911007": "87210",   # Sputum examination (same)
    "1015401000000102": "82270",  # Fecal occult blood test
    "252160004": "81025",   # Urine pregnancy test
    "387607004": "44320",   # Colostomy construction
    "433112001": "37187",   # Percutaneous mechanical thrombectomy
    "445912000": "59120",   # Ectopic pregnancy excision + fallopian tube
    "714812005": "59841",   # Induced termination of pregnancy (surgical, >13 wks)
    "66348005":  "59400",   # Vaginal delivery (global)
    "11466000":  "59510",   # Cesarean section (global)
    "65588006":  "59400",   # Premature birth — billed as vaginal delivery
    "177157003": "59409",   # Spontaneous breech delivery (vaginal delivery only)
    "236974004": "59409",   # Instrumental delivery (forceps/vacuum)
    "85548006":  "59300",   # Episiotomy (when billed separately)
    "31208007":  "59409",   # Medical induction of labor — billed under delivery code
    "237001001": "59409",   # Augmentation of labor — same
    "18946005":  "62322",   # Epidural anesthesia (lumbar, w/o imaging guidance)
    "13995008":  "24900",   # Amputation, arm through humerus
    "46028000":  "25900",   # Amputation at wrist
    "79733001":  "27590",   # Amputation, thigh
    "180030006": "28800",   # Amputation, midfoot
    "703423002": "77427",   # Radiation tx management (chemo+radiation — use rad mgmt code)
}
FALLBACK_CPT = "99213"  # established patient office visit — safe generic fallback

def get_cpt(snomed_code):
    return SNOMED_TO_CPT.get(str(snomed_code), FALLBACK_CPT)