import streamlit as st
from config import CUSTOM_CSS, COLORS
import data_processor as dp
from tabs import player_profile, comparison, team_matrix, transfer_scout

# 1. SAYFA KONFİGÜRASYONU
# Menünün uygulamaya girildiğinde her zaman AÇIK olarak başlamasını garantiliyoruz:
st.set_page_config(page_title="ScoutLab Pro | FM26 Intelligence Hub", layout="wide", initial_sidebar_state="expanded")

# 2. GÖRSEL KİMLİK ENJEKSİYONU (Config'den gelen CSS)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def main():
    # SIDEBAR: Navigasyon ve Veri Yükleme
    st.sidebar.markdown(f"<h2 style='text-align: center; color: {COLORS['primary']};'>SCOUTLAB PRO</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    file = st.sidebar.file_uploader("📂 FM CSV Export Yükle", type=['csv', 'html'])
    min_min = st.sidebar.number_input("⏱️ Minimum Dakika Filtresi", min_value=0, value=300, step=100)
    
    if file:
        # Veri data_processor üzerinden temizlenip /90 ve Lig Çarpanları uygulanarak önbelleğe alınıyor
        df = dp.process_fm_data(file, min_min)
        
        if df.empty:
            st.sidebar.warning("⚠️ Filtreye uygun veya geçerli formatta oyuncu bulunamadı.")
            return
            
        players = sorted(df['Player'].unique())
        
        # ANA SEKMELER
        tab_list = [
            "👤 OYUNCU PROFİLİ", 
            "⚔️ KIYASLAMA / PİZZA", 
            "🏁 ZONE KONTROL MATRİSİ", 
            "💰 İSTATİSTİKSEL SCOUT"
        ]
        tabs = st.tabs(tab_list)

        # SEKMELERİN RENDER EDİLMESİ
        with tabs[0]:
            player_profile.render(df, players)
            
        with tabs[1]:
            comparison.render(df, players)
            
        with tabs[2]:
            team_matrix.render(df)
            
        with tabs[3]:
            transfer_scout.render(df) 
            
    else:
        # Karşılama Ekranı (Boş Durum)
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown(f"<h1 style='text-align: center; color: {COLORS['primary']}; font-size: 3rem;'>ScoutLab Pro'ya Hoş Geldiniz</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: {COLORS['text_muted']}; font-size: 1.2rem;'>Football Manager 26 verilerinizi profesyonel bir veri bilimi platformuna dönüştürün.</p>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class='metric-card' style='margin-top: 30px;'>
                <h3 style='margin-top: 0;'>🚀 Neler Yapabilirsiniz?</h3>
                <ul style='line-height: 1.8;'>
                    <li><b>In-Possession / Out-of-Possession</b> analizleri ve Mustermann Radarları.</li>
                    <li>Sadece özelliklere değil, saha içi <b>istatistiklere ve performansa</b> dayalı transfer önerileri.</li>
                    <li>Oyuncularınızın taktiksel elit bölgelerdeki yerini gösteren <b>Zone Kontrol Matrisleri</b>.</li>
                    <li>Lig çarpanları ile optimize edilmiş adil puanlama sistemi.</li>
                </ul>
                <hr style='border-color: #1F2937;'>
                <p style='color: #00E5FF; text-align: center; margin-bottom: 0;'><i>Başlamak için sol menüden takımınızın veya scout havuzunuzun FM Export CSV dosyasını yükleyin.</i></p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()