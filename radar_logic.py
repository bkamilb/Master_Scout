# radar_logic.py
import data_processor as dp
from config import MUSTERMANN_ZONES, METRIC_PROPS

def get_score_from_zones(val, metric, group):
    """
    Oyuncunun ham verisini, 4'lü Mustermann Mutlak Sınırlarına göre 0-100 arası 
    standart bir 'Scout Puanı'na (Interpolasyon) dönüştürür.
    Sıfıra bölünme (ZeroDivisionError) korumaları eklenmiştir.
    """
    is_inverse = METRIC_PROPS.get(metric, False)
    
    # İlgili Mustermann Grubunun metrik sınırlarını al
    zones = MUSTERMANN_ZONES.get(group, {}).get(metric)
    
    # Eğer metrik bu gruba tanımlı değilse, grafiği patlatmamak için nötr (50) dön.
    if not zones:
        return 50.0 

    b1, b2, b3, b4 = zones # Sırasıyla: [Kötü, Ortalama, İyi, Elit]

    # --- KORUMA: Sıfıra bölünmeyi engellemek için epsilon değeri ---
    epsilon = 1e-5

    # --- TERS METRİK MANTIĞI (Örn: Yenilen Gol, Top Kaybı - Düşük olan elittir) ---
    if is_inverse:
        # Değer b1'den (kötüden) bile büyükse (0-25 arası ceza puanı)
        if val >= b1: 
            safe_b1 = b1 if b1 != 0 else epsilon
            return max(0.0, 25 - ((val - b1) / safe_b1) * 25)
        
        # Bölgeler arası interpolasyon
        if val >= b2: 
            diff = (b1 - b2) if (b1 - b2) != 0 else epsilon
            return 25 + ((b1 - val) / diff) * 25
        if val >= b3: 
            diff = (b2 - b3) if (b2 - b3) != 0 else epsilon
            return 50 + ((b2 - val) / diff) * 25
        if val >= b4: 
            diff = (b3 - b4) if (b3 - b4) != 0 else epsilon
            return 75 + ((b3 - val) / diff) * 20
        
        # Elit barajını da aştıysa (b4'ten küçükse)
        safe_b4 = b4 if b4 != 0 else epsilon
        return min(100.0, 95 + ((b4 - val) / safe_b4) * 5)

    # --- NORMAL METRİK MANTIĞI (Yüksek olan elittir) ---
    else:
        # Kötü sınırından bile düşükse (0-25 arası ceza)
        if val <= b1: 
            safe_b1 = b1 if b1 != 0 else epsilon
            return max(0.0, (val / safe_b1) * 25)
        
        # Bölgeler arası interpolasyon
        if val <= b2: 
            diff = (b2 - b1) if (b2 - b1) != 0 else epsilon
            return 25 + ((val - b1) / diff) * 25
        if val <= b3: 
            diff = (b3 - b2) if (b3 - b2) != 0 else epsilon
            return 50 + ((val - b2) / diff) * 25
        if val <= b4: 
            diff = (b4 - b3) if (b4 - b3) != 0 else epsilon
            return 75 + ((val - b3) / diff) * 20
        
        # Elit barajını da aştıysa
        safe_b4 = b4 if b4 != 0 else epsilon
        return min(100.0, 95 + ((val - b4) / safe_b4) * 5)

def calculate_radar_points(player_row, team_df, metrics, group_name):
    """
    Ana oyuncu için Radar/Pizza grafiğine gönderilecek işlenmiş 0-100 puanları 
    ve tooltip'lerde gösterilecek ham değerleri hesaplar.
    """
    processed_values = []
    raw_values = []
    
    for m in metrics:
        val = dp.get_val(player_row, m)
        raw_values.append(val)
        
        score = get_score_from_zones(val, m, group_name)
        processed_values.append(score)
        
    return {"display_values": processed_values, "raw_values": raw_values}

def get_group_peers_data(player_row, team_df, metrics, group_name):
    """Arkadaki rakipler için verileri hazırlayan fonksiyon"""
    auto_group = dp.get_player_group(player_row['Position'])
    
    peers = [row for _, row in team_df.iterrows() 
             if dp.get_player_group(row['Position']) == auto_group 
             and row['Player'] != player_row['Player']]
    
    peers_processed = []
    for peer in peers:
        p_vals = []
        for m in metrics:
            val = dp.get_val(peer, m)
            score = get_score_from_zones(val, m, group_name)
            p_vals.append(score)
        peers_processed.append(p_vals)
        
    return peers_processed