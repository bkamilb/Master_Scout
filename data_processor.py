import pandas as pd
import streamlit as st
from config import LEAGUE_MAP

# --- ANA VERİ İŞLEME MOTORU (PIPELINE) ---

@st.cache_data(show_spinner="Veriler temizleniyor, /90 hesaplanıyor ve Lig Çarpanları uygulanıyor...")
def process_fm_data(file, min_minutes=300):
    """
    Ham CSV'yi alır, temizler, /90 metrikleri onarır ve Lig Çarpanı vurulmuş olarak hafızaya (cache) alır.
    """
    try:
        # 1. Veriyi Oku ve Temizle (Akıllı Ayırıcı Algılayıcı)
        # BİLGİ: Windows Bölge ayarlarına göre FM dosyaları virgül (,) veya noktalı virgül (;) ile ayrılabilir.
        try:
            # Önce noktalı virgül (European/Turkish standart) ile okumayı dener
            df = pd.read_csv(file, sep=';', encoding='utf-8')
            # Eğer yanlışlıkla tek bir sütun okuduysa (yani aslında virgülle ayrılmışsa), virgüle geri döner
            if len(df.columns) < 5:  
                file.seek(0)
                df = pd.read_csv(file, sep=',', encoding='utf-8')
        except Exception:
            # İşletim sistemi veya dosya encoding'i farklıysa UTF-8-SIG (FM HTML formatı) ile dener
            file.seek(0)
            df = pd.read_csv(file, sep=',', encoding='utf-8-sig')

        df.rename(columns=lambda x: str(x).strip(), inplace=True)
        
        # 2. Dakika Filtresi
        min_col = 'Mins' if 'Mins' in df.columns else 'Min' if 'Min' in df.columns else 'Minutes'
        if min_col in df.columns:
            # Boş veya hatalı dakika verilerini 0 yap, sayıya çevir
            df[min_col] = pd.to_numeric(df[min_col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            df = df[df[min_col] >= min_minutes]
            
        if df.empty:
            return pd.DataFrame()
            
        # 3. Lig Çarpanını Hesapla ve Sütun Olarak Ekle
        if 'Division' in df.columns:
            df['League_Weight'] = df['Division'].apply(_get_league_multiplier)
        else:
            df['League_Weight'] = 1.0

        # 4. Ham veriden /90 Eksiklerini Tamamla
        df = _calculate_per90_metrics(df, min_col)

        # 5. Lig Çarpanını Performans Metriklerine Uygula
        df = _apply_multipliers(df)

        return df

    except Exception as e:
        st.error(f"Kritik Veri Okuma Hatası: {e}")
        return pd.DataFrame()

def _get_league_multiplier(div_name):
    """config.py'daki listeye göre oyuncunun ligine ait katsayıyı bulur."""
    div = str(div_name).lower()
    for tier, data in LEAGUE_MAP.items():
        if any(kw in div for kw in data['keywords']):
            return data['multiplier']
    return LEAGUE_MAP["Other/Unknown"]["multiplier"]

def _calculate_per90_metrics(df, min_col):
    """CSV'de /90 verisi yoksa, ham veri ve dakikayı kullanarak otomatik üretir."""
    if min_col not in df.columns: return df
    
    # (Ham Veri Sütunu -> Dönüşecek Sütun)
    metrics_to_convert = {
        'Goals': 'Goals/90', 'Gls': 'Goals/90',
        'xG': 'xG/90', 'Shots': 'Shot/90',
        'xA': 'xA/90', 'Key Passes': 'KP/90',
        'Dribbles': 'Drb/90', 'Progressive Passes': 'Pr passes/90',
        'Asts': 'Asts/90', 'Assists': 'Asts/90'
    }
    
    for raw_col, per90_col in metrics_to_convert.items():
        if per90_col not in df.columns and raw_col in df.columns:
            raw_data = pd.to_numeric(df[raw_col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            mins_data = df[min_col].replace(0, 1) # Sıfıra bölünme hatasını engelle
            df[per90_col] = (raw_data / mins_data) * 90
            
    return df

def _apply_multipliers(df):
    """Lig çarpanını Age, Height, Weight ve Minutes dışındaki tüm sayısal verilere vurur."""
    exclude_cols = ['Age', 'Height', 'Weight', 'Mins', 'Min', 'Minutes', 'League_Weight']
    
    # Virgüllü sayıları noktaya çevirip numeric formata zorla
    for col in df.columns:
        if col not in exclude_cols and df[col].dtype == 'object':
            try:
                # Avrupa formatı olan '1,5' (1.5) gibi değerleri düzelt
                clean_str = df[col].astype(str).str.replace('%', '').str.replace(',', '.').str.replace('-', '0')
                df[col] = pd.to_numeric(clean_str, errors='ignore')
            except:
                continue

    # Çarpanı uygula (Performans verileri doğrudan güncellenir)
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in num_cols:
        if col not in exclude_cols:
            df[col] = df[col] * df['League_Weight']
            
    return df

# --- DİĞER MODÜLLERLE UYUM İÇİN YARDIMCI FONKSİYONLAR (CORE FUNCTIONS) ---

def get_val(row, metric):
    """
    CSV kolon adlarındaki boşluk, /, tire hatalarına karşı bağışıklık sağlayan veri çekici.
    Diğer tüm dosyalar (radarlar vb.) veriyi buradan okur.
    """
    if pd.isna(row).all(): return 0.0
    
    target = str(metric).lower().strip().replace(" ", "").replace("/", "").replace("%", "").replace("-", "")
    
    # FM26 İsimlendirme Varyasyonları (Eş Anlamlılar)
    synonyms = {
        "goals90": ["goalsper90minutes", "gls90", "goals90", "goals"],
        "tcka90": ["tcka", "tacklesattempted", "tcka90"],
        "tckr": ["tckr", "tackleswonratio", "tackleswon"],
        "pass": ["pas", "passaccuracy", "passing"],
        "dist90": ["distance90", "dist90"],
        "conversion": ["conversion", "conv"],
        "drb90": ["drb90", "dribbles90"],
        "shot90": ["shot90", "shots90"],
        "xg90": ["xg90"], "xa90": ["xa90"],
        "kp90": ["keypasses90", "kp90"],
        "asts90": ["ast90", "assists90"],
        "psa90": ["passesattempted90", "psa90"],
        "prpasses90": ["progressivepasses90", "prpasses90"],
        "posswon90": ["possessionwon90", "posswon90"],
        "int90": ["interceptions90", "int90"],
        "blk90": ["blocks90", "blk90"],
        "clr90": ["clearances90", "clr90"],
        "hdrsw90": ["headerswon90", "hdrsw90"],
        "aera90": ["aerialsattempted90", "aera90"],
        "hdr": ["headerwonratio", "hdr"],
        "xgprevented90": ["xgprevented90"],
        "goalsconceded90": ["goalsconceded90"],
        "posslost90": ["possessionlost90", "posslost90"],
        "opkp90": ["opkp90", "openplaykeypasses90"]
    }
    
    target_list = synonyms.get(target, [target])
    
    for col in row.index:
        col_clean = str(col).lower().strip().replace(" ", "").replace("/", "").replace("%", "").replace("-", "")
        if col_clean in target_list:
            try:
                return float(str(row[col]).replace(',', '.').replace('-', '0'))
            except: continue
            
    return 0.0

def get_player_group(pos):
    """Kısa FM pozisyonundan Mustermann Ana Grubunu döndürür."""
    pos = str(pos).upper()
    if 'GK' in pos: return "Goalkeepers"
    if any(x in pos for x in ['ST', 'AM (C)']): return "Attackers"
    if any(x in pos for x in ['D (', 'WB (', 'D/WB']): return "Defenders"
    return "Midfielders"

def get_all_player_groups(pos):
    """Bir oyuncunun oynayabildiği tüm Mustermann gruplarını liste olarak döner (Kıyaslama için)."""
    groups = []
    pos = str(pos).upper()
    if 'GK' in pos: groups.append("Goalkeepers")
    if any(x in pos for x in ['ST', 'AM (C)', 'AM (R)', 'AM (L)']): groups.append("Attackers")
    if any(x in pos for x in ['D (', 'WB (', 'D/WB']): groups.append("Defenders")
    if any(x in pos for x in ['DM', 'M (', 'AM (R)', 'AM (L)', 'M/AM']): groups.append("Midfielders")
    if not groups: groups.append("Midfielders") # Fallback
    return groups