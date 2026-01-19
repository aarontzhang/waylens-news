"""
Company data extracted from WayLens prospects PDF.
Each company has a name, category, search_term, priority_tier, and priority_weight.

Priority Tiers:
- Tier 1 (weight 100): Direct competitors - Samsara, Motive, Lytx, Netradyne, Geotab
- Tier 2 (weight 50): Major insurers, large fleet platforms, key customers
- Tier 3 (weight 20): Mid-size players, important partners
- Tier 4 (weight 5): Small resellers, niche players
"""

# Tier definitions for easy assignment
TIER_1_CRITICAL = {
    "Samsara", "Motive (KeepTruckin)", "Lytx", "Netradyne", "Geotab"
}

TIER_2_HIGH = {
    # Major insurers with fleet programs
    "Progressive Smart Haul", "Travelers (Northland)", "Liberty Mutual",
    "Zurich Insurance", "The Hartford", "Nationwide", "Great West Casualty",
    "Fairmatic", "Cover Whale", "Nirvana Insurance", "GEICO",
    # Major fleet platforms
    "Verizon Connect", "Platform Science", "Ford Pro Telematics",
    "Enterprise Fleet Management", "Ryder", "Penske",
    # Risk/Telematics leaders
    "CCC Intelligent Solutions", "SambaSafety", "Fleetio",
    # Major brokers
    "Aon", "Marsh", "Lockton", "HUB International",
    # Key current customers
    "GPS Trackit", "Gorilla Safety", "Orion Fleet Intelligence", "Konexial"
}

TIER_3_STANDARD = {
    # Mid-size insurers
    "Chubb", "AXA XL", "Crum & Forster", "Acuity Insurance", "Arch Insurance",
    "Protective Insurance", "Tokio Marine", "Hanover Insurance Group",
    "Philadelphia Insurance", "Sentry Insurance", "HDVI",
    # Mid-size fleet management
    "Azuga (Bridgestone)", "Shell Fleet Solutions", "WEX", "Holman", "Wheels Inc",
    "Transflo / ATI", "Rush Enterprises",
    # Key Geotab resellers
    "Element Fleet", "GPS Insight", "GoFleet", "Descartes", "GM Fleet",
    # Key brokers
    "Ryan Specialty", "Reliance Partners", "Alliant Insurance", "Acrisure (Wholesure)",
    # Risk tech
    "Milliman", "Roadzen (Kruzr)", "GreaterThan", "Predictive Coach",
    # Current customers
    "Moter (AIOI Mitsui)", "Traxero", "Acetech"
}

def get_priority(company_name: str) -> tuple[int, int]:
    """Get priority tier and weight for a company."""
    if company_name in TIER_1_CRITICAL:
        return 1, 100
    elif company_name in TIER_2_HIGH:
        return 2, 50
    elif company_name in TIER_3_STANDARD:
        return 3, 20
    else:
        return 4, 5


