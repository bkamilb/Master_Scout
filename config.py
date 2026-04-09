# config.py

# --- 🎨 1. GÖRSEL KİMLİK VE KOZMETİK (PREMIUM DARK AESTHETIC) ---
COLORS = {
    'background': '#0A0E17',      # Çok koyu lacivert/siyah (Premium Dark)
    'panel_bg': '#121826',        # Kart ve panel arkaplanları
    'primary': '#00E5FF',         # Neon Cyan (Ana Vurgu - Kendi Oyuncumuz)
    'primary_glow': 'rgba(0, 229, 255, 0.15)',
    'secondary': '#FF3366',       # Neon Pembe/Kırmızı (Kıyaslama / Transfer)
    'secondary_glow': 'rgba(255, 51, 102, 0.15)',
    'peers': 'rgba(255, 255, 255, 0.2)', # Arkadaki silüet rakipler
    'text_main': '#F3F4F6',
    'text_muted': '#9CA3AF',
    'grid_lines': '#1F2937',
    
    # Mustermann Zonları İçin Mutlak Renkler
    'zone_elite': 'rgba(0, 255, 136, 0.12)',   # Zümrüt Yeşili
    'zone_good': 'rgba(0, 229, 255, 0.08)',    # Cyan
    'zone_average': 'rgba(255, 204, 0, 0.05)', # Sarı
    'zone_poor': 'rgba(255, 51, 102, 0.05)'    # Kırmızı
}

# Uygulamanın her yerine modern görünüm katacak CSS enjeksiyonu
CUSTOM_CSS = f"""
<style>
    .stApp {{ background-color: {COLORS['background']}; color: {COLORS['text_main']}; font-family: 'Inter', sans-serif; }}
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    .metric-card {{ background: {COLORS['panel_bg']}; border-radius: 12px; padding: 20px; border: 1px solid {COLORS['grid_lines']}; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; background-color: transparent; }}
    .stTabs [data-baseweb="tab"] {{ color: {COLORS['text_muted']}; font-weight: 600; padding-bottom: 10px; border-radius: 0; }}
    .stTabs [aria-selected="true"] {{ color: {COLORS['primary']} !important; border-bottom: 3px solid {COLORS['primary']} !important; background-color: transparent !important; }}
</style>
"""

# --- ⚽ 2. LİG ÇARPANLARI (LEAGUE WEIGHTS) ---
LEAGUE_MAP = {
    "Tier 1 (Elite)": {"keywords": ["premier division", "premier league", "bundesliga", "la liga", "serie a", "champions league"], "multiplier": 1.0},
    "Tier 2 (High)": {"keywords": ["ligue 1", "eredivisie", "liga portugal", "sky bet championship", "europa league"], "multiplier": 0.90},
    "Tier 3 (Competitive)": {"keywords": ["turkish super lig", "süper lig", "belgian pro league", "brazilian national first"], "multiplier": 0.82},
    "Tier 4 (Developing)": {"keywords": ["austrian bundesliga", "scottish premiership", "greek super league", "swiss super league"], "multiplier": 0.72},
    "Tier 5 (Lower/Emerging)": {"keywords": ["allsvenskan", "eliteserien", "superliga", "ekstraklasa", "mls", "saudi pro"], "multiplier": 0.60},
    "Other/Unknown": {"keywords": [], "multiplier": 0.45}
}

# --- ⚖️ 3. TERS METRİK MANTIĞI (INVERSE METRICS) ---
# True olanlar: Düşük değerin daha iyi olduğu metriklerdir (Örn: Yenilen Gol).
METRIC_PROPS = {
    "Goals Conceded/90": True,
    "Poss Lost/90": True,
    "xG Prevented/90": False,
    "Poss Won/90": False,
    "Ps A/90": False,
    "Pr passes/90": False,
    "Goals/90": False,
    "xG/90": False,
    "Shot/90": False,
    "Conversion %": False,
    "Drb/90": False,
    "Dist/90": False,
    "Blk/90": False,
    "Clr/90": False,
    "Int/90": False,
    "Tck A/90": False,
    "Tck R": False,
    "Hdrs W/90": False,
    "Aer A/90": False,
    "Hdr %": False,
    "Asts/90": False,
    "xA/90": False,
    "KP/90": False,
    "OP-KP/90": False,
    "Pas %": False
}

