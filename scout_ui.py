# scout_ui.py
import streamlit as st
import radar_factory as rf
from config import PLAYER_FACETS, COLORS
import data_processor as dp

def render_player_header(player_row):
    minutes = player_row.get('Mins', player_row.get('Min', player_row.get('Minutes', 0)))
    league = player_row.get('Division', 'Bilinmeyen Lig')
    
    st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid {COLORS['primary']}; padding: 25px; margin-bottom: 20px;">
            <h1 style="margin:0; color:{COLORS['primary']}; font-size: 2.5rem;">{player_row['Player']}</h1>
            <p style="margin:5px 0 0 0; font-size:1.1rem; color:{COLORS['text_muted']};">
                <b>Mevki:</b> {player_row['Position']} &nbsp;|&nbsp; 
                <b>Yaş:</b> {player_row.get('Age', '-')} &nbsp;|&nbsp; 
                <b>Süre:</b> {minutes} Dakika &nbsp;|&nbsp; 
                <b>Lig:</b> {league}
            </p>
        </div>
    """, unsafe_allow_html=True)

def render_player_intelligence_hub(player_data, df, group):
    facets = PLAYER_FACETS.get(group, {})
    
    if not facets:
        st.warning(f"Bu pozisyon ({group}) için Radar Parametresi bulunamadı.")
        return

    peer_list_all = sorted(df[df['Player'] != player_data['Player']]['Player'].unique().tolist())
    facet_names = list(facets.keys())

    # 1. 🛡️ ORTAK (GLOBAL) HAFIZA
    # Oyuncu eklendiğinde her iki grafikte de aynı anda görünmesi için tek bir state kullanıyoruz.
    state_key = f"active_peers_global_{player_data['Player']}"
    if state_key not in st.session_state:
        st.session_state[state_key] = []
        
    visible_peers = st.session_state[state_key]

    st.markdown(f"<h3 style='color:{COLORS['text_main']}; margin-top:10px; border-bottom: 1px solid {COLORS['grid_lines']}; padding-bottom: 10px;'>📡 In-Possession / Out-of-Possession Profilleri</h3>", unsafe_allow_html=True)

    # 2. 📊 GRAFİKLERİ YAN YANA ÇİZ
    # Facet sayısı kadar sütun oluştur (Genelde IP ve OOP olmak üzere 2 tane)
    chart_cols = st.columns(len(facet_names))
    
    for idx, facet_name in enumerate(facet_names):
        with chart_cols[idx]:
            # Grafiğin kendi küçük başlığı
            st.markdown(f"<h4 style='color:{COLORS['text_main']}; text-align:center;'>{facet_name}</h4>", unsafe_allow_html=True)
            metrics = facets[facet_name]["metrics"]
            
            # Ortak 'visible_peers' listesi ile grafiği çiz
            fig = rf.create_radar_chart(player_data, df, group, metrics, compare_peers=visible_peers)
            st.plotly_chart(fig, use_container_width=True)

    # 3. 🎯 BUTONLARI EN ALTA YERLEŞTİR
    st.markdown("---")
    st.markdown(f"<p style='font-size:14px; color:{COLORS['primary']}; font-weight:bold; text-align:center; margin-bottom:15px;'>⚡ Kıyaslamak istediğiniz oyuncuları seçin (Seçiminiz her iki grafiğe de yansır - Maksimum 2 kişi):</p>", unsafe_allow_html=True)
    
    # Alt tarafta daha fazla yerimiz olduğu için butonları 8'li dizebiliriz
    btns_per_row = 8 
    for i in range(0, len(peer_list_all), btns_per_row):
        row_batch = peer_list_all[i : i + btns_per_row]
        b_cols = st.columns(btns_per_row)
        
        for idx, peer in enumerate(row_batch):
            is_active = peer in visible_peers
            btn_label = (f"🔴 {peer}" if visible_peers.index(peer) == 0 else f"🟡 {peer}") if is_active else f"⚪ {peer}"
            
            if b_cols[idx].button(btn_label, key=f"btn_{state_key}_{peer}"):
                if is_active:
                    visible_peers.remove(peer)
                else:
                    if len(visible_peers) >= 2: visible_peers.pop(0) 
                    visible_peers.append(peer)
                st.session_state[state_key] = visible_peers
                st.rerun()