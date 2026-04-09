# similarity_engine.py
import numpy as np
import pandas as pd
from config import RADAR_PARAMS
import data_processor as dp

# --- 1. DNA (YAPISAL) BENZERLİK ---
# Sadece Kendi Takımımız İçin (FM'in 1-20'lik Nitelik Skalası Üzerinden)

def find_dna_twins(df, target_player_name, top_n=3):
    """
    Oyuncunun sadece zihinsel, fiziksel ve teknik özelliklerini kıyaslar. 
    (Öklid Mesafesi kullanılır: Mesafe ne kadar azsa, oyuncu o kadar benzerdir)
    """
    if target_player_name not in df['Player'].values:
        return []
        
    # Sadece CSV'de gerçekten var olan özellikleri al
    available_params = [p for p in RADAR_PARAMS if p in df.columns]
    if not available_params:
        return []

    target_vals = df[df['Player'] == target_player_name][available_params].values[0]
    others = df[df['Player'] != target_player_name].copy()
    
    if others.empty: return []

    # Euclidean Distance Hesabı
    distances = np.linalg.norm(others[available_params].values - target_vals, axis=1)
    others['similarity_score'] = distances
    
    # En düşük mesafe (En yüksek benzerlik) olanları getir
    return others.sort_values('similarity_score').head(top_n).to_dict('records')

# --- 2. PERFORMANS (İSTATİSTİKSEL) BENZERLİK ---
# Transfer havuzu için /90 metriklerine dayalı

def find_similar_players(df, target_player_name, metrics, top_n=5):
    """
    Scout transfer hedeflerini oyuncunun sahada ürettiği istatistiklere 
    göre bulur. (Kosinüs Benzerliği - Cosine Similarity kullanılır)
    Veriler işleme girmeden önce Z-Score ile standardize edilir.
    """
    if target_player_name not in df['Player'].values or not metrics:
        return []

    # Hedef ve havuzdaki oyuncuların tüm metriklerini çek (Lig çarpanlı veriler)
    def extract_metrics(row):
        return [dp.get_val(row, m) for m in metrics]

    matrix = np.array([extract_metrics(row) for _, row in df.iterrows()], dtype=float)
    
    # Eğer filtreler sonucu tüm tablo 0 ise matris çökmesini engelle
    if np.all(matrix == 0):
        return []

    # --- 🧠 Z-SCORE STANDARDİZASYONU (MÜKEMMELLEŞTİRİLMİŞ KISIM) ---
    # Farklı ölçeklerdeki verilerin (örn: 0.5 xG ile 70 Pas) eşit ağırlıkta 
    # değerlendirilmesi için veriyi 0 ortalama ve 1 standart sapma ile hizalıyoruz.
    means = np.mean(matrix, axis=0)
    stds = np.std(matrix, axis=0)
    stds[stds == 0] = 1e-10 # Sıfıra bölünmeyi engelle
    
    matrix_standardized = (matrix - means) / stds

    # Hedef oyuncunun standartlaştırılmış vektörünü bul
    player_idx = df[df['Player'] == target_player_name].index[0]
    target_vector = matrix_standardized[player_idx]

    # Vektörel Kosinüs Benzerliği (Cosine Similarity) Hesaplama
    # Formül: (A . B) / (||A|| * ||B||)
    target_norm = np.linalg.norm(target_vector)
    matrix_norms = np.linalg.norm(matrix_standardized, axis=1)
    
    # Sıfıra bölünmeyi engelle
    denominators = target_norm * matrix_norms
    denominators[denominators == 0] = 1e-10 
    
    cos_similarities = np.dot(matrix_standardized, target_vector) / denominators
    
    # Sonuçları DataFrame'e ekle
    df_sim = df.copy()
    df_sim['Similarity'] = cos_similarities
    
    # Hedef oyuncunun kendisini çıkar ve en benzerleri getir
    df_sim = df_sim[df_sim['Player'] != target_player_name]
    df_sim = df_sim.sort_values('Similarity', ascending=False)
    
    return df_sim.head(top_n).to_dict('records')