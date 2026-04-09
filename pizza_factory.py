# pizza_factory.py
import matplotlib.pyplot as plt
from mplsoccer import PyPizza
from config import COLORS

def create_pizza_comparison(params, player_vals, compare_vals, player_name, ref_name):
    p_vals = [float(v) for v in player_vals]
    c_vals = [float(v) for v in compare_vals]
    
    bg_color = COLORS['background']
    p_color = COLORS['primary']
    c_color = COLORS['secondary']
    
    baker = PyPizza(
        params=params,                  
        background_color=bg_color, 
        straight_line_color=COLORS['grid_lines'],  
        straight_line_lw=1.5,
        last_circle_lw=1,               
        other_circle_lw=1,
    )

    fig, ax = baker.make_pizza(
        values=p_vals,
        compare_values=c_vals,
        figsize=(6, 6), # Daha kompakt boyut
        kwargs_slices=dict(facecolor=p_color, edgecolor=bg_color, zorder=2, linewidth=1, alpha=0.7),
        kwargs_compare=dict(facecolor=c_color, edgecolor=bg_color, zorder=2, linewidth=1, alpha=0.4),
        # Fontsize 8'e çekildi ve ha ayarı kütüphaneye bırakıldı
        kwargs_params=dict(color=COLORS['text_main'], fontsize=8, va="center", alpha=0.9),
        kwargs_values=dict(color=bg_color, fontsize=7, zorder=4, bbox=dict(edgecolor='white', facecolor=p_color, boxstyle="round,pad=0.1", lw=1)),
        kwargs_compare_values=dict(color=bg_color, fontsize=7, zorder=4, bbox=dict(edgecolor='white', facecolor=c_color, boxstyle="round,pad=0.1", lw=1))
    )

    fig.text(0.515, 0.98, player_name, size=13, ha="center", color=p_color, fontweight="bold")
    fig.text(0.515, 0.95, f"vs {ref_name}", size=9, ha="center", color=c_color)
    
    return fig