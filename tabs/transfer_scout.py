import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import data_processor as dp
import radar_factory as rf  
from config import COLORS, MUSTERMANN_ZONES

def calculate_per_90(df):
    """
    CSV'den gelen tüm ham verileri 90 dakika bazlı olacak şekilde onarır.
    MUSTERMANN_ZONES içindeki 17 metriğin tamamını kapsar.
    """
    if 'Mins' not in df.columns:
        return df
    
    df_copy = df.copy()
    # Dakika verisini güvenli sayıya çevir
    mins = pd.to_numeric(df_copy['Mins'], errors='coerce').fillna(0)
    
    # Otomatik hesaplanacak metriklerin eşleşme haritası (Ham Sütun -> /90 Hedefi)
    per_90_map = {
        'Goals/90': ['Goals', 'Gls', 'Gol'],
        'xG/90': ['xG'],
        'Shot/90': ['Shots', 'Shot', 'Şut'],
        'xA/90': ['xA'],
        'KP/90': ['Key Passes', 'KP', 'Kilit Pas'],
        'Drb/90': ['Dribbles', 'Drb', 'Dripling'],
        'Pr Passes/90': ['Progressive Passes', 'Pr Passes'],
        'Ps A/90': ['Passes Attempted', 'Ps A', 'Pas Denemesi'],
        'Poss Won/90': ['Possession Won', 'Poss Won', 'Top Kazanma'],
        'Poss Lost/90': ['Possession Lost', 'Poss Lost', 'Top Kaybı'],
        'Int/90': ['Interceptions', 'Int', 'Top Kesme'],
        'Clr/90': ['Clearances', 'Clr', 'Uzaklaştırma'],
        'Blk/90': ['Blocks', 'Blk', 'Blok'],
        'Tck A/90': ['Tackles Attempted', 'Tck A', 'Top Çalma Den.'],
        'Aer A/90': ['Aerial Attempted', 'Aer A', 'Hava Topu Den.'],
        'Goals Conceded/90': ['Goals Conceded', 'GC', 'Yenilen Gol'],
        'xG Prevented/90': ['xG Prevented', 'xGP', 'Önlenen xG']
    }

    for target, sources in per_90_map.items():
        # Eğer hedef sütun zaten varsa dokunma, yoksa ham veriden hesapla
        if target not in df_copy.columns:
            for src in sources:
                if src in df_copy.columns:
                    raw_val = pd.to_numeric(df_copy[src], errors='coerce').fillna(0)
                    df_copy[target] = np.where(mins > 0, (raw_val / mins) * 90.0, 0.0)
                    break
                    
    return df_copy

def get_league_multiplier(division_name):
    """Lig kalitesine göre çarpan belirler (config.py LEAGUE_MAP üzerinden)."""
    from config import LEAGUE_MAP
    div = str(division_name).lower()
    for tier, data in LEAGUE_MAP.items():
        if any(kw in div for kw in data['keywords']):
            return data['multiplier']
    return LEAGUE_MAP.get("Other/Unknown", {}).get("multiplier", 0.45)

def get_age_bonus(age):
    """Yaşa göre puan bonusu/cezası."""
    if age <= 19: return 20
    if age <= 21: return 15
    if age <= 24: return 8
    if age <= 28: return 0
    if age <= 31: return -10
    return -20 

def get_rec_bonus(rec_str):
    """Scout tavsiyesine göre puan bonusu."""
    rec = str(rec_str).upper()
    if 'A+' in rec: return 15
    if 'A' in rec: return 12
    if 'B+' in rec: return 7
    if 'C' in rec: return -5
    if any(x in rec for x in ['D', 'E', 'F']): return -15
    return 0