COMPANIES = [
    # Insurance Companies & MGAs
    {"name": "Travelers (Northland)", "category": "Insurance Companies & MGAs", "search_term": "Travelers Insurance Northland", "priority_tier": 2, "priority_weight": 50},
    {"name": "Progressive Smart Haul", "category": "Insurance Companies & MGAs", "search_term": "Progressive Smart Haul trucking", "priority_tier": 2, "priority_weight": 50},
    {"name": "Nirvana Insurance", "category": "Insurance Companies & MGAs", "search_term": "Nirvana Insurance trucking", "priority_tier": 2, "priority_weight": 50},
    {"name": "GMI Insurance", "category": "Insurance Companies & MGAs", "search_term": "GMI Insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Producers National", "category": "Insurance Companies & MGAs", "search_term": "Producers National Insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Protective Insurance", "category": "Insurance Companies & MGAs", "search_term": "Protective Insurance Progressive", "priority_tier": 3, "priority_weight": 20},
    {"name": "Fairmatic", "category": "Insurance Companies & MGAs", "search_term": "Fairmatic insurance fleet", "priority_tier": 2, "priority_weight": 50},
    {"name": "Great West Casualty", "category": "Insurance Companies & MGAs", "search_term": "Great West Casualty trucking", "priority_tier": 2, "priority_weight": 50},
    {"name": "Liberty Mutual", "category": "Insurance Companies & MGAs", "search_term": "Liberty Mutual commercial auto", "priority_tier": 2, "priority_weight": 50},
    {"name": "Zurich Insurance", "category": "Insurance Companies & MGAs", "search_term": "Zurich Insurance fleet", "priority_tier": 2, "priority_weight": 50},
    {"name": "Chubb", "category": "Insurance Companies & MGAs", "search_term": "Chubb insurance trucking", "priority_tier": 3, "priority_weight": 20},
    {"name": "AVIVA", "category": "Insurance Companies & MGAs", "search_term": "AVIVA insurance fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Westfield Insurance", "category": "Insurance Companies & MGAs", "search_term": "Westfield Insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "OOIDA Truck Insurance", "category": "Insurance Companies & MGAs", "search_term": "OOIDA truck insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Crum & Forster", "category": "Insurance Companies & MGAs", "search_term": "Crum Forster transportation", "priority_tier": 3, "priority_weight": 20},
    {"name": "DMC Insurance", "category": "Insurance Companies & MGAs", "search_term": "DMC Insurance trucking", "priority_tier": 4, "priority_weight": 5},
    {"name": "AXA XL", "category": "Insurance Companies & MGAs", "search_term": "AXA XL fleet insurance", "priority_tier": 3, "priority_weight": 20},
    {"name": "The Hartford", "category": "Insurance Companies & MGAs", "search_term": "Hartford insurance trucking", "priority_tier": 2, "priority_weight": 50},
    {"name": "Nationwide", "category": "Insurance Companies & MGAs", "search_term": "Nationwide commercial auto", "priority_tier": 2, "priority_weight": 50},
    {"name": "Flock Insurance", "category": "Insurance Companies & MGAs", "search_term": "Flock insurance telematics", "priority_tier": 4, "priority_weight": 5},
    {"name": "Intact Specialty", "category": "Insurance Companies & MGAs", "search_term": "Intact Specialty insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Arch Insurance", "category": "Insurance Companies & MGAs", "search_term": "Arch Insurance transportation", "priority_tier": 3, "priority_weight": 20},
    {"name": "Skyward Insurance", "category": "Insurance Companies & MGAs", "search_term": "Skyward Insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Northbridge Insurance", "category": "Insurance Companies & MGAs", "search_term": "Northbridge Insurance Canada", "priority_tier": 4, "priority_weight": 5},
    {"name": "Mapfre Insurance", "category": "Insurance Companies & MGAs", "search_term": "Mapfre insurance fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Acadia Insurance", "category": "Insurance Companies & MGAs", "search_term": "Acadia Insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Berkley", "category": "Insurance Companies & MGAs", "search_term": "W.R. Berkley insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Carolina Casualty", "category": "Insurance Companies & MGAs", "search_term": "Carolina Casualty Insurance trucking", "priority_tier": 4, "priority_weight": 5},
    {"name": "Berkley Prime Transportation", "category": "Insurance Companies & MGAs", "search_term": "Berkley Prime Transportation", "priority_tier": 4, "priority_weight": 5},
    {"name": "Gemini Transportation UW", "category": "Insurance Companies & MGAs", "search_term": "Gemini Transportation underwriting", "priority_tier": 4, "priority_weight": 5},
    {"name": "C3 Insurance", "category": "Insurance Companies & MGAs", "search_term": "C3 Insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Tokio Marine", "category": "Insurance Companies & MGAs", "search_term": "Tokio Marine insurance", "priority_tier": 3, "priority_weight": 20},
    {"name": "eTechnology Services", "category": "Insurance Companies & MGAs", "search_term": "eTechnology Services insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Hanover Insurance Group", "category": "Insurance Companies & MGAs", "search_term": "Hanover Insurance Group", "priority_tier": 3, "priority_weight": 20},
    {"name": "Philadelphia Insurance", "category": "Insurance Companies & MGAs", "search_term": "Philadelphia Insurance Companies", "priority_tier": 3, "priority_weight": 20},
    {"name": "Mitsui Sumitomo", "category": "Insurance Companies & MGAs", "search_term": "Mitsui Sumitomo Insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Trucking Proud Insurance", "category": "Insurance Companies & MGAs", "search_term": "Trucking Proud Insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Motor Transport Mutual RRG", "category": "Insurance Companies & MGAs", "search_term": "Motor Transport Mutual", "priority_tier": 4, "priority_weight": 5},
    {"name": "Acuity Insurance", "category": "Insurance Companies & MGAs", "search_term": "Acuity Insurance", "priority_tier": 3, "priority_weight": 20},
    {"name": "Quanata (State Farm)", "category": "Insurance Companies & MGAs", "search_term": "Quanata State Farm telematics", "priority_tier": 4, "priority_weight": 5},
    {"name": "Pouch Insurance", "category": "Insurance Companies & MGAs", "search_term": "Pouch Insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Sentry Insurance", "category": "Insurance Companies & MGAs", "search_term": "Sentry Insurance trucking", "priority_tier": 3, "priority_weight": 20},
    {"name": "Mobilatas", "category": "Insurance Companies & MGAs", "search_term": "Mobilatas insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Y-Risk (Hartford Rideshare)", "category": "Insurance Companies & MGAs", "search_term": "Y-Risk Hartford rideshare", "priority_tier": 4, "priority_weight": 5},
    {"name": "Grange Insurance", "category": "Insurance Companies & MGAs", "search_term": "Grange Insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "HDVI", "category": "Insurance Companies & MGAs", "search_term": "HDVI High Definition Vehicle Insurance", "priority_tier": 3, "priority_weight": 20},
    {"name": "Cover Whale", "category": "Insurance Companies & MGAs", "search_term": "Cover Whale trucking insurance", "priority_tier": 2, "priority_weight": 50},
    {"name": "Great American National Interstate", "category": "Insurance Companies & MGAs", "search_term": "Great American National Interstate Vanliner", "priority_tier": 4, "priority_weight": 5},
    {"name": "Lancer Insurance", "category": "Insurance Companies & MGAs", "search_term": "Lancer Insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Knightbrook (Novo Insurance)", "category": "Insurance Companies & MGAs", "search_term": "Knightbrook Novo Insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "eMAXX (Energi)", "category": "Insurance Companies & MGAs", "search_term": "eMAXX Energi insurance", "priority_tier": 4, "priority_weight": 5},

    # Brokers
    {"name": "Aon", "category": "Brokers", "search_term": "Aon insurance broker fleet", "priority_tier": 2, "priority_weight": 50},
    {"name": "Lockton", "category": "Brokers", "search_term": "Lockton insurance broker trucking", "priority_tier": 2, "priority_weight": 50},
    {"name": "HUB International", "category": "Brokers", "search_term": "HUB International insurance", "priority_tier": 2, "priority_weight": 50},
    {"name": "BFL Canada", "category": "Brokers", "search_term": "BFL Canada insurance broker", "priority_tier": 4, "priority_weight": 5},
    {"name": "Assurant", "category": "Brokers", "search_term": "Assurant insurance fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Reliance Partners", "category": "Brokers", "search_term": "Reliance Partners trucking insurance", "priority_tier": 3, "priority_weight": 20},
    {"name": "Alliant Insurance", "category": "Brokers", "search_term": "Alliant Insurance Services", "priority_tier": 3, "priority_weight": 20},
    {"name": "Futuristic UW", "category": "Brokers", "search_term": "Futuristic Underwriters", "priority_tier": 4, "priority_weight": 5},
    {"name": "Ryan Specialty", "category": "Brokers", "search_term": "Ryan Specialty Group", "priority_tier": 3, "priority_weight": 20},
    {"name": "McGriff Insurance", "category": "Brokers", "search_term": "McGriff Insurance Services", "priority_tier": 4, "priority_weight": 5},
    {"name": "Transportation Insurance Advisors", "category": "Brokers", "search_term": "Transportation Insurance Advisors", "priority_tier": 4, "priority_weight": 5},
    {"name": "Crest Insurance", "category": "Brokers", "search_term": "Crest Insurance Group", "priority_tier": 4, "priority_weight": 5},
    {"name": "Acrisure (Wholesure)", "category": "Brokers", "search_term": "Acrisure Wholesure", "priority_tier": 3, "priority_weight": 20},
    {"name": "Marsh", "category": "Brokers", "search_term": "Marsh McLennan insurance", "priority_tier": 2, "priority_weight": 50},
    {"name": "TrueNorth", "category": "Brokers", "search_term": "TrueNorth Companies insurance", "priority_tier": 4, "priority_weight": 5},
    {"name": "Cottingham & Butler", "category": "Brokers", "search_term": "Cottingham Butler insurance", "priority_tier": 4, "priority_weight": 5},

    # Risk Management Tech & Telematics
    {"name": "Tnedicca", "category": "Risk Management Tech & Telematics", "search_term": "Tnedicca fleet safety", "priority_tier": 4, "priority_weight": 5},
    {"name": "Milliman", "category": "Risk Management Tech & Telematics", "search_term": "Milliman insurance analytics", "priority_tier": 3, "priority_weight": 20},
    {"name": "Predictive Coach", "category": "Risk Management Tech & Telematics", "search_term": "Predictive Coach driver safety", "priority_tier": 3, "priority_weight": 20},
    {"name": "SambaSafety", "category": "Risk Management Tech & Telematics", "search_term": "SambaSafety driver risk", "priority_tier": 2, "priority_weight": 50},
    {"name": "GreaterThan", "category": "Risk Management Tech & Telematics", "search_term": "GreaterThan AI driving", "priority_tier": 3, "priority_weight": 20},
    {"name": "Roadzen (Kruzr)", "category": "Risk Management Tech & Telematics", "search_term": "Roadzen Kruzr insurance", "priority_tier": 3, "priority_weight": 20},
    {"name": "AGM Technologies", "category": "Risk Management Tech & Telematics", "search_term": "AGM Technologies fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Xtract", "category": "Risk Management Tech & Telematics", "search_term": "Xtract fleet intelligence", "priority_tier": 4, "priority_weight": 5},
    {"name": "Lightship Neuroscience", "category": "Risk Management Tech & Telematics", "search_term": "Lightship Neuroscience driver", "priority_tier": 4, "priority_weight": 5},
    {"name": "StreetScope", "category": "Risk Management Tech & Telematics", "search_term": "StreetScope fleet safety", "priority_tier": 4, "priority_weight": 5},
    {"name": "Tourmo.ai", "category": "Risk Management Tech & Telematics", "search_term": "Tourmo AI fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "RF Tracking", "category": "Risk Management Tech & Telematics", "search_term": "RF Tracking fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Cognizant", "category": "Risk Management Tech & Telematics", "search_term": "Cognizant insurance technology", "priority_tier": 4, "priority_weight": 5},
    {"name": "Fleetio", "category": "Risk Management Tech & Telematics", "search_term": "Fleetio fleet management", "priority_tier": 2, "priority_weight": 50},
    {"name": "CCC Intelligent Solutions", "category": "Risk Management Tech & Telematics", "search_term": "CCC Intelligent Solutions auto", "priority_tier": 2, "priority_weight": 50},

    # Fleet Management / TSPs
    {"name": "Navixy", "category": "Fleet Management", "search_term": "Navixy fleet tracking", "priority_tier": 4, "priority_weight": 5},
    {"name": "SquareGPS", "category": "Fleet Management", "search_term": "SquareGPS fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Transflo / ATI", "category": "Fleet Management", "search_term": "Transflo ATI trucking", "priority_tier": 3, "priority_weight": 20},
    {"name": "Barcoding Inc", "category": "Fleet Management", "search_term": "Barcoding Inc fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Rush Enterprises", "category": "Fleet Management", "search_term": "Rush Enterprises truck", "priority_tier": 3, "priority_weight": 20},
    {"name": "Enterprise Fleet Management", "category": "Fleet Management", "search_term": "Enterprise Fleet Management", "priority_tier": 2, "priority_weight": 50},
    {"name": "Wheels Inc", "category": "Fleet Management", "search_term": "Wheels Inc fleet", "priority_tier": 3, "priority_weight": 20},
    {"name": "Holman", "category": "Fleet Management", "search_term": "Holman fleet leasing", "priority_tier": 3, "priority_weight": 20},
    {"name": "Ryder", "category": "Fleet Management", "search_term": "Ryder fleet management", "priority_tier": 2, "priority_weight": 50},
    {"name": "Penske", "category": "Fleet Management", "search_term": "Penske truck leasing", "priority_tier": 2, "priority_weight": 50},
    {"name": "WEX", "category": "Fleet Management", "search_term": "WEX fleet fuel cards", "priority_tier": 3, "priority_weight": 20},
    {"name": "Northern Business Intelligence", "category": "Fleet Management", "search_term": "Northern Business Intelligence fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Gridline", "category": "Fleet Management", "search_term": "Gridline fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Utilimarc", "category": "Fleet Management", "search_term": "Utilimarc fleet analytics", "priority_tier": 4, "priority_weight": 5},
    {"name": "Attrix Technologies", "category": "Fleet Management", "search_term": "Attrix Technologies fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Bell Canada", "category": "Fleet Management", "search_term": "Bell Canada fleet IoT", "priority_tier": 4, "priority_weight": 5},
    {"name": "Rogers", "category": "Fleet Management", "search_term": "Rogers fleet management", "priority_tier": 4, "priority_weight": 5},
    {"name": "Vodafone Business", "category": "Fleet Management", "search_term": "Vodafone Business fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Zubie", "category": "Fleet Management", "search_term": "Zubie fleet tracking", "priority_tier": 4, "priority_weight": 5},
    {"name": "Azuga (Bridgestone)", "category": "Fleet Management", "search_term": "Azuga Bridgestone fleet", "priority_tier": 3, "priority_weight": 20},
    {"name": "Geoforce", "category": "Fleet Management", "search_term": "Geoforce asset tracking", "priority_tier": 4, "priority_weight": 5},
    {"name": "T-Mobile Fleet", "category": "Fleet Management", "search_term": "T-Mobile fleet IoT", "priority_tier": 4, "priority_weight": 5},
    {"name": "Telus", "category": "Fleet Management", "search_term": "Telus fleet management", "priority_tier": 4, "priority_weight": 5},
    {"name": "Shell Fleet Solutions", "category": "Fleet Management", "search_term": "Shell fleet solutions", "priority_tier": 3, "priority_weight": 20},
    {"name": "Fleet Hoster", "category": "Fleet Management", "search_term": "Fleet Hoster GPS", "priority_tier": 4, "priority_weight": 5},
    {"name": "Fleetistics", "category": "Fleet Management", "search_term": "Fleetistics GPS", "priority_tier": 4, "priority_weight": 5},
    {"name": "Fleet Wolf", "category": "Fleet Management", "search_term": "Fleet Wolf tracking", "priority_tier": 4, "priority_weight": 5},
    {"name": "LEVL Telematics", "category": "Fleet Management", "search_term": "LEVL Telematics fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Continumm", "category": "Fleet Management", "search_term": "Continumm fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Fleet Nav Systems", "category": "Fleet Management", "search_term": "Fleet Nav Systems", "priority_tier": 4, "priority_weight": 5},
    {"name": "Fleetster", "category": "Fleet Management", "search_term": "Fleetster fleet management", "priority_tier": 4, "priority_weight": 5},
    {"name": "Didcom", "category": "Fleet Management", "search_term": "Didcom fleet LATAM", "priority_tier": 4, "priority_weight": 5},
    {"name": "Traxxis GPS", "category": "Fleet Management", "search_term": "Traxxis GPS fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "FleetBoss", "category": "Fleet Management", "search_term": "FleetBoss GPS tracking", "priority_tier": 4, "priority_weight": 5},
    {"name": "Verizon Connect", "category": "Fleet Management", "search_term": "Verizon Connect fleet", "priority_tier": 2, "priority_weight": 50},
    {"name": "Platform Science", "category": "Fleet Management", "search_term": "Platform Science Trimble fleet", "priority_tier": 2, "priority_weight": 50},
    {"name": "Fleetup", "category": "Fleet Management", "search_term": "Fleetup fleet management", "priority_tier": 4, "priority_weight": 5},
    {"name": "Ford Pro Telematics", "category": "Fleet Management", "search_term": "Ford Pro Telematics fleet", "priority_tier": 2, "priority_weight": 50},

    # Geotab Resellers
    {"name": "Envue Telematics", "category": "Geotab Resellers", "search_term": "Envue Telematics", "priority_tier": 4, "priority_weight": 5},
    {"name": "Element Fleet", "category": "Geotab Resellers", "search_term": "Element Fleet Management", "priority_tier": 3, "priority_weight": 20},
    {"name": "BlueArrow Telematics", "category": "Geotab Resellers", "search_term": "BlueArrow Telematics", "priority_tier": 4, "priority_weight": 5},
    {"name": "Advantage One", "category": "Geotab Resellers", "search_term": "Advantage One GPS", "priority_tier": 4, "priority_weight": 5},
    {"name": "EJ Ward", "category": "Geotab Resellers", "search_term": "EJ Ward fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "CAN-AM Telematics", "category": "Geotab Resellers", "search_term": "CAN-AM Telematics", "priority_tier": 4, "priority_weight": 5},
    {"name": "Penske Truck Leasing", "category": "Geotab Resellers", "search_term": "Penske Truck Leasing telematics", "priority_tier": 4, "priority_weight": 5},
    {"name": "US Cellular Fleet", "category": "Geotab Resellers", "search_term": "US Cellular fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "FleetNet America (Cox)", "category": "Geotab Resellers", "search_term": "FleetNet America Cox Automotive", "priority_tier": 4, "priority_weight": 5},
    {"name": "High Point GPS", "category": "Geotab Resellers", "search_term": "High Point GPS", "priority_tier": 4, "priority_weight": 5},
    {"name": "Vehicare", "category": "Geotab Resellers", "search_term": "Vehicare fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "GM Fleet", "category": "Geotab Resellers", "search_term": "GM OnStar fleet", "priority_tier": 3, "priority_weight": 20},
    {"name": "Roadflex", "category": "Geotab Resellers", "search_term": "Roadflex fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Descartes", "category": "Geotab Resellers", "search_term": "Descartes Systems fleet", "priority_tier": 3, "priority_weight": 20},
    {"name": "GPS Insight", "category": "Geotab Resellers", "search_term": "GPS Insight fleet tracking", "priority_tier": 3, "priority_weight": 20},
    {"name": "AssetWorks", "category": "Geotab Resellers", "search_term": "AssetWorks fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Metrica Movil", "category": "Geotab Resellers", "search_term": "Metrica Movil fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Navisaf", "category": "Geotab Resellers", "search_term": "Navisaf fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "GPS Fleet Management Solutions", "category": "Geotab Resellers", "search_term": "GPS Fleet Management Solutions", "priority_tier": 4, "priority_weight": 5},
    {"name": "Argos Connected Solutions", "category": "Geotab Resellers", "search_term": "Argos Connected Solutions", "priority_tier": 4, "priority_weight": 5},
    {"name": "Jim Pattison Lease", "category": "Geotab Resellers", "search_term": "Jim Pattison Lease", "priority_tier": 4, "priority_weight": 5},
    {"name": "USA Fleet Solutions", "category": "Geotab Resellers", "search_term": "USA Fleet Solutions", "priority_tier": 4, "priority_weight": 5},
    {"name": "Mike Albert Fleet Solutions", "category": "Geotab Resellers", "search_term": "Mike Albert Fleet Solutions", "priority_tier": 4, "priority_weight": 5},
    {"name": "Geotrac", "category": "Geotab Resellers", "search_term": "Geotrac GPS", "priority_tier": 4, "priority_weight": 5},
    {"name": "GoFleet", "category": "Geotab Resellers", "search_term": "GoFleet GPS tracking", "priority_tier": 3, "priority_weight": 20},
    {"name": "Fleetworthy", "category": "Geotab Resellers", "search_term": "Fleetworthy Solutions", "priority_tier": 4, "priority_weight": 5},
    {"name": "Airiq", "category": "Geotab Resellers", "search_term": "Airiq telematics", "priority_tier": 4, "priority_weight": 5},

    # Competitors (Tier 1 - Critical)
    {"name": "Samsara", "category": "Competitors", "search_term": "Samsara fleet telematics", "priority_tier": 1, "priority_weight": 100},
    {"name": "Motive (KeepTruckin)", "category": "Competitors", "search_term": "Motive KeepTruckin fleet", "priority_tier": 1, "priority_weight": 100},
    {"name": "Lytx", "category": "Competitors", "search_term": "Lytx DriveCam fleet", "priority_tier": 1, "priority_weight": 100},
    {"name": "Netradyne", "category": "Competitors", "search_term": "Netradyne Driveri fleet camera", "priority_tier": 1, "priority_weight": 100},
    {"name": "Geotab", "category": "Competitors", "search_term": "Geotab telematics fleet", "priority_tier": 1, "priority_weight": 100},

    # Current Customers (important to monitor)
    {"name": "GEICO", "category": "Current Customers", "search_term": "GEICO auto insurance", "priority_tier": 2, "priority_weight": 50},
    {"name": "Moter (AIOI Mitsui)", "category": "Current Customers", "search_term": "Moter AIOI Mitsui Sumitomo", "priority_tier": 3, "priority_weight": 20},
    {"name": "GPS Trackit", "category": "Current Customers", "search_term": "GPS Trackit fleet", "priority_tier": 2, "priority_weight": 50},
    {"name": "Orion Fleet Intelligence", "category": "Current Customers", "search_term": "Orion Fleet Intelligence", "priority_tier": 2, "priority_weight": 50},
    {"name": "Acetech", "category": "Current Customers", "search_term": "Acetech fleet", "priority_tier": 3, "priority_weight": 20},
    {"name": "Traxero", "category": "Current Customers", "search_term": "Traxero fleet", "priority_tier": 3, "priority_weight": 20},
    {"name": "Gorilla Safety", "category": "Current Customers", "search_term": "Gorilla Safety fleet", "priority_tier": 2, "priority_weight": 50},
    {"name": "Prometheus", "category": "Current Customers", "search_term": "Prometheus fleet trucking", "priority_tier": 4, "priority_weight": 5},
    {"name": "RPM Global Connect", "category": "Current Customers", "search_term": "RPM Global Connect fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "Konexial", "category": "Current Customers", "search_term": "Konexial trucking", "priority_tier": 2, "priority_weight": 50},
    {"name": "Add On Systems", "category": "Current Customers", "search_term": "Add On Systems fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "eTrucks", "category": "Current Customers", "search_term": "eTrucks fleet management", "priority_tier": 4, "priority_weight": 5},
    {"name": "Prophecta", "category": "Current Customers", "search_term": "Prophecta fleet", "priority_tier": 4, "priority_weight": 5},
    {"name": "EZ Fleet Tracking", "category": "Current Customers", "search_term": "EZ Fleet Tracking GPS", "priority_tier": 4, "priority_weight": 5},
]


def seed_companies(db_module):
    """Seed all companies into the database."""
    count = 0
    for company in COMPANIES:
        result = db_module.add_company(
            name=company["name"],
            category=company["category"],
            search_term=company["search_term"],
            priority_tier=company.get("priority_tier", 4),
            priority_weight=company.get("priority_weight", 5)
        )
        if result:
            count += 1
    return count


def get_all_categories():
    """Get unique categories from companies list."""
    return list(set(c["category"] for c in COMPANIES))