# --- 🎯 4. MUTLAK MUSTERMANN BARAJLARI (ABSOLUTE BOUNDS) ---
# Düzen: [Kötü, Ortalama, İyi, Elit]
# Ters metriklerde (True) değerler BÜYÜKTEN KÜÇÜĞE dizilir, çünkü küçük elittir!
MUSTERMANN_ZONES = {
    "Goalkeepers": {
        "Goals Conceded/90": [1.57, 1.45, 1.31, 1.20],
        "xG Prevented/90": [-0.16, -0.12, -0.07, -0.02],
        "Poss Won/90": [7.25, 7.62, 8.17, 8.53],
        "Ps A/90": [21.58, 23.26, 24.38, 26.06],
        "Pr Passes/90": [0.37, 0.58, 0.74, 0.98],
        "Poss Lost/90": [8.21, 6.04, 3.67, 2.35]
    },
    "Defenders": {
        "Blk/90": [0.62, 0.56, 0.68, 0.75],
        "Clr/90": [0.90, 1.03, 1.13, 1.28],
        "Int/90": [2.38, 2.65, 2.88, 3.12],
        "Tck A/90": [0.87, 1.07, 2.25, 3.48],
        "Tck R": [72.4, 74.7, 76.7, 79.0],
        "Aer A/90": [3.15, 3.82, 4.57, 5.35],
        "Hdr %": [52.4, 60.8, 65.6, 70.7],
        "Poss Won/90": [8.33, 9.09, 9.77, 10.54],
        "Ps A/90": [50.96, 56.45, 62.33, 69.88],
        "KP/90": [0.20, 0.29, 0.77, 1.39],
        "xA/90": [0.02, 0.03, 0.06, 0.13],
        "Pr Passes/90": [3.19, 4.44, 6.18, 7.95],
        "Poss Lost/90": [12.01, 8.18, 4.90, 4.05],
        "Drb/90": [0.04, 0.08, 0.55, 1.75],
        "Shot/90": [0.25, 0.34, 0.48, 0.68],
        "xG/90": [0.01, 0.02, 0.03, 0.04],
        "Goals/90": [0.01, 0.02, 0.03, 0.05]
    },
    "Midfielders": {
        "Blk/90": [0.27, 0.40, 0.51, 0.61],
        "Clr/90": [0.49, 0.70, 0.84, 1.01],
        "Int/90": [1.96, 2.32, 2.52, 2.86],
        "Tck A/90": [1.49, 1.98, 2.34, 2.72],
        "Tck R": [67.3, 69.8, 72.4, 74.7],
        "Aer A/90": [1.67, 2.16, 2.64, 3.45],
        "Hdr %": [27.0, 36.1, 44.8, 54.4],
        "Poss Won/90": [5.63, 6.92, 7.82, 8.53],
        "Ps A/90": [48.62, 54.66, 60.74, 68.83],
        "KP/90": [0.87, 1.20, 1.60, 2.08],
        "xA/90": [0.06, 0.09, 0.13, 0.19],
        "Pr Passes/90": [3.69, 5.02, 5.82, 6.91],
        "Poss Lost/90": [10.21, 8.44, 7.15, 6.04],
        "Drb/90": [0.22, 0.37, 0.72, 1.56],
        "Shot/90": [0.88, 1.17, 1.57, 2.02],
        "xG/90": [0.04, 0.06, 0.11, 0.22],
        "Goals/90": [0.04, 0.07, 0.11, 0.23]
    },
    "Attackers": {
        "Blk/90": [0.10, 0.16, 0.24, 0.32],
        "Clr/90": [0.17, 0.31, 0.49, 0.64],
        "Int/90": [0.90, 1.37, 1.97, 2.34],
        "Tck A/90": [0.48, 1.24, 2.34, 2.94],
        "Tck R": [65.3, 70.7, 74.0, 76.6],
        "Aer A/90": [2.92, 3.60, 4.94, 6.86],
        "Hdr %": [19.5, 26.9, 33.5, 40.3],
        "Poss Won/90": [2.47, 4.16, 6.52, 7.52],
        "Ps A/90": [28.63, 35.10, 43.27, 50.29],
        "KP/90": [1.18, 1.53, 1.95, 2.31],
        "xA/90": [0.12, 0.16, 0.21, 0.26],
        "Pr Passes/90": [0.98, 2.10, 3.55, 4.75],
        "Poss Lost/90": [14.95, 12.36, 8.53, 6.12],
        "Drb/90": [0.84, 1.63, 3.43, 5.62],
        "Shot/90": [1.96, 2.22, 2.47, 2.81],
        "xG/90": [0.21, 0.26, 0.32, 0.40],
        "Goals/90": [0.22, 0.29, 0.37, 0.47]
    }
}