def get_metric_weight(metric_name, focus, role=""):
    """
    Taktiksel odağa göre metrik ağırlıklarını belirler.
    Gereksiz metrikleri (örneğin forvet için savunma) 0 çarpanıyla dışlar.
    """
    m_clean = str(metric_name).lower().strip().replace(" ", "").replace("/", "").replace("%", "").replace("-", "")
    is_off = any(k in m_clean for k in ['goal', 'xg', 'shot', 'xa', 'kp', 'drb', 'conv', 'finalthird'])
    is_def = any(k in m_clean for k in ['blk', 'clr', 'int', 'tck', 'aer', 'hdr', 'conceded', 'prevented', 'posswon'])
    
    if role == "Attackers":
        if "Ofansif" in focus: return 1.5 if is_off else (0.0 if is_def else 1.0)
        elif "Defansif" in focus: return 1.0 if is_off else (1.5 if is_def else 1.0)
        else: return 1.0 if is_off else (0.0 if is_def else 1.0)
            
    elif role == "Defenders":
        if "Defansif" in focus: return 1.5 if is_def else (0.0 if is_off else 1.0)
        elif "Ofansif" in focus: return 1.0 if is_def else (1.5 if is_off else 1.0)
        else: return 1.0 if is_def else (0.0 if is_off else 1.0)
            
    elif role == "Midfielders":
        if "Ofansif" in focus: return 1.5 if is_off else (0.5 if is_def else 1.0)
        elif "Defansif" in focus: return 0.5 if is_off else (1.5 if is_def else 1.0)
        else: return 1.0 
            
    return 1.0 

def calculate_mustermann_score(val, bounds, is_inverse):
    """Değeri Mustermann eşiklerine göre 1-5 seviyeye ve renge çevirir."""
    vp, p, a, g = bounds
    level = 1
    if not is_inverse:
        if val >= g: level = 5
        elif val >= a: level = 4
        elif val >= p: level = 3
        elif val >= vp: level = 2
    else:
        if val <= g: level = 5
        elif val <= a: level = 4
        elif val <= p: level = 3
        elif val <= vp: level = 2

    color_map = {
        5: 'rgba(0, 255, 136, 0.9)', 
        4: 'rgba(0, 212, 255, 0.9)', 
        3: 'rgba(255, 215, 0, 0.9)', 
        2: 'rgba(255, 140, 0, 0.9)', 
        1: 'rgba(255, 75, 75, 0.9)'  
    }
    return level, color_map[level]

def calculate_scout_grade(score):
    """Scout puanını harf notuna çevirir."""
    if score >= 90: return "S", "#FFD700" 
    if score >= 80: return "A+", "#00FF88"
    if score >= 75: return "A", "#00FF88"
    if score >= 70: return "B+", "#00D4FF"
    if score >= 65: return "B", "#00D4FF"
    if score >= 55: return "C", "#FFA500"
    if score >= 45: return "D", "#FF8C00"
    return "F", "#FF4B4B"

def get_short_name(m):
    """Tablo başlıkları için metrik isimlerini kısaltır."""
    mapping = {
        "Goals Conceded/90": "GC", "xG Prevented/90": "xGP", "Poss Won/90": "PW",
        "Ps A/90": "PsA", "Pr Passes/90": "PrP", "Poss Lost/90": "PL",
        "Blk/90": "BLK", "Clr/90": "CLR", "Int/90": "INT", "Tck A/90": "TkA",
        "Tck R": "TkR", "Aer A/90": "Aer", "Hdr %": "Hd%", "KP/90": "KP",
        "xA/90": "xA", "Drb/90": "DRB", "Shot/90": "SHT", "xG/90": "xG", "Goals/90": "GLS"
    }
    return mapping.get(m, m[:3].upper())

