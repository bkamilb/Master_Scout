# scout_charts.py
import plotly.express as px
import plotly.graph_objects as go
import data_processor as dp
from config import COLORS

def create_strategic_matrix(df, conf):
    """
    Takım veya Scout havuzundaki oyuncuları 2 metrik (X ve Y) üzerinden
    kıyaslayan ve medyan (ortanca) çizgileriyle elitleri belirleyen Matrix.
    Tüm senaryolarda (Top Taşıma dahil) size guard uygulanır.
    """
    df_plot = df.copy()

    # X ve Y eksenlerinin değerlerini get_val ile doldur
    for axis in ['x', 'y']:
        metric = conf.get(axis)
        if metric:
            df_plot[metric] = df_plot.apply(lambda row: dp.get_val(row, metric), axis=1)

    # Size metriği için özel guard:
    # - Önce get_val ile doldur
    # - Sıfır / negatif değerleri küçük pozitif sayıya çek (Plotly crash yapar)
    # - Eğer veri pratikte yoksa (max <= 0.01) size tamamen kaldırılır
    size_metric = conf.get('size')
    size_param = None
    if size_metric:
        df_plot[size_metric] = df_plot.apply(lambda row: dp.get_val(row, size_metric), axis=1)
        df_plot[size_metric] = df_plot[size_metric].clip(lower=0.01)
        if df_plot[size_metric].max() > 0.1:
            size_param = size_metric

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

    # Medyan (Ortalama) Çizgileri — Elitleri Ayırmak İçin
    x_col = conf['x']
    y_col = conf['y']
    if len(df_plot) > 0 and x_col in df_plot.columns and y_col in df_plot.columns:
        med_x = df_plot[x_col].median()
        med_y = df_plot[y_col].median()
        x_max = df_plot[x_col].max()
        y_max = df_plot[y_col].max()

        fig.add_hline(
            y=med_y, line_dash="dash",
            line_color=COLORS['grid_lines'],
            annotation_text="Lig Ortalaması",
            annotation_font_color=COLORS['text_muted']
        )
        fig.add_vline(
            x=med_x, line_dash="dash",
            line_color=COLORS['grid_lines'],
            annotation_text="Lig Ortalaması",
            annotation_font_color=COLORS['text_muted']
        )

        # Sağ üst köşeyi (Elit Bölge) hafif aydınlat
        if x_max > med_x and y_max > med_y:
            fig.add_shape(
                type="rect", xref="x", yref="y",
                x0=med_x, y0=med_y,
                x1=x_max * 1.05, y1=y_max * 1.05,
                fillcolor=COLORS['zone_elite'],
                opacity=0.3, layer="below", line_width=0
            )

        # Sol alt köşeyi (Zayıf Bölge) çok hafif kırmızı vurgula
        x_min = df_plot[x_col].min()
        y_min = df_plot[y_col].min()
        if x_min < med_x and y_min < med_y:
            fig.add_shape(
                type="rect", xref="x", yref="y",
                x0=x_min * 0.95, y0=y_min * 0.95,
                x1=med_x, y1=med_y,
                fillcolor=COLORS['zone_poor'],
                opacity=0.25, layer="below", line_width=0
            )

    size_label = f"Boyut: {size_param}" if size_param else ""
    fig.update_layout(
        title=dict(
            text=f"{conf.get('desc', 'Stratejik Performans Matrisi')}   <sup style='font-size:11px;color:#9CA3AF;'>{size_label}</sup>",
            font=dict(color=COLORS['primary'], size=16)
        ),
        xaxis_title=f"⬅️ Düşük  |  {x_col}  |  Yüksek ➡️",
        yaxis_title=f"⬅️ Düşük  |  {y_col}  |  Yüksek ➡️",
        margin=dict(l=20, r=20, t=50, b=20),
        legend_title="Mevki",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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

    fig.update_traces(marker=dict(size=10, opacity=0.4), selector=dict(mode='markers'))

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