# --- 🧠 5. OYUNCU RADAR GRUPLARI (FACETS) ---
# --- 🧠 5. OYUNCU RADAR GRUPLARI (FACETS) ---
# Gerçek IP (In-Possession) ve OOP (Out-of-Possession) ayrımı
PLAYER_FACETS = {
    "Goalkeepers": {
        "Shot Stopping & Sweeping (OOP)": {"metrics": ["Goals Conceded/90", "xG Prevented/90", "Poss Won/90"], "mode": "performance"},
        "Distribution (IP)": {"metrics": ["Ps A/90", "Pr Passes/90", "Poss Lost/90"], "mode": "performance"}
    },
    "Defenders": {
        "Build-up & Support (IP)": {"metrics": ["Ps A/90", "Pr Passes/90", "KP/90", "xA/90", "Drb/90", "Poss Lost/90"], "mode": "performance"},
        "Defending (OOP)": {"metrics": ["Tck A/90", "Int/90", "Blk/90", "Clr/90", "Poss Won/90", "Aer A/90"], "mode": "performance"}
    },
    "Midfielders": {
        "Creating & Carrying (IP)": {"metrics": ["Ps A/90", "Pr Passes/90", "KP/90", "xA/90", "Drb/90", "Poss Lost/90"], "mode": "performance"},
        "Screening & Winning (OOP)": {"metrics": ["Tck A/90", "Int/90", "Poss Won/90", "Blk/90", "Clr/90", "Aer A/90"], "mode": "performance"}
    },
    "Attackers": {
        "Attacking Threat (IP)": {"metrics": ["Goals/90", "xG/90", "Shot/90", "Drb/90", "KP/90", "xA/90"], "mode": "performance"},
        "Pressing & Work Rate (OOP)": {"metrics": ["Poss Won/90", "Tck A/90", "Int/90", "Blk/90", "Clr/90", "Aer A/90"], "mode": "performance"}
    }
}

# --- 🧬 6. FM26 ROL VE ANAHTAR NİTELİKLER (DNA & SCOUTING) ---
RADAR_PARAMS = ['Passing', 'Technique', 'Dribbling', 'Vision', 'Decisions', 'Anticipation', 'Pace', 'Stamina']
ATTR_MAPPING = {
    "Wor": "Work Rate", "Vis": "Vision", "Tec": "Technique", "Tck": "Tackling",
    "Sta": "Stamina", "Str": "Strength", "Pos": "Positioning", "Pas": "Passing",
    "OtB": "Off The Ball", "Mar": "Marking", "Fin": "Finishing", "Dec": "Decisions",
    "Cmp": "Composure", "Ant": "Anticipation", "Acc": "Acceleration", "Pac": "Pace",
    "Jump": "Jumping Reach", "Cnt": "Concentration"
}

