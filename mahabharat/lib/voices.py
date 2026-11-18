"""Voice cast for Tinku ki Mahabharat.
Each entry: (kokoro Hindi voice, speed, F0 factor, formant factor). Lines are reshaped with WORLD
(pitch + voice character, speed unchanged), recorded in one breath, inner pauses tightened to ~0.14 s.
Hindi voices available: hm_omega, hm_psi (male), hf_alpha, hf_beta (female).
Keep every character distinct from the others who share a scene. Name colours are for caption tags."""

VOICE_CAST = {
    # host
    "tinku":        ("hf_beta",  1.00, 1.65, 1.15),   # cute young boy
    # elders & kings
    "shantanu":     ("hm_omega", 0.90, 0.90, 0.96),   # regal, warm
    "bheeshm":      ("hm_omega", 0.88, 0.82, 0.93),   # deep, steady, wise
    "dhritarashtra":("hm_omega", 0.88, 0.86, 0.92),   # heavy, troubled
    "pandu":        ("hm_psi",   0.92, 0.95, 0.98),
    "vidura":       ("hm_psi",   0.90, 0.90, 0.97),   # calm, thoughtful
    "vyasa":        ("hm_omega", 0.85, 0.78, 0.92),   # very old sage
    "drona":        ("hm_psi",   0.90, 0.85, 0.95),   # strict teacher
    "kripa":        ("hm_omega", 0.92, 0.95, 0.97),
    "sanjaya":      ("hm_psi",   0.98, 1.00, 1.00),
    # heroes
    "krishna":      ("hm_psi",   0.95, 1.08, 1.04),   # gentle, smiling, kind
    "yudhishthir":  ("hm_omega", 0.92, 0.97, 0.98),   # calm, truthful
    "bheem":        ("hm_omega", 0.95, 0.80, 0.90),   # big, booming, jolly
    "arjun":        ("hm_psi",   0.95, 1.00, 1.00),   # confident, clear
    "nakul":        ("hm_psi",   1.00, 1.12, 1.05),
    "sahadev":      ("hm_psi",   0.98, 1.18, 1.06),
    "abhimanyu":    ("hm_psi",   1.02, 1.28, 1.09),   # brave teenager
    "karn":         ("hm_omega", 0.92, 0.88, 0.97),   # proud, generous
    "duryodhan":    ("hm_omega", 0.95, 0.93, 0.95),   # proud, jealous
    "dushasan":     ("hm_psi",   1.00, 0.92, 0.96),
    "shakuni":      ("hm_psi",   0.92, 0.96, 1.10),   # sly, nasal
    "ashwatthama":  ("hm_psi",   0.98, 1.05, 1.02),
    "ekalavya":     ("hm_psi",   0.98, 1.15, 1.06),
    # queens & women
    "ganga":        ("hf_alpha", 0.95, 1.00, 1.00),   # gentle goddess
    "satyavati":    ("hf_beta",  0.95, 1.00, 1.00),
    "kunti":        ("hf_beta",  0.92, 0.92, 0.97),   # loving mother
    "gandhari":     ("hf_alpha", 0.92, 0.90, 0.96),   # dignified
    "madri":        ("hf_beta",  0.95, 1.06, 1.02),
    "draupadi":     ("hf_alpha", 0.95, 1.08, 1.04),   # bright, strong
    "amba":         ("hf_beta",  0.95, 1.10, 1.03),
    "hidimba":      ("hf_alpha", 0.98, 0.95, 0.98),
    # narrator-ish / crowds
    "yaksha":       ("hm_omega", 0.88, 0.75, 0.90),   # mysterious, echoing (add more reverb)
}

NAME_COLORS = {
    "tinku": "#f08a00", "shantanu": "#1d8a8a", "ganga": "#2f8fd8", "bheeshm": "#6b7a99", "krishna": "#2f6fd8",
    "arjun": "#c0392b", "bheem": "#7a3fbf", "yudhishthir": "#b58900", "karn": "#e04a1f", "duryodhan": "#2c8f5a",
    "draupadi": "#d81b60", "shakuni": "#4b2a6e", "abhimanyu": "#2f7bff", "nakul": "#14a3a3", "sahadev": "#3fae4a",
}


# Tinku & Friends (kids series). English topics use the *_en voices, Hindi topics the *_hi voices.
# Blended voices ('a*0.5+b*0.5') work in sing.py; for spoken TTS build the style with voice_style() the same way.
# Targets (median F0): Tinku ~285 Hz, Pinky ~300–315 Hz, Golu ~340–370 Hz. Moti barks are synthesized SFX.
FRIENDS_VOICES = {
    "tinku_en": ("af_heart*0.5+am_michael*0.5", 0.86, 1.55, 1.20),   # owner's pick (blend of two Kokoro styles; sing.py voice_style())
    "pinky_en": ("af_bella", 0.86, 1.48, 1.12),
    "golu_en":  ("af_heart", 0.84, 1.70, 1.20),
    "tinku_hi": ("hf_beta", 0.95, 1.65, 1.15),
    "pinky_hi": ("hf_alpha", 0.95, 1.45, 1.12),   # measure F0 and adjust to target on first Hindi episode
    "golu_hi":  ("hf_beta", 0.92, 1.95, 1.22),
}
