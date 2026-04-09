# tabs/comparison.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import data_processor as dp
from config import MUSTERMANN_ZONES, COLORS

def calculate_similarity_z_score(vector1, vector2):
    """Vektörel kosinüs benzerliğini hesaplar (Z-Score verileri için)."""
    v1 = np.array(vector1)
    v2 = np.array(vector2)
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0: 
        return 0.0
    cos_sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return max(0, cos_sim * 100)

def render(df, players):
    st.markdown("### ⚔️ Takım İçi Kapsamlı Düello: Performans vs DNA")
    st.caption("Solda sahada ürettikleri istatistikleri (/90 Performans), sağda ise 1-20 FM niteliklerini (DNA) kıyaslayın.")
    st.markdown("---")
    
    # --- 1. KONTROL PANELİ ---
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    with col1:
        p1 = st.selectbox("🔵 1. Oyuncu (Kırmızı Köşe)", players, key="duel_p1")
    with col2:
        p2 = st.selectbox("🔴 2. Oyuncu (Mavi Köşe)", players, index=1 if len(players)>1 else 0, key="duel_p2")
    with col3:
        p1_data = df[df['Player'] == p1].iloc[0]
        auto_g = dp.get_player_group(p1_data['Position'])
        group_options = ["Goalkeepers", "Defenders", "Midfielders", "Attackers"]
        group = st.selectbox("🎯 Analiz Rolü", group_options, index=group_options.index(auto_g))

    if p1 == p2:
        st.warning("Lütfen kıyaslama yapmak için iki farklı oyuncu seçin.")
        return

    p2_data = df[df['Player'] == p2].iloc[0]

    # --- 2. VERİ HAZIRLIĞI: SOL GRAFİK (PERFORMANS) ---
    perf_metrics = list(MUSTERMANN_ZONES.get(group, {}).keys())
    p1_perf_vals, p2_perf_vals = [], []
    p1_perf_scores, p2_perf_scores = [], []

    if perf_metrics:
        # Performans verilerini 0-100 Mustermann puanına çevirme
        for m in perf_metrics:
            v1, v2 = float(dp.get_val(p1_data, m)), float(dp.get_val(p2_data, m))
            p1_perf_vals.append(v1)
            p2_perf_vals.append(v2)
            
            bounds = MUSTERMANN_ZONES.get(group, {}).get(m, [0,0,0,0])
            is_inv = bounds[0] > bounds[3] if bounds else False
            epsilon = 1e-5
            
            def get_score(val, b):
                b1, b2, b3, b4 = b
                if not is_inv:
                    if val <= b1: return max(0, (val / (b1 or epsilon)) * 25)
                    if val <= b2: return 25 + ((val - b1) / ((b2 - b1) or epsilon)) * 25
                    if val <= b3: return 50 + ((val - b2) / ((b3 - b2) or epsilon)) * 25
                    if val <= b4: return 75 + ((val - b3) / ((b4 - b3) or epsilon)) * 20
                    return min(100, 95 + ((val - b4) / (b4 or epsilon)) * 5)
                else:
                    if val >= b1: return max(0, 25 - ((val - b1) / (b1 or epsilon)) * 25)
                    if val >= b2: return 25 + ((b1 - val) / ((b1 - b2) or epsilon)) * 25
                    if val >= b3: return 50 + ((b2 - val) / ((b2 - b3) or epsilon)) * 25
                    if val >= b4: return 75 + ((b3 - val) / ((b3 - b4) or epsilon)) * 20
                    return min(100, 95 + ((b4 - val) / (b4 or epsilon)) * 5)

            p1_perf_scores.append(get_score(v1, bounds))
            p2_perf_scores.append(get_score(v2, bounds))

    # --- 3. VERİ HAZIRLIĞI: SAĞ GRAFİK (DNA 1-20 & KADRANLAR) ---
    is_p1_gk = group == "Goalkeepers"
    
    if not is_p1_gk:
        # Dribbling özellikle Hücum alanına taşındı.
        quadrants = {
            "🛡️ Savunma": ['Marking', 'Tackling', 'Positioning', 'Heading'],
            "🧠 Zihinsel": ['Determination', 'Composure', 'Work Rate', 'Team Work', 'Anticipation', 'Concentration', 'Off The Ball', 'Decisions'],
            "⚔️ Hücum": ['Finishing', 'Technique', 'Passing', 'Vision', 'Dribbling', 'Crossing', 'First Touch', 'Flair'],
            "⚡ Fiziksel": ['Pace', 'Acceleration', 'Strength', 'Stamina', 'Agility', 'Balance', 'Jumping Reach']
        }
    else:
        quadrants = {
            "🧤 Kalecilik": ['Handling', 'Reflexes', 'One On Ones', 'Aerial Reach', 'Command Of Area', 'Communication'],
            "🧠 Zihinsel": ['Determination', 'Composure', 'Anticipation', 'Concentration', 'Decisions'],
            "🦶 Dağıtım": ['Passing', 'Vision', 'Kicking', 'Throwing'],
            "⚡ Fiziksel": ['Agility', 'Balance', 'Strength', 'Acceleration']
        }

    # Kadran Renkleri (Arka plan dolgusu için pastel tonlar)
    quadrant_colors = {
        "🛡️ Savunma": "rgba(59, 130, 246, 0.15)",  # Mavi
        "🧤 Kalecilik": "rgba(59, 130, 246, 0.15)", # Mavi
        "🧠 Zihinsel": "rgba(139, 92, 246, 0.15)",  # Mor
        "⚔️ Hücum": "rgba(239, 68, 68, 0.15)",      # Kırmızı
        "🦶 Dağıtım": "rgba(239, 68, 68, 0.15)",    # Kırmızı
        "⚡ Fiziksel": "rgba(16, 185, 129, 0.15)"   # Yeşil
    }

    dna_metrics = []
    for q, m_list in quadrants.items():
        q_metrics = [m for m in m_list if m in df.columns]
        dna_metrics.extend(q_metrics)
        quadrants[q] = q_metrics

    if dna_metrics:
        matrix_raw = df[dna_metrics].values
        means = np.mean(matrix_raw, axis=0)
        stds = np.std(matrix_raw, axis=0)
        stds[stds == 0] = 1e-10 

        p1_dna_raw = pd.to_numeric(p1_data[dna_metrics], errors='coerce').fillna(10).values.astype(float)
        p2_dna_raw = pd.to_numeric(p2_data[dna_metrics], errors='coerce').fillna(10).values.astype(float)

        p1_z = (p1_dna_raw - means) / stds
        p2_z = (p2_dna_raw - means) / stds

        similarity_pct = calculate_similarity_z_score(p1_z, p2_z)
        
        # Üstünlükler (Sadece DNA üzerinden hesaplanıyor)
        p1_adv, p2_adv = [], []
        for i, m in enumerate(dna_metrics):
            diff = p1_z[i] - p2_z[i]
            if diff >= 0.8: p1_adv.append((m, diff, p1_dna_raw[i], p2_dna_raw[i]))
            elif diff <= -0.8: p2_adv.append((m, -diff, p1_dna_raw[i], p2_dna_raw[i]))
                
        p1_adv.sort(key=lambda x: x[1], reverse=True)
        p2_adv.sort(key=lambda x: x[1], reverse=True)

    # --- 4. GÖRSEL ARAYÜZ (UI) OLUŞTURMA ---
    
    # Ortak Özellikler Paneli
    sim_color = "#00FF88" if similarity_pct >= 85 else "#FFB020" if similarity_pct >= 70 else "#FF4444"
    
    col_sim, col_adv1, col_adv2 = st.columns([1, 1.5, 1.5])
    with col_sim:
        st.markdown(f"""
        <div style='background-color: #121826; padding: 20px; border-radius: 10px; text-align: center; height: 100%; border: 1px solid #1F2937;'>
            <h4 style='margin: 0; color: #9CA3AF;'>🧬 DNA Benzerliği</h4>
            <h1 style='margin: 10px 0 0 0; color: {sim_color}; font-size: 2.5rem;'>%{similarity_pct:.1f}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col_adv1:
        st.markdown(f"<div style='background-color: #121826; padding: 15px; border-radius: 10px; height: 100%; border: 1px solid #1F2937;'><h5 style='color: {COLORS.get('primary', '#00E5FF')}; margin-top:0;'>📈 {p1} Üstünlükleri</h5>", unsafe_allow_html=True)
        if p1_adv:
            for m, diff, v1, v2 in p1_adv[:4]:
                st.markdown(f"<div style='font-size:14px;'>- <b>{m}:</b> {v1:.0f} <span style='color: #888;'>(vs {v2:.0f})</span></div>", unsafe_allow_html=True)
        else:
            st.caption("Belirgin üstünlük yok.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_adv2:
        st.markdown(f"<div style='background-color: #121826; padding: 15px; border-radius: 10px; height: 100%; border: 1px solid #1F2937;'><h5 style='color: {COLORS.get('secondary', '#FF3366')}; margin-top:0;'>📉 {p2} Üstünlükleri</h5>", unsafe_allow_html=True)
        if p2_adv:
            for m, diff, v1, v2 in p2_adv[:4]:
                st.markdown(f"<div style='font-size:14px;'>- <b>{m}:</b> {v2:.0f} <span style='color: #888;'>(vs {v1:.0f})</span></div>", unsafe_allow_html=True)
        else:
            st.caption("Belirgin üstünlük yok.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # --- 5. İKİ GRAFİĞİ YAN YANA ÇİZME ---
    col_graph1, col_graph2 = st.columns(2)

    # SOL GRAFİK: PERFORMANS (0-100)
    with col_graph1:
        if not perf_metrics:
            st.warning("Bu rol için performans verisi bulunamadı.")
        else:
            fig_perf = go.Figure()
            
            p1_hover = [f"<b>{m}</b><br>Skor: {p1_perf_scores[i]:.1f}<br>Veri (/90): {p1_perf_vals[i]:.2f}" for i, m in enumerate(perf_metrics)]
            p2_hover = [f"<b>{m}</b><br>Skor: {p2_perf_scores[i]:.1f}<br>Veri (/90): {p2_perf_vals[i]:.2f}" for i, m in enumerate(perf_metrics)]

            # P1 Performans
            fig_perf.add_trace(go.Scatterpolar(
                r=p1_perf_scores + [p1_perf_scores[0]], theta=perf_metrics + [perf_metrics[0]],
                fill='toself', fillcolor=COLORS.get('primary_glow', 'rgba(0, 229, 255, 0.15)'),
                line=dict(color=COLORS.get('primary', '#00E5FF'), width=3),
                name=p1, text=p1_hover + [p1_hover[0]], hoverinfo="text"
            ))

            # P2 Performans
            fig_perf.add_trace(go.Scatterpolar(
                r=p2_perf_scores + [p2_perf_scores[0]], theta=perf_metrics + [perf_metrics[0]],
                fill='toself', fillcolor=COLORS.get('secondary_glow', 'rgba(255, 51, 102, 0.15)'),
                line=dict(color=COLORS.get('secondary', '#FF3366'), width=3),
                name=p2, text=p2_hover + [p2_hover[0]], hoverinfo="text"
            ))

            fig_perf.update_layout(
                template="plotly_dark",
                title=dict(text=f"Sahadaki Performans (/90) - {group}", font=dict(color='#F3F4F6', size=16), x=0.5),
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], tickvals=[25, 50, 75, 100], ticktext=["Poor", "Average", "Good", "Elite"], tickfont=dict(color='#9CA3AF', size=9), gridcolor='#1F2937'),
                    angularaxis=dict(gridcolor='#1F2937', tickfont=dict(color='#F3F4F6', size=10)),
                    bgcolor='#0A0E17'
                ),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=60, b=40, l=40, r=40),
                legend=dict(orientation="h", y=-0.15, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_perf, use_container_width=True)

    # SAĞ GRAFİK: DNA (Z-SCORE VE KADRANLAR)
    with col_graph2:
        if not dna_metrics:
            st.warning("FM nitelikleri bulunamadı.")
        else:
            fig_dna = go.Figure()

            # Kadranları (Bölgeleri) arka plan olarak boyama (Barpolar Tekniği)
            for q_name, q_metrics in quadrants.items():
                if q_metrics:
                    fig_dna.add_trace(go.Barpolar(
                        r=[5.0] * len(q_metrics),        # Çap büyüklüğü (Radius)
                        base=[-2.5] * len(q_metrics),    # Z-score -2.5'ten başlar
                        theta=q_metrics,
                        marker_color=quadrant_colors.get(q_name, "rgba(255,255,255,0.1)"),
                        name=q_name,
                        hoverinfo='skip',
                        showlegend=True,
                        marker_line_width=0
                    ))

            # P1 DNA
            p1_dna_hover = [f"<b>{m}</b><br>{p1} (FM): {p1_dna_raw[i]:.0f}<br>{p2} (FM): {p2_dna_raw[i]:.0f}" for i, m in enumerate(dna_metrics)]
            fig_dna.add_trace(go.Scatterpolar(
                r=p1_z.tolist() + [p1_z[0]], theta=dna_metrics + [dna_metrics[0]],
                mode='lines+markers',
                line=dict(color=COLORS.get('primary', '#00E5FF'), width=3),
                marker=dict(size=6, color="#0A0E17", line=dict(color=COLORS.get('primary', '#00E5FF'), width=2)),
                name=f"{p1} (DNA)", text=p1_dna_hover + [p1_dna_hover[0]], hoverinfo="text"
            ))

            # P2 DNA
            fig_dna.add_trace(go.Scatterpolar(
                r=p2_z.tolist() + [p2_z[0]], theta=dna_metrics + [dna_metrics[0]],
                mode='lines+markers',
                line=dict(color=COLORS.get('secondary', '#FF3366'), width=3),
                marker=dict(size=6, color="#0A0E17", line=dict(color=COLORS.get('secondary', '#FF3366'), width=2)),
                name=f"{p2} (DNA)", text=p1_dna_hover + [p1_dna_hover[0]], hoverinfo="text"
            ))

            fig_dna.update_layout(
                template="plotly_dark",
                title=dict(text="Oyuncu DNA'sı (1-20 Özellikler)", font=dict(color='#F3F4F6', size=16), x=0.5),
                polar=dict(
                    radialaxis=dict(
                        visible=True, range=[-2.5, 2.5], 
                        tickvals=[-2.0, -1.0, 0, 1.0, 2.0],
                        ticktext=["-2σ", "-1σ", "Ort.", "+1σ", "+2σ"], 
                        tickfont=dict(color='#9CA3AF', size=9), gridcolor='#1F2937'
                    ),
                    angularaxis=dict(gridcolor='#1F2937', tickfont=dict(color='#F3F4F6', size=10)),
                    bgcolor='#0A0E17',
                    barmode='overlay' # Kadranların birbirinin üstüne binmesini engeller
                ),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=60, b=40, l=40, r=40),
                legend=dict(orientation="h", y=-0.15, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_dna, use_container_width=True)