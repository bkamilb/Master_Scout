# radar_factory.py
import plotly.graph_objects as go
import radar_logic as rl
import data_processor as dp
from config import COLORS, METRIC_PROPS

def create_radar_chart(player_row, team_df, group_name, metrics, mode="performance", title_override=None, compare_peers=None):
    """
    Oyuncu için 0-100 mutlak puan sistemine dayalı, arkasında Mustermann 
    bölgelerinin renklendirildiği yüksek çözünürlüklü radar grafiği çizer.
    """
    # 1. Ana Oyuncunun Verilerini Hesapla
    p_data = rl.calculate_radar_points(player_row, team_df, metrics, group_name)
    p_vals = p_data["display_values"]
    raw_vals = p_data["raw_values"]
    
    # --- 🧠 PERCENTILE (YÜZDELİK DİLİM) HESAPLAMA ---
    hover_texts = []
    for i, m in enumerate(metrics):
        val = raw_vals[i]
        is_inverse = METRIC_PROPS.get(m, False)
        
        # O metrikteki tüm oyuncuların verilerini çek
        all_vals = [dp.get_val(row, m) for _, row in team_df.iterrows()]
        all_vals = [v for v in all_vals if v is not None]
        
        if len(all_vals) > 0:
            if is_inverse:
                # Ters metrikse (Yenilen gol, Top kaybı) daha DÜŞÜK olan daha iyidir
                better_count = sum(1 for v in all_vals if v > val)
            else:
                # Normal metrikse daha YÜKSEK olan daha iyidir
                better_count = sum(1 for v in all_vals if v < val)
            
            percentile = (better_count / len(all_vals)) * 100
        else:
            percentile = 50.0
            
        hover_texts.append(f"<b>{m}</b><br>Skor: {p_vals[i]:.1f}/100<br>Ham Veri: {val:.2f}<br><i>Mevki Dilimi (Percentile): <b>%{percentile:.0f}</b></i>")
    
    fig = go.Figure()

    # 2. Arkadaki Silüetleri (Rakipleri) Çiz
    peers_processed = rl.get_group_peers_data(player_row, team_df, metrics, group_name)
    for peer_vals in peers_processed:
        fig.add_trace(go.Scatterpolar(
            r=peer_vals + [peer_vals[0]], 
            theta=metrics + [metrics[0]],
            mode='lines',
            line=dict(color=COLORS['peers'], width=1),
            fill=None,
            hoverinfo='skip',
            showlegend=False
        ))

    # 3. Spesifik Kıyaslama Hedefleri Varsa Onları Çiz (Örn: Diğer Forvetler)
    if compare_peers:
        for idx, peer_name in enumerate(compare_peers):
            peer_row = team_df[team_df['Player'] == peer_name]
            if not peer_row.empty:
                peer_data = rl.calculate_radar_points(peer_row.iloc[0], team_df, metrics, group_name)
                c_vals = peer_data["display_values"]
                
                color = COLORS.get('secondary', '#FF3366') if idx == 0 else '#FFB020'
                fig.add_trace(go.Scatterpolar(
                    r=c_vals + [c_vals[0]],
                    theta=metrics + [metrics[0]],
                    fill='toself',
                    fillcolor=color.replace(')', ', 0.15)').replace('rgb', 'rgba') if 'rgba' not in color else color,
                    line=dict(color=color, width=2),
                    marker=dict(size=6, color=color),
                    name=peer_name,
                    showlegend=True
                ))

    # 4. Ana Oyuncuyu En Öne Çiz (Radar Poligonu)
    fig.add_trace(go.Scatterpolar(
        r=p_vals + [p_vals[0]],
        theta=metrics + [metrics[0]],
        fill='toself',
        fillcolor=COLORS['primary_glow'],
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8, color=COLORS['text_main'], line=dict(color=COLORS['primary'], width=2)),
        name=str(player_row['Player']),
        text=hover_texts + [hover_texts[0]],
        hoverinfo="text",
        showlegend=True
    ))

    # 5. Mustermann Arkaplan Bölgelerini (0-25 Kötü, 25-50 Ort, 50-75 İyi, 75-100 Elit) Ayarla
    fig.update_layout(
        template="plotly_dark",
        title=dict(text=title_override or "Intelligence Radar", font=dict(color=COLORS['primary'], size=16), y=0.95, x=0.5, xanchor='center'),
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 100],
                tickvals=[25, 50, 75, 100],
                ticktext=["Poor", "Average", "Good", "Elite"],
                tickfont=dict(size=9, color=COLORS['text_muted']),
                gridcolor=COLORS['grid_lines'],
                showline=False
            ),
            angularaxis=dict(
                gridcolor=COLORS['grid_lines'],
                tickfont=dict(size=11, color=COLORS['text_main'], weight="bold")
            ),
            bgcolor=COLORS['background']
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=80, b=40, l=40, r=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5, font=dict(color=COLORS['text_main']))
    )

    return fig