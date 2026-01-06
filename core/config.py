# core/config.py

CONFIGS = ["Concept 0", "Concept 1", "Concept 2", "Concept 3", "Concept 4"]

QUANT_KPIS = [
    "CAPEX", "OPEX", "Volume_Occupation",
    "Boil_off", "Specific_Heat_Capacity", "Load_Bearing"
]

QUAL_KPIS = [
    "Resistance_to_Thermal_Deformations",
    "Adaptability_to_Tank_Shapes",
    "Fire_Resistance",
    "Air_Condensation_Avoidance",
    "Health_Risk_for_Workers",
    "Commercial_Uptake",
    "FMECA_Score"
]

ALL_KPIS = ["LCA"] + QUANT_KPIS + QUAL_KPIS

KPI_LABELS = {
    # --- Aggregate ---
    "LCA": "Life Cycle Assessment",

    # --- Quantitative ---
    "CAPEX": "CapEx",
    "OPEX": "OpEx",
    "Volume_Occupation": "Volume occupation",
    "Boil_off": "Boil-off rate",
    "Specific_Heat_Capacity": "Specific heat capacity",
    "Load_Bearing": "Load bearing capacity",

    # --- Qualitative ---
    "Resistance_to_Thermal_Deformations": "Resistance to thermal deformations",
    "Adaptability_to_Tank_Shapes": "Adaptability to tank shapes",
    "Fire_Resistance": "Fire resistance",
    "Air_Condensation_Avoidance": "Air condensation avoidance",
    "Health_Risk_for_Workers": "Health risk for workers",
    "Commercial_Uptake": "Commercial uptake",
    "FMECA_Score": "FMECA score",
}


LCA_CATEGORIES = [
    "Climate change (GWP100)", "Ozone depletion (ODP)",
    "Human toxicity_cancer", "Human toxicity_non-cancer",
    "Particulate matter", "Ionizing radiation_human health",
    "Photochemical ozone formation, human health", "Acidification",
    "Eutrophication_terrestrial", "Eutrophication_freshwater",
    "Eutrophication_marine", "Ecotoxicity_freshwater",
    "Land use", "Water use",
    "Resource use_minerals and metals", "Resource use_fossils"
]