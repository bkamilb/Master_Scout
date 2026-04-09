import streamlit as st
import scout_charts as sc
from config import SCATTER_PLOTS

def render(df):
    st.markdown("### 🗺️ Zone Kontrol Matrisi")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        scenario = st.selectbox("🎯 Analiz Senaryosu Seçin", list(SCATTER_PLOTS.keys()))
        conf = SCATTER_PLOTS[scenario]
    
    with col2:
        st.info(f"💡 **İpucu:** {conf.get('desc', 'Sağ üst kadran her iki metrikte de ortalamanın üstünde olan elit performansı gösterir.')}")

    # Grafik fabrikasından oluşturulan stratejik matris
    fig = sc.create_strategic_matrix(df, conf)
    st.plotly_chart(fig, use_container_width=True)