def render(df_team):
    st.title("🌐 Akıllı Transfer Merkezi (Data Scouting)")
    
    # Mevcut takım verisini onar
    df_team = calculate_per_90(df_team)
    
    transfer_file = st.file_uploader("Scout Raporunu Yükle (CSV)", type=["csv"], key="tr_hub")
    if not transfer_file:
        st.info("💡 Hedef oyuncuların istatistiklerini içeren CSV dosyasını yükleyin.")
        return

    # Tüm unique metrikleri topla (Yeni config yapısı üzerinden)
    ALL_METRICS = []
    for g in ["Goalkeepers", "Defenders", "Midfielders", "Attackers"]:
        for m in MUSTERMANN_ZONES.get(g, {}).keys():
            if m not in ALL_METRICS:
                ALL_METRICS.append(m)

    with st.spinner("Oyuncular 17 farklı kritere göre analiz ediliyor..."):
        df_scout = dp.process_fm_data(transfer_file, min_minutes=300)
        df_scout = calculate_per_90(df_scout)
        
        processed_data = []
        for idx, row in df_scout.iterrows():
            player_dict = row.to_dict()
            multiplier = get_league_multiplier(row.get('Division', ''))
            player_dict['Multiplier'] = multiplier
            
            group = dp.get_player_group(row.get('Position', ''))
            player_dict['Musti_Group'] = group
            musti_metrics_group = list(MUSTERMANN_ZONES.get(group, {}).keys())
            
            total_elite = 0
            total_stat_score = 0
            valid_metrics = 0
            style_dict = {}
            
            for m in ALL_METRICS:
                raw_val = dp.get_val(row, m)
                adj_val = raw_val * multiplier 
                player_dict[f"{m} (Adj)"] = round(adj_val, 2)
                
                # Yeni MUSTERMANN_ZONES uyumu
                bounds = MUSTERMANN_ZONES.get(group, {}).get(m)
                
                # BUG FIX: Eğer bu metrik oyuncunun grubuna ait değilse (bounds=None),
                # renklendirmeyi nötr bırak ve elite/skor hesabına KATMA.
                # [0,0,0,0] fallback'i kaldırdık çünkü val=0 ile val>=g(0) her zaman level=5 veriyordu.
                if not bounds:
                    style_dict[f"{m} (Adj)"] = "transparent"
                    continue  # Bu metriği atla, gruba ait değil
                    
                is_inverse = bounds[0] > bounds[3]
                level, hex_color = calculate_mustermann_score(adj_val, bounds, is_inverse)
                
                style_dict[f"{m} (Adj)"] = hex_color
                
                # Sadece gruba ait metriklerde elite say
                if level == 5:
                    total_elite += 1
                        
                if m in musti_metrics_group:
                    w = get_metric_weight(m, "Dengeli", group)
                    total_stat_score += (level / 5) * 100 * w
                    valid_metrics += w
                
            player_dict['Total_Elite_Count'] = total_elite
            base_score = (total_stat_score / valid_metrics) if valid_metrics > 0 else 0
            
            final_score = base_score + get_age_bonus(row.get('Age', 25)) + get_rec_bonus(row.get('Rec', 'C'))
            player_dict['Scout_Score'] = min(max(final_score, 0), 100) 
            player_dict['_style'] = style_dict 
            processed_data.append(player_dict)

        df_analyzed = pd.DataFrame(processed_data)

    st.success(f"✅ {len(df_analyzed)} oyuncu tam veri setiyle (17 Metrik) analiz edildi!")

    st.markdown("### 🔎 Kapsamlı Arama ve Filtreleme")
    
    view_mode = st.radio("📊 Tablo Görünümü:", 
                         ["Sadece Seçili Grubun İstatistikleri", "Tüm İstatistikleri Göster"], 
                         horizontal=True)
    show_all = "Tüm" in view_mode

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        f_group = st.selectbox("Pozisyon Grubu", ["Tümü", "Defenders", "Midfielders", "Attackers", "Goalkeepers"])
    with c2:
        f_elite = st.slider(f"Min. Elit Özellik", 0, 15, 0)
    with c3:
        f_score = st.slider("Min. Scout Puanı", 0, 100, 50)
    with c4:
        f_age = st.slider("Maksimum Yaş", 15, 40, 35)

    df_filtered = df_analyzed[
        (df_analyzed['Total_Elite_Count'] >= f_elite) &
        (df_analyzed['Scout_Score'] >= f_score) &
        (df_analyzed['Age'] <= f_age)
    ]
    if f_group != "Tümü":
        df_filtered = df_filtered[df_filtered['Musti_Group'] == f_group]

    # --- 1. ISI HARİTASI (HEATMAP) TABLOSU ---
    st.markdown("""
    <div style='display: flex; gap: 8px; margin-bottom: 15px; font-size: 11px; align-items: center; flex-wrap: wrap;'>
        <span style='color: #aaa;'><b>Renk Skalası:</b></span>
        <div style='padding: 3px 10px; background-color: rgba(0, 255, 136, 0.9); border-radius: 4px; color: black; font-weight: bold;'>Elit</div>
        <div style='padding: 3px 10px; background-color: rgba(0, 212, 255, 0.9); border-radius: 4px; color: black; font-weight: bold;'>İyi</div>
        <div style='padding: 3px 10px; background-color: rgba(255, 215, 0, 0.9); border-radius: 4px; color: black; font-weight: bold;'>Ortalama</div>
        <div style='padding: 3px 10px; background-color: rgba(255, 140, 0, 0.9); border-radius: 4px; color: white; font-weight: bold;'>Zayıf</div>
        <div style='padding: 3px 10px; background-color: rgba(255, 75, 75, 0.9); border-radius: 4px; color: white; font-weight: bold;'>Çok Zayıf</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not df_filtered.empty:
        metrics_to_show = ALL_METRICS if (show_all or f_group == "Tümü") else list(MUSTERMANN_ZONES.get(f_group, {}).keys())
        df_display = df_filtered.sort_values('Scout_Score', ascending=False)
        
        html = """
        <style>
        .scout-table { width: 100%; table-layout: fixed; border-collapse: collapse; font-family: sans-serif; font-size: 11px; color: #ddd; margin-bottom: 20px; }
        .scout-table th { background-color: #1e1e1e; padding: 6px 2px; border-bottom: 1px solid #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-align: center; font-size: 10px;}
        .scout-table td { padding: 0; border-bottom: 1px solid #333; border-right: 1px solid #222; text-align: center; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; height: 26px; }
        .scout-table .player-name { text-align: left; padding-left: 8px; font-weight: bold; border-right: none; width: 140px; }
        .scout-table .text-cell { padding: 4px 2px; border-right: none; width: 35px; }
        .scout-table tr:hover { background-color: #2a2a2a; }
        .stat-cell:hover { opacity: 0.7; }
        </style>
        <table class='scout-table'>
        """
        
        # Başlıklar
        html += "<thead><tr><th class='player-name'>Player</th><th class='text-cell'>Age</th><th class='text-cell'>Elit</th><th style='width: 45px;'>Puan</th>"
        for m in metrics_to_show:
            html += f"<th>{get_short_name(m)}</th>"
        html += "</tr></thead><tbody>"

        # Satırlar
        for _, row in df_display.iterrows():
            html += "<tr>"
            html += f"<td class='player-name'>{row['Player']}</td>"
            html += f"<td class='text-cell'>{row['Age']}</td>"
            html += f"<td class='text-cell'>{row['Total_Elite_Count']}</td>"
            html += f"<td class='text-cell' style='font-weight:bold; color: #00d4ff;'>{row['Scout_Score']:.1f}</td>"
            
            style_dict = row['_style']
            for m in metrics_to_show:
                col_name = f"{m} (Adj)"
                val = row.get(col_name, 0)
                bg_color = style_dict.get(col_name, "transparent")
                html += f"<td class='stat-cell' style='background-color: {bg_color}; cursor: help;' title='{m}: {val:.2f}'><div style='width: 100%; height: 100%;'></div></td>"
            html += "</tr>"
        
        html += "</tbody></table>"
        st.markdown(html, unsafe_allow_html=True)


        # --- 2. DERİN ANALİZ VE DİNAMİK PUANLAMA ---
        st.markdown("---")
        st.markdown("### 🎓 Oyuncu Değerlendirme & Takım İçi Projeksiyon")
        
        selected_player = st.selectbox("Detaylı Analiz Edilecek Oyuncuyu Seçin:", df_filtered['Player'].tolist())
        
        if selected_player:
            raw_row = df_scout[df_scout['Player'] == selected_player].iloc[0]
            multiplier = get_league_multiplier(raw_row.get('Division', ''))
            
            col_ctrl1, col_ctrl2 = st.columns(2)
            
            with col_ctrl1:
                default_role = dp.get_player_group(raw_row.get('Position', ''))
                roles = ["Goalkeepers", "Defenders", "Midfielders", "Attackers"]
                idx = roles.index(default_role) if default_role in roles else 2
                selected_role = st.selectbox("🔍 Oyuncu Rolünü Simüle Et:", roles, index=idx, key=f"role_{selected_player}")
                
            with col_ctrl2:
                focus = st.radio("⚖️ Taktiksel Odak (Skor Ağırlığı):", ["🛡️ Defansif", "⚖️ Dengeli", "⚔️ Ofansif"], index=1, horizontal=True)

            musti_metrics_role = list(MUSTERMANN_ZONES.get(selected_role, {}).keys())
            total_weighted_score = 0
            total_weight = 0
            role_elite_count = 0
            
            mock_player_row = raw_row.copy()
            mock_player_row['Player'] = f"{selected_player} (Proje)"
            
            for m in musti_metrics_role:
                val = dp.get_val(raw_row, m) * multiplier
                mock_player_row[m] = val  
                bounds = MUSTERMANN_ZONES.get(selected_role, {}).get(m, [0,0,0,0])
                is_inverse = bounds[0] > bounds[3] if bounds else False
                level, _ = calculate_mustermann_score(val, bounds, is_inverse)
                
                if level == 5: role_elite_count += 1
                
                w = get_metric_weight(m, focus, selected_role)
                total_weighted_score += (level / 5) * 100 * w
                total_weight += w
                
            base_score = (total_weighted_score / total_weight) if total_weight > 0 else 0
            final_score = min(max(base_score + get_age_bonus(raw_row.get('Age', 25)) + get_rec_bonus(raw_row.get('Rec', 'C')), 0), 100)
            grade, grade_color = calculate_scout_grade(final_score)

            st.markdown("<br>", unsafe_allow_html=True)
            col_grade, col_info = st.columns([1, 2])
            
            with col_grade:
                st.markdown(f"""
                <div style='text-align: center; background-color: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 2px solid {grade_color};'>
                    <h4 style='margin:0; color: #aaa;'>DİNAMİK NOT</h4>
                    <h1 style='font-size: 80px; margin: 0; color: {grade_color}; font-weight: 900; line-height: 1;'>{grade}</h1>
                    <h2 style='margin: 0; color: white;'>{final_score:.1f} <span style='font-size: 14px; color: #888;'>/ 100</span></h2>
                </div>
                """, unsafe_allow_html=True)
                
            with col_info:
                actual_pos = raw_row.get('Position', 'Bilinmiyor')
                st.markdown(f"#### 📋 {selected_role} Projeksiyon Özeti ({actual_pos})")
                st.write(f"- **Yaş:** {raw_row.get('Age')} | **Lig Çarpanı:** x{multiplier}")
                st.write(f"- **Elit Özellik Sayısı:** {role_elite_count} / {len(musti_metrics_role)}")
                st.info(f"💡 **Rol Optimizasyonu:** Bu oyuncu için {focus} odaklı {len(musti_metrics_role)} metrik analiz edildi. Role uygun olmayan veriler nottan dışlandı.")


            # --- 3. YENİ: MİNİMAL TAKTİKSEL OPERASYON MERKEZİ ---
            st.markdown("---")
            st.markdown("### 🎯 Taktiksel Operasyon Merkezi")
            st.caption("Filtrelenen oyuncuları grafiğe ekleyerek Taktiksel Roller üzerinden birbiriyle kıyaslayın.")

            # Sol taraf Radar, Sağ Taraf Havuz Listesi
            col_radar, col_list = st.columns([2.5, 1])

            with col_list:
                st.markdown("#### 📋 Scout Havuzu")
                st.info("Kıyaslamak için oyuncunun adına tıklayın.")

                RADAR_PALETTE = [COLORS.get('primary', '#00E5FF'), COLORS.get('secondary', '#FF3366'), '#00FFAA', '#FFB020', '#B020FF', '#FF4444']
                active_players = []

                for idx, row in df_filtered.iterrows():
                    p_name = row['Player']
                    state_key = f"to_active_{p_name}"

                    if state_key not in st.session_state:
                        st.session_state[state_key] = False

                    is_active = st.session_state[state_key]

                    assigned_color = RADAR_PALETTE[len(active_players) % len(RADAR_PALETTE)] if is_active else "#9CA3AF"
                    btn_type = "primary" if is_active else "secondary"

                    c_btn, c_ind = st.columns([5, 1])
                    with c_btn:
                        # Tıklanabilir buton ile seçim
                        if st.button(f"{p_name}", key=f"btn_{p_name}", use_container_width=True, type=btn_type):
                            st.session_state[state_key] = not is_active
                            st.rerun()

                    with c_ind:
                        if is_active:
                            # Neon renk belirteci
                            st.markdown(f"<div style='width: 14px; height: 14px; border-radius: 50%; background-color: {assigned_color}; margin-top: 12px; box-shadow: 0 0 8px {assigned_color};'></div>", unsafe_allow_html=True)

                    if is_active:
                        # Sadece aktif oyuncuda alt sekmeler açılır (Kompakt tasarım)
                        c_role, c_foc = st.columns(2)
                        
                        auto_g = dp.get_player_group(row.get('Position', ''))
                        group_opts = ["Goalkeepers", "Defenders", "Midfielders", "Attackers"]
                        if auto_g not in group_opts: auto_g = "Midfielders"
                        
                        sel_group = c_role.selectbox("Rol", group_opts, index=group_opts.index(auto_g), key=f"grp_{p_name}", label_visibility="collapsed")
                        
                        foci = ["🛡️ Defansif", "⚖️ Dengeli", "⚔️ Ofansif"]
                        sel_focus = c_foc.selectbox("Odak", foci, index=1, key=f"foc_{p_name}", label_visibility="collapsed")

                        active_players.append({
                            "name": p_name,
                            "data": row,
                            "group": sel_group,
                            "focus": sel_focus,
                            "color": assigned_color
                        })
                    st.markdown("<hr style='margin: 4px 0px; border-color: #1F2937;'>", unsafe_allow_html=True)

            with col_radar:
                if not active_players:
                    st.markdown(f"<div style='text-align:center; padding: 100px 0; color: #9CA3AF; border: 1px dashed #1F2937; border-radius: 10px;'>Radar grafiğini oluşturmak için sağdaki listeden oyuncu seçin.</div>", unsafe_allow_html=True)
                else:
                    fig = go.Figure()

                    base_group = active_players[0]['group']
                    metrics = list(MUSTERMANN_ZONES.get(base_group, {}).keys())

                    if not metrics:
                        st.warning(f"Seçilen {base_group} rolü için metrik bulunamadı.")
                    else:
                        for p in active_players:
                            p_vals = []
                            raw_vals = []
                            
                            multiplier = get_league_multiplier(p['data'].get('Division', ''))
                            
                            for m in metrics:
                                raw_val = dp.get_val(p['data'], m)
                                adj_val = raw_val * multiplier
                                raw_vals.append(adj_val)
                                
                                bounds = MUSTERMANN_ZONES.get(p['group'], {}).get(m, [0,0,0,0])
                                is_inverse = bounds[0] > bounds[3] if bounds else False
                                
                                b1, b2, b3, b4 = bounds
                                score = 50.0
                                epsilon = 1e-5 # Sıfıra bölünme koruması
                                if not is_inverse:
                                    if adj_val <= b1: score = max(0, (adj_val / (b1 if b1 else epsilon)) * 25)
                                    elif adj_val <= b2: score = 25 + ((adj_val - b1) / ((b2 - b1) if (b2 - b1) else epsilon)) * 25
                                    elif adj_val <= b3: score = 50 + ((adj_val - b2) / ((b3 - b2) if (b3 - b2) else epsilon)) * 25
                                    elif adj_val <= b4: score = 75 + ((adj_val - b3) / ((b4 - b3) if (b4 - b3) else epsilon)) * 20
                                    else: score = min(100, 95 + ((adj_val - b4) / (b4 if b4 else epsilon)) * 5)
                                else:
                                    if adj_val >= b1: score = max(0, 25 - ((adj_val - b1) / (b1 if b1 else epsilon)) * 25)
                                    elif adj_val >= b2: score = 25 + ((b1 - adj_val) / ((b1 - b2) if (b1 - b2) else epsilon)) * 25
                                    elif adj_val >= b3: score = 50 + ((b2 - adj_val) / ((b2 - b3) if (b2 - b3) else epsilon)) * 25
                                    elif adj_val >= b4: score = 75 + ((b3 - adj_val) / ((b3 - b4) if (b3 - b4) else epsilon)) * 20
                                    else: score = min(100, 95 + ((b4 - adj_val) / (b4 if b4 else epsilon)) * 5)
                                
                                p_vals.append(score)

                            hover_texts = []
                            for i, m in enumerate(metrics):
                                hover_texts.append(f"<b>{m}</b><br>Skor: {p_vals[i]:.1f}/100<br>Ham Veri: {raw_vals[i]:.2f}")
                            
                            color = p['color']
                            rgba_color = f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15)" if color.startswith('#') else color.replace(')', ', 0.15)').replace('rgb', 'rgba')
                            
                            fig.add_trace(go.Scatterpolar(
                                r=p_vals + [p_vals[0]],
                                theta=metrics + [metrics[0]],
                                mode='lines+markers',
                                fill='toself',
                                fillcolor=rgba_color,
                                line=dict(color=color, width=3),
                                marker=dict(size=8, color="#0A0E17", line=dict(color=color, width=2)),
                                name=f"{p['name']} ({p['group']})",
                                text=hover_texts + [hover_texts[0]],
                                hoverinfo="text"
                            ))

                        fig.update_layout(
                            template="plotly_dark",
                            title=dict(text=f"Rol Kıyaslaması: {base_group}", font=dict(color=COLORS.get('primary', '#00E5FF'), size=18), x=0.5, y=0.95),
                            polar=dict(
                                radialaxis=dict(visible=True, range=[0, 100], tickvals=[25, 50, 75, 100], ticktext=["Poor", "Average", "Good", "Elite"], tickfont=dict(color='#9CA3AF', size=9), gridcolor='#1F2937', showline=False),
                                angularaxis=dict(gridcolor='#1F2937', tickfont=dict(color='#F3F4F6', size=11, weight="bold")),
                                bgcolor='#0A0E17'
                            ),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(t=80, b=40, l=40, r=40),
                            legend=dict(orientation="h", y=-0.2, xanchor="center", x=0.5, font=dict(color='#F3F4F6', size=12)),
                            height=700
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)

        # --- 4. PERFORMANS - POTANSİYEL SCATTER MATRİXİ ---
        st.markdown("---")
        st.markdown("### 📈 Performans ve Potansiyel (Yaş) Matrixi")
        st.caption("Sağ üst köşe = Elit Performans + Genç Yaş.")
        
        df_analyzed['Status'] = np.where(df_analyzed['Player'].isin(df_filtered['Player']), 'Uygun Hedef', 'Filtre Dışı')
        
        fig_scatter = go.Figure()
        
        df_out = df_analyzed[df_analyzed['Status'] == 'Filtre Dışı']
        fig_scatter.add_trace(go.Scatter(
            x=df_out['Scout_Score'], y=df_out['Age'], 
            mode='markers', marker=dict(color='rgba(255,255,255,0.1)', size=8),
            text=df_out['Player'], name='Filtre Dışı'
        ))
        
        df_in = df_analyzed[df_analyzed['Status'] == 'Uygun Hedef']
        fig_scatter.add_trace(go.Scatter(
            x=df_in['Scout_Score'], y=df_in['Age'], 
            mode='markers', marker=dict(color=COLORS.get('primary', '#00d4ff'), size=13, line=dict(color='white', width=1)),
            text=df_in['Player'], name='Filtreden Geçenler'
        ))
        
        fig_scatter.update_layout(
            template="plotly_dark", 
            xaxis_title="Scout Puanı (Performans)", 
            yaxis_title="Yaş (Potansiyel)", 
            yaxis=dict(autorange="reversed"), 
            height=600
        )
        
        fig_scatter.add_vline(x=df_analyzed['Scout_Score'].median(), line_dash="dash", line_color="gray", opacity=0.5)
        fig_scatter.add_hline(y=df_analyzed['Age'].median(), line_dash="dash", line_color="gray", opacity=0.5)
        
        st.plotly_chart(fig_scatter, use_container_width=True)

    else:
        st.warning("⚠️ Filtrelerinize uygun oyuncu bulunamadı. Lütfen kriterleri esnetin.")
