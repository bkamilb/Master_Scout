# scout_charts.py
import plotly.express as px
import data_processor as dp
from config import COLORS

def create_strategic_matrix(df, conf):
    """
    Takım veya Scout havuzundaki oyuncuları 2 metrik (X ve Y) üzerinden 
    kıyaslayan ve medyan (ortanca) çizgileriyle elitleri belirleyen Matrix.
    """
    df_plot = df.copy()
    
    for axis in ['x', 'y', 'size']:
        metric = conf.get(axis)
        if metric:
            df_plot[metric] = df_plot.apply(lambda row: dp.get_val(row, metric), axis=1)

    size_param = conf.get('size') if conf.get('size') in df_plot.columns else None

    fig = px.scatter(
        df_plot, 
        x=conf['x'], 
        y=conf['y'], 
        size=size_param,
        color="Position", 
        hover_name="Player",
        template="plotly_dark",
        height=600,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Medyan (Ortalama) Çizgileri - Elitleri Ayırmak İçin
    if len(df_plot) > 0:
        med_x = df_plot[conf['x']].median()
        med_y = df_plot[conf['y']].median()
        
        fig.add_hline(y=med_y, line_dash="dash", line_color=COLORS['grid_lines'], annotation_text="Lig Ortalaması")
        fig.add_vline(x=med_x, line_dash="dash", line_color=COLORS['grid_lines'], annotation_text="Lig Ortalaması")
        
        # Sağ üst köşeyi (Elit Bölge) hafif aydınlat
        fig.add_shape(type="rect", xref="x", yref="y",
                      x0=med_x, y0=med_y, x1=df_plot[conf['x']].max()*1.05, y1=df_plot[conf['y']].max()*1.05,
                      fillcolor=COLORS['zone_elite'], opacity=0.3, layer="below", line_width=0)

    fig.update_layout(
        title=dict(text=conf.get('desc', 'Stratejik Performans Matrisi'), font=dict(color=COLORS['primary'], size=16)),
        xaxis_title=f"⬅️ Düşük | {conf['x']} | Yüksek ➡️",
        yaxis_title=f"⬅️ Düşük | {conf['y']} | Yüksek ➡️",
        margin=dict(l=20, r=20, t=40, b=20),
        legend_title="Mevki"
    )
    
    return fig

def create_group_scatter(df, target_player, group_name):
    """Tüm oyuncuları gösterir, hedef oyuncuyu vurgular."""
    df_plot = df.copy()
    min_col = 'Mins' if 'Mins' in df_plot.columns else 'Min' if 'Min' in df_plot.columns else 'Minutes'
    df_plot['Mins_Plot'] = df_plot[min_col] if min_col in df_plot.columns else 0
        
    fig = px.scatter(
        df_plot, x="Age", y="Mins_Plot", text="Player", color="Position",
        hover_name="Player", template="plotly_dark", height=450
    )
    
    # Tüm oyuncuları biraz transparan yap
    fig.update_traces(marker=dict(size=10, opacity=0.4), selector=dict(mode='markers'))
    
    # Sadece hedef oyuncuyu belirgin (opak ve büyük) yap
    target_row = df_plot[df_plot['Player'] == target_player]
    if not target_row.empty:
        fig.add_scatter(
            x=target_row['Age'], 
            y=target_row['Mins_Plot'],
            mode='markers+text',
            marker=dict(size=20, color=COLORS['primary'], line=dict(color='white', width=2)),
            text=target_row['Player'],
            textposition="top center",
            textfont=dict(color=COLORS['primary'], size=14, weight='bold'),
            name="Hedef Oyuncu"
        )
        
    fig.update_layout(
        title="Yaş vs Süre (Tecrübe Eğrisi)",
        xaxis_title="Yaş",
        yaxis_title="Oynadığı Dakika",
        showlegend=False
    )
    return fig