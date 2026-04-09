# tabs/player_profile.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import data_processor as dp
from config import MUSTERMANN_ZONES, COLORS

# --- YARDIMCI FONKSİYONLAR (Tablo Skoru ve Ağırlıklar İçin) ---
def calculate_mustermann_score(val, bounds, is_inverse):
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

def get_metric_weight(metric_name, focus, role=""):
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

def get_age_bonus(age):
    if age <= 19: return 20
    if age <= 21: return 15
    if age <= 24: return 8
    if age <= 28: return 0
    if age <= 31: return -10
    return -20 

def get_short_name(m):
    mapping = {
        "Goals Conceded/90": "GC", "xG Prevented/90": "xGP", "Poss Won/90": "PW",
        "Ps A/90": "PsA", "Pr Passes/90": "PrP", "Poss Lost/90": "PL",
        "Blk/90": "BLK", "Clr/90": "CLR", "Int/90": "INT", "Tck A/90": "TkA",
        "Tck R": "TkR", "Aer A/90": "Aer", "Hdr %": "Hd%", "KP/90": "KP",
        "xA/90": "xA", "Drb/90": "DRB", "Shot/90": "SHT", "xG/90": "xG", "Goals/90": "GLS"
    }
    return mapping.get(m, m[:3].upper())

# --- ANA RENDER FONKSİYONU ---
def render(df, players):
    # 1. Takımı Kaleciden Forvete Doğru Sıralama İşlemi
    sort_map = {"Goalkeepers": 1, "Defenders": 2, "Midfielders": 3, "Attackers": 4}
    df_temp = df.copy()
    df_temp['Temp_Group'] = df_temp['Position'].apply(dp.get_player_group)
    df_temp['Sort_Order'] = df_temp['Temp_Group'].map(sort_map).fillna(5)
    df_sorted = df_temp.sort_values(by=['Sort_Order', 'Player']).reset_index(drop=True)

    st.markdown("### 👤 Kapsamlı Oyuncu Profili ve Kıyaslama")
    st.caption("Takımınızdaki oyuncuları seçerek roller üzerinden kıyaslayın ve detaylı ısı haritalarını inceleyin.")
    st.markdown("---")

    # Sol Sütun (İnce Liste), Sağ Sütun (Geniş Analiz)
    col_list, col_content = st.columns([1, 2.8])

    active_players = []

    with col_list:
        st.markdown("#### 📋 Takım Kadrosu")
        st.info("Kıyaslamak için isimlere tıklayın.")
        
        RADAR_PALETTE = [COLORS.get('primary', '#00E5FF'), COLORS.get('secondary', '#FF3366'), '#00FFAA', '#FFB020', '#B020FF', '#FF4444']

        for idx, row in df_sorted.iterrows():
            p_name = row['Player']
            state_key = f"prof_active_{p_name}"
            
            if state_key not in st.session_state:
                st.session_state[state_key] = False
                
            is_active = st.session_state[state_key]
            assigned_color = RADAR_PALETTE[len(active_players) % len(RADAR_PALETTE)] if is_active else "#9CA3AF"
            btn_type = "primary" if is_active else "secondary"
            
            c_btn, c_ind = st.columns([5, 1])
            with c_btn:
                if st.button(f"{p_name}", key=f"pbtn_{p_name}", use_container_width=True, type=btn_type):
                    st.session_state[state_key] = not is_active
                    st.rerun()
            with c_ind:
                if is_active:
                    st.markdown(f"<div style='width: 14px; height: 14px; border-radius: 50%; background-color: {assigned_color}; margin-top: 12px; box-shadow: 0 0 8px {assigned_color};'></div>", unsafe_allow_html=True)
            
            if is_active:
                c_role, c_foc = st.columns(2)
                auto_g = row['Temp_Group']
                group_opts = ["Goalkeepers", "Defenders", "Midfielders", "Attackers"]
                sel_group = c_role.selectbox("Rol", group_opts, index=group_opts.index(auto_g), key=f"pgrp_{p_name}", label_visibility="collapsed")
                
                foci = ["🛡️ Defansif", "⚖️ Dengeli", "⚔️ Ofansif"]
                sel_focus = c_foc.selectbox("Odak", foci, index=1, key=f"pfoc_{p_name}", label_visibility="collapsed")
                
                active_players.append({
                    "name": p_name,
                    "data": row,
                    "group": sel_group,
                    "focus": sel_focus,
                    "color": assigned_color
                })
            st.markdown("<hr style='margin: 4px 0px; border-color: #1F2937;'>", unsafe_allow_html=True)

    with col_content:
        if not active_players:
            st.markdown(f"<div style='text-align:center; padding: 100px 0; color: #9CA3AF; border: 1px dashed #1F2937; border-radius: 10px;'>Profilini ve radarını görmek istediğiniz oyuncuları sol taraftan seçin.</div>", unsafe_allow_html=True)
        else:
            # Temel analiz çerçevesi ilk seçilen oyuncunun rolüne göre belirlenir
            base_group = active_players[0]['group']
            metrics = list(MUSTERMANN_ZONES.get(base_group, {}).keys())

            # --- 1. DİNAMİK RADAR CHART ---
            if not metrics:
                st.warning(f"Seçilen {base_group} rolü için metrik bulunamadı.")
            else:
                fig = go.Figure()
                processed_table_data = [] 

                for p in active_players:
                    p_vals = []
                    raw_vals = []
                    
                    row_data = p['data']
                    total_elite = 0
                    total_stat_score = 0
                    valid_metrics = 0
                    style_dict = {}

                    for m in metrics:
                        # Kendi takımımız olduğu için lig çarpanına gerek yok
                        raw_val = float(dp.get_val(row_data, m)) 
                        raw_vals.append(raw_val)
                        
                        bounds = MUSTERMANN_ZONES.get(p['group'], {}).get(m, [0,0,0,0])
                        is_inverse = bounds[0] > bounds[3] if bounds else False
                        
                        # Radar için interpolasyon puanı (0-100)
                        b1, b2, b3, b4 = bounds
                        score = 50.0
                        epsilon = 1e-5
                        if not is_inverse:
                            if raw_val <= b1: score = max(0, (raw_val / (b1 if b1 else epsilon)) * 25)
                            elif raw_val <= b2: score = 25 + ((raw_val - b1) / ((b2 - b1) if (b2 - b1) else epsilon)) * 25
                            elif raw_val <= b3: score = 50 + ((raw_val - b2) / ((b3 - b2) if (b3 - b2) else epsilon)) * 25
                            elif raw_val <= b4: score = 75 + ((raw_val - b3) / ((b4 - b3) if (b4 - b3) else epsilon)) * 20
                            else: score = min(100, 95 + ((raw_val - b4) / (b4 if b4 else epsilon)) * 5)
                        else:
                            if raw_val >= b1: score = max(0, 25 - ((raw_val - b1) / (b1 if b1 else epsilon)) * 25)
                            elif raw_val >= b2: score = 25 + ((b1 - raw_val) / ((b1 - b2) if (b1 - b2) else epsilon)) * 25
                            elif raw_val >= b3: score = 50 + ((b2 - raw_val) / ((b2 - b3) if (b2 - b3) else epsilon)) * 25
                            elif raw_val >= b4: score = 75 + ((b3 - raw_val) / ((b3 - b4) if (b3 - b4) else epsilon)) * 20
                            else: score = min(100, 95 + ((b4 - raw_val) / (b4 if b4 else epsilon)) * 5)
                        
                        p_vals.append(score)

                        # Tablo için Mustermann Skoru (1-5 Renk Skalası)
                        level, hex_color = calculate_mustermann_score(raw_val, bounds, is_inverse)
                        style_dict[m] = hex_color
                        if level == 5: total_elite += 1
                        
                        w = get_metric_weight(m, p['focus'], p['group'])
                        total_stat_score += (level / 5) * 100 * w
                        valid_metrics += w

                    # Radar Çizimleri
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

                    # Oyuncu Analiz Puanını Hesapla (Table için)
                    base_score = (total_stat_score / valid_metrics) if valid_metrics > 0 else 0
                    final_score = min(max(base_score + get_age_bonus(row_data.get('Age', 25)), 0), 100)

                    # Tablo Satırı Olarak Ekle
                    processed_table_data.append({
                        "Player": p['name'],
                        "Age": row_data.get('Age', '-'),
                        "Total_Elite_Count": total_elite,
                        "Scout_Score": final_score,
                        "raw_data": dict(zip(metrics, raw_vals)),
                        "_style": style_dict
                    })

                fig.update_layout(
                    template="plotly_dark",
                    title=dict(text=f"Rol Performansı: {base_group}", font=dict(color=COLORS.get('primary', '#00E5FF'), size=18), x=0.5, y=0.95),
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], tickvals=[25, 50, 75, 100], ticktext=["Poor", "Average", "Good", "Elite"], tickfont=dict(color='#9CA3AF', size=9), gridcolor='#1F2937', showline=False),
                        angularaxis=dict(gridcolor='#1F2937', tickfont=dict(color='#F3F4F6', size=11, weight="bold")),
                        bgcolor='#0A0E17'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=80, b=40, l=40, r=40),
                    legend=dict(orientation="h", y=-0.2, xanchor="center", x=0.5, font=dict(color='#F3F4F6', size=12)),
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)

            # --- 2. HEATMAP (ISI HARİTASI) TABLOSU ---
            st.markdown("### 📊 Detaylı Performans Tablosu")
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

            if processed_table_data:
                # Puanı en yüksek olanı en üste al
                processed_table_data.sort(key=lambda x: x['Scout_Score'], reverse=True)

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
                
                # Tablo Başlıkları
                html += "<thead><tr><th class='player-name'>Player</th><th class='text-cell'>Age</th><th class='text-cell'>Elit</th><th style='width: 45px;'>Puan</th>"
                for m in metrics:
                    html += f"<th>{get_short_name(m)}</th>"
                html += "</tr></thead><tbody>"

                # Tablo Satırları ve CSS Enjeksiyonu
                for row in processed_table_data:
                    html += "<tr>"
                    html += f"<td class='player-name'>{row['Player']}</td>"
                    html += f"<td class='text-cell'>{row['Age']}</td>"
                    html += f"<td class='text-cell'>{row['Total_Elite_Count']}</td>"
                    html += f"<td class='text-cell' style='font-weight:bold; color: #00d4ff;'>{row['Scout_Score']:.1f}</td>"
                    
                    style_dict = row['_style']
                    for m in metrics:
                        val = row['raw_data'].get(m, 0)
                        bg_color = style_dict.get(m, "transparent")
                        html += f"<td class='stat-cell' style='background-color: {bg_color}; cursor: help;' title='{m}: {val:.2f}'><div style='width: 100%; height: 100%;'></div></td>"
                    html += "</tr>"
                
                html += "</tbody></table>"
                st.markdown(html, unsafe_allow_html=True)