FM26_ROLES = {
    "Kaleciler": {
        "Goalkeeper (IP)": ["Handling", "Aerial Reach", "Command Of Area", "Communication", "Positioning", "Reflexes", "Agility", "Concentration"],
        "Ball-Playing GK (IP)": ["Handling", "Aerial Reach", "Command Of Area", "Communication", "Kicking", "Positioning", "Reflexes", "Agility", "Roaming", "Expressive"],
        "No-Nonsense GK (IP)": ["Handling", "Aerial Reach", "Command Of Area", "Communication", "Positioning", "Reflexes", "Agility", "Concentration"],
        "Goalkeeper (OOP)": ["Handling", "Aerial Reach", "Command Of Area", "Communication", "Positioning", "Reflexes", "Agility", "Concentration"],
        "Sweeper Keeper (OOP)": ["Handling", "Aerial Reach", "Command Of Area", "Communication", "Anticipation", "Decisions", "One On Ones", "Reflexes"],
        "Line-Holding Keeper (OOP)": ["Handling", "Aerial Reach", "Command Of Area", "Communication", "Positioning", "Reflexes", "Agility", "Concentration"]
    },
    "Stoperler": {
        "Centre-Back (IP)": ["Heading", "Marking", "Tackling", "Anticipation", "Positioning", "Strength", "Jumping Reach"],
        "Advanced CB (IP)": ["Heading", "Marking", "Passing", "Tackling", "Anticipation", "Decisions", "Positioning", "Technique", "Expressive"],
        "Ball-Playing CB (IP)": ["Heading", "Marking", "Passing", "Tackling", "Anticipation", "Positioning", "Strength", "Jumping Reach", "Expressive"],
        "No-Nonsense CB (IP)": ["Heading", "Marking", "Tackling", "Anticipation", "Positioning", "Strength", "Jumping Reach"],
        "Centre-Back (OOP)": ["Heading", "Marking", "Tackling", "Anticipation", "Positioning", "Strength", "Jumping Reach"],
        "Stopping CB (OOP)": ["Heading", "Marking", "Tackling", "Anticipation", "Positioning", "Strength", "Jumping Reach", "Bravery"],
        "Covering CB (OOP)": ["Heading", "Marking", "Tackling", "Anticipation", "Decisions", "Positioning", "Strength", "Pace"],
        "Wide Centre-Back (IP)": ["Heading", "Marking", "Tackling", "Anticipation", "Positioning", "Strength", "Jumping Reach"],
        "Overlapping CB (IP)": ["Crossing", "Heading", "Marking", "Tackling", "Anticipation", "Work Rate", "Strength", "Stamina"],
        "Stopping Wide CB (OOP)": ["Heading", "Marking", "Tackling", "Anticipation", "Positioning", "Strength", "Jumping Reach", "Bravery"],
        "Covering Wide CB (OOP)": ["Heading", "Marking", "Tackling", "Anticipation", "Decisions", "Positioning", "Strength", "Pace"]
    },
    "Bekler ve Kanat Bekler": {
        "Full-Back (IP)": ["Passing", "Tackling", "Anticipation", "Positioning", "Teamwork", "Work Rate", "Acceleration", "Stamina"],
        "Attacking Full-Back (IP)": ["Crossing", "Passing", "Tackling", "Anticipation", "Positioning", "Work Rate", "Acceleration", "Stamina"],
        "No-Nonsense Full-Back (IP)": ["Heading", "Marking", "Tackling", "Anticipation", "Positioning", "Strength", "Jumping Reach"],
        "Inverted Full-Back (IP)": ["Heading", "Marking", "Tackling", "Anticipation", "Positioning", "Strength", "Jumping Reach"],
        "False Full-Back (IP)": ["Passing", "Tackling", "Anticipation", "Decisions", "Positioning", "Teamwork", "Work Rate", "Technique"],
        "Wing-Back (IP)": ["Crossing", "Dribbling", "Passing", "Tackling", "Anticipation", "Work Rate", "Acceleration", "Stamina"],
        "Inverted Wing-Back (IP)": ["Passing", "Tackling", "Anticipation", "Decisions", "Positioning", "Teamwork", "Work Rate", "Technique"],
        "Advanced Wing-Back (IP)": ["Crossing", "Dribbling", "Passing", "Technique", "Work Rate", "Acceleration", "Agility", "Stamina"],
        "Complete Wing-Back (IP)": ["Crossing", "Dribbling", "Passing", "Tackling", "Technique", "Work Rate", "Acceleration", "Stamina"],
        "Pressing FB (OOP)": ["Marking", "Tackling", "Anticipation", "Positioning", "Teamwork", "Work Rate", "Acceleration", "Aggression"],
        "Holding FB (OOP)": ["Marking", "Tackling", "Anticipation", "Decisions", "Positioning", "Acceleration", "Concentration"]
    },
    "Orta Sahalar": {
        "Attacking Mid (IP)": ["Long Shots", "Off The Ball", "Passing", "First Touch", "Technique", "Flair", "Composure"],
        "Channel Mid (IP)": ["Crossing", "Off The Ball", "Passing", "First Touch", "Technique", "Work Rate", "Acceleration", "Composure"],
        "Midfield Playmaker (IP)": ["Off The Ball", "Passing", "Vision", "Decisions", "First Touch", "Technique", "Teamwork", "Composure"],
        "Pressing CM (OOP)": ["Tackling", "Anticipation", "Decisions", "Teamwork", "Work Rate", "Stamina", "Aggression"],
        "Screening CM (OOP)": ["Marking", "Tackling", "Decisions", "Positioning", "Concentration"],
        "Wide Covering CM (OOP)": ["Marking", "Tackling", "Decisions", "Teamwork", "Work Rate", "Stamina", "Agility"],
        "Defensive Mid (IP)": ["Tackling", "Anticipation", "Positioning", "Teamwork", "Concentration"],
        "Deep-Lying Playmaker (IP)": ["Passing", "Vision", "Decisions", "First Touch", "Technique", "Teamwork", "Composure"],
        "Box-to-Box Mid (IP)": ["Off The Ball", "Passing", "Tackling", "Teamwork", "Work Rate", "Stamina"],
        "Box-to-Box Playmaker (IP)": ["Off The Ball", "Passing", "Vision", "Decisions", "First Touch", "Technique", "Teamwork", "Work Rate"],
        "Half-Back (IP)": ["Heading", "Marking", "Tackling", "Anticipation", "Positioning", "Teamwork", "Strength", "Jumping Reach"],
        "Dropping DM (IP)": ["Marking", "Tackling", "Anticipation", "Decisions", "Positioning", "Teamwork", "Work Rate", "Strength"],
        "Screening DM (IP)": ["Marking", "Tackling", "Anticipation", "Decisions", "Positioning", "Concentration"],
        "Wide Covering DM (IP)": ["Marking", "Tackling", "Anticipation", "Decisions", "Positioning", "Teamwork", "Work Rate", "Stamina"],
        "Attacking Mid (OOP)": ["Anticipation", "Decisions", "Work Rate"],
        "Central Mid (OOP)": ["Tackling", "Decisions", "Teamwork", "Work Rate"],
        "Defensive Mid (OOP)": ["Tackling", "Anticipation", "Decisions", "Positioning", "Teamwork", "Work Rate"]
    },
    "Kanatlar": {
        "Winger (IP)": ["Crossing", "Dribbling", "Technique", "Teamwork", "Acceleration", "Pace", "Agility"],
        "Inside Forward (IP)": ["Dribbling", "Off The Ball", "Anticipation", "First Touch", "Technique", "Acceleration", "Agility", "Composure"],
        "Playmaking Winger (IP)": ["Crossing", "Dribbling", "Off The Ball", "Passing", "Vision", "Decisions", "First Touch", "Technique", "Expressive"],
        "Wide Forward (IP)": ["Dribbling", "Off The Ball", "Anticipation", "First Touch", "Technique", "Acceleration", "Pace", "Agility"],
        "Inside Winger (IP)": ["Dribbling", "First Touch", "Technique", "Teamwork", "Acceleration", "Agility", "Composure"],
        "Wide Midfielder (IP)": ["Crossing", "Passing", "Decisions", "Technique", "Teamwork", "Work Rate", "Stamina", "Pace"],
        "Winger / WM (OOP)": ["Anticipation", "Decisions", "Teamwork", "Work Rate", "Acceleration"],
        "Tracking Winger / WM (OOP)": ["Anticipation", "Decisions", "Teamwork", "Work Rate", "Acceleration", "Stamina", "Aggression"],
        "Inside Outlet Winger (OOP)": ["Off The Ball", "Anticipation", "Decisions", "Teamwork", "Balance", "Concentration"],
        "Wide Outlet Winger / WM (OOP)": ["Off The Ball", "Anticipation", "Decisions", "Teamwork", "Pace", "Concentration"]
    },
    "Forvetler": {
        "Deep-Lying Forward (IP)": ["Finishing", "Off The Ball", "First Touch", "Technique", "Strength", "Composure"],
        "Central Forward (IP)": ["Finishing", "Heading", "Off The Ball", "First Touch", "Technique", "Acceleration", "Strength", "Composure"],
        "Target Forward (IP)": ["Finishing", "Heading", "Off The Ball", "Strength", "Jumping Reach", "Balance", "Bravery", "Aggression"],
        "Poacher (IP)": ["Finishing", "Heading", "Off The Ball", "Anticipation", "Acceleration", "Composure", "Concentration"],
        "Channel Forward (IP)": ["Dribbling", "Finishing", "Off The Ball", "First Touch", "Technique", "Work Rate", "Acceleration", "Composure"],
        "False Nine (IP)": ["Dribbling", "Off The Ball", "Passing", "Vision", "Decisions", "First Touch", "Technique", "Teamwork"],
        "Central Forward (OOP)": ["Anticipation", "Decisions", "Work Rate"],
        "Tracker CF (OOP)": ["Anticipation", "Decisions", "Teamwork", "Work Rate", "Stamina", "Aggression"],
        "Central Outlet CF (OOP)": ["Off The Ball", "Anticipation", "Decisions", "Teamwork", "Balance", "Concentration"]
    }
}

# --- 📊 7. SCATTER PLOT AYARLARI ---
SCATTER_PLOTS = {
    "🎯 Bitiricilik ve Fırsatçılık": {"x": "xG/90", "y": "Goals/90", "size": "Shot/90", "desc": "Sağ Üst: Klinik bitiriciler."},
    "🪄 Yaratıcılık": {"x": "xA/90", "y": "KP/90", "size": "Ps A/90", "desc": "Sağ Üst: Ana yaratıcılar."},
    "🚧 Defansif Yoğunluk": {"x": "Tck A/90", "y": "Int/90", "size": "Hdr %", "desc": "Sağ Üst: Her yerde olan savunmacılar."},
    "🚂 Top Taşıma": {"x": "Pr passes/90", "y": "Drb/90", "size": "Pas %", "desc": "Sağ Üst: Modern dikine oyuncular."}
}