import streamlit as st
import pandas as pd
import numpy as np

# Dataset
data = {
    'Alternatif': [
        'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8',
        'a9', 'a10', 'a11', 'a12', 'a13', 'a14', 'a15'
    ],
    'Kepadatan Penduduk': [
        32269, 25908, 9324, 16318, 32634, 9449, 14826, 
        26286, 8351, 9728, 25395, 8458, 6647, 4476, 3337
    ],
    'Jumlah Kasus Penyakit': [
        1504, 1045, 2173, 2547, 1427, 412, 594, 
        1069, 1561, 660, 2071, 2981, 3540, 1946, 2432
    ],
    'Jumlah Tenaga Kesehatan': [
        68, 81, 130, 138, 75, 35, 49, 
        57, 50, 70, 92, 99, 138, 129, 131
    ],
    'Jumlah Rumah Sakit': [
        1, 5, 3, 8, 3, 9, 3, 
        1, 2, 1, 1, 5, 1, 5, 5
    ],
    'Jumlah Puskesmas': [
        3, 2, 4, 4, 3, 1, 2, 
        2, 2, 2, 3, 5, 4, 5, 5
    ],
    'Jumlah Posyandu': [
        52, 60, 90, 122, 92, 32, 35, 
        55, 37, 13, 85, 81, 83, 108, 68
    ]
}

# DataFrame
df = pd.DataFrame(data)

# Sidebar untuk pengaturan input
st.sidebar.title("Pengaturan Input")
st.sidebar.subheader("Bobot dan Jenis Atribut")

# Input bobot dan atribut melalui sidebar
default_bobot_atribut = "25,benefit\n25,benefit\n20,benefit\n10,cost\n10,cost\n10,cost"
bobot_atribut = st.sidebar.text_area(
    "Masukkan bobot dan jenis atribut dalam format: bobot,atribut.",
    value=default_bobot_atribut,
    help="Pisahkan baris untuk setiap kriteria. Contoh: '25,benefit' artinya bobot 25 dan atribut benefit."
)

# Parsing input
try:
    input_lines = bobot_atribut.strip().split("\n")
    bobot = [int(line.split(",")[0]) for line in input_lines]
    atribut = [line.split(",")[1] for line in input_lines]
except:
    st.sidebar.error("Pastikan format input sesuai (contoh: '25,benefit') dan gunakan koma sebagai pemisah.")
    st.stop()

# Menyimpan progres ke dalam session_state
if 'progres' not in st.session_state:
    st.session_state.progres = 0  # Awal hanya tampil dataset

# Fungsi untuk mengupdate progres
def update_progres(step):
    st.session_state.progres = step

# Tombol reset
def reset():
    st.session_state.progres = 0  # Reset ke tampilkan dataset

# Tombol reset
if st.sidebar.button("Reset"):
    reset()

# Judul aplikasi
st.title("Sistem Pendukung Keputusan: TOPSIS")
st.write("Aplikasi ini menggunakan metode TOPSIS untuk membantu dalam pengambilan keputusan.")

# Selalu tampilkan dataset di atas
st.subheader("Dataset")
st.dataframe(df)

# Sidebar navigasi tanpa tombol "Proses ke Dataset"
sidebar_options = [
    ("Hasil Normalisasi SAW", 1),
    ("Normalisasi Matriks TOPSIS", 2),
    ("Matriks Keputusan Ternormalisasi Berbobot", 3),
    ("Menentukan Solusi Ideal Positif", 4),
    ("Menentukan Solusi Ideal Negatif", 5),
    ("Menghitung Jarak dari Solusi Ideal", 6),
    ("Menghitung Nilai Preferensi", 7),
    ("Menyusun Ranking", 8)
]

# Tombol navigasi sidebar
for label, step in sidebar_options:
    if st.sidebar.button(f"{label}", key=step):
        update_progres(step)

# Normalisasi matriks jika progres >= 1
if st.session_state.progres >= 1:
    matriks = df.iloc[:, 1:].values
    matriks_normalisasi = np.zeros(matriks.shape)

    for i in range(matriks.shape[1]):
        if atribut[i] == 'benefit':  # Kriteria benefit
            matriks_normalisasi[:, i] = matriks[:, i] / np.max(matriks[:, i])
        else:  # Kriteria cost
            matriks_normalisasi[:, i] = np.min(matriks[:, i]) / matriks[:, i]

    # DataFrame hasil normalisasi
    df_normalisasi = pd.DataFrame(
        matriks_normalisasi, 
        columns=df.columns[1:], 
        index=df['Alternatif']
    )

    # Menampilkan hasil normalisasi
    st.subheader("Hasil Normalisasi SAW")
    st.dataframe(df_normalisasi)

    # *Hasil Kuadrat SAW*
    hasil_kuadrat_saw = np.square(matriks_normalisasi)
    st.subheader("Hasil Kuadrat SAW")
    st.dataframe(pd.DataFrame(hasil_kuadrat_saw, columns=df.columns[1:], index=df['Alternatif']))

    # *Penjumlahan Kuadrat SAW per Kolom*
    penjumlahan_kuadrat_saw = np.sum(hasil_kuadrat_saw, axis=0)
    st.subheader("Penjumlahan hasil Kuadrat atribut per Kolom")
    st.write(penjumlahan_kuadrat_saw)

    # *Akar dari Penjumlahan Kuadrat SAW per Kolom*
    akar_penjumlahan_kuadrat = np.sqrt(penjumlahan_kuadrat_saw)
    st.subheader("Akar dari Penjumlahan Kuadrat SAW per Kolom")
    st.write(akar_penjumlahan_kuadrat)

# Normalisasi matriks TOPSIS jika progres >= 2
if st.session_state.progres >= 2:
    matriks_normalisasi_topsis = np.zeros(matriks_normalisasi.shape)

    for j in range(matriks_normalisasi.shape[1]):
        pembagi = np.sqrt(np.sum(matriks_normalisasi[:, j]**2))
        matriks_normalisasi_topsis[:, j] = matriks_normalisasi[:, j] / pembagi

    # DataFrame hasil normalisasi TOPSIS
    df_normalisasi_topsis = pd.DataFrame(
        matriks_normalisasi_topsis,
        columns=df.columns[1:],
        index=df['Alternatif']
    )

    # Menampilkan hasil normalisasi TOPSIS
    st.subheader("Normalisasi Matriks TOPSIS")
    st.dataframe(df_normalisasi_topsis)

# Matriks Keputusan Berbobot jika progres >= 3
if st.session_state.progres >= 3:
    bobot_total = np.sum(bobot)
    bobot_ternormalisasi = [b / bobot_total for b in bobot]

    # Menampilkan Bobot Ternormalisasi
    st.subheader("Bobot Ternormalisasi")
    df_bobot_ternormalisasi = pd.DataFrame(
        {'Kriteria': df.columns[1:], 'Bobot': bobot, 'Bobot Ternormalisasi': bobot_ternormalisasi}
    )
    st.dataframe(df_bobot_ternormalisasi)

    # Matriks Keputusan Berbobot
    matriks_berbobot = np.zeros(matriks_normalisasi_topsis.shape)

    for i in range(matriks.shape[1]):
        matriks_berbobot[:, i] = matriks_normalisasi_topsis[:, i] * bobot_ternormalisasi[i]

    df_matriks_berbobot = pd.DataFrame(
        matriks_berbobot,
        columns=df.columns[1:],
        index=df['Alternatif']
    )

    # Menampilkan matriks keputusan berbobot
    st.subheader("Matriks Keputusan Ternormalisasi Berbobot")
    st.dataframe(df_matriks_berbobot)

# Menentukan Solusi Ideal Positif (A+) jika progres >= 4
if st.session_state.progres >= 4:
    A_plus = np.zeros(matriks_berbobot.shape[1])

    # Menentukan solusi ideal positif (A+) untuk setiap kriteria
    for j in range(matriks_berbobot.shape[1]):
        if atribut[j] == 'benefit':
            A_plus[j] = np.max(matriks_berbobot[:, j])  # Solusi ideal positif untuk benefit
        else:
            A_plus[j] = np.min(matriks_berbobot[:, j])  # Solusi ideal positif untuk cost

    # Menampilkan solusi ideal positif
    st.subheader("Solusi Ideal Positif (A+)")
    st.write(A_plus)

# Menentukan Solusi Ideal Negatif (A-) jika progres >= 5
if st.session_state.progres >= 5:
    A_minus = np.zeros(matriks_berbobot.shape[1])

    # Menentukan solusi ideal negatif (A-) untuk setiap kriteria
    for j in range(matriks_berbobot.shape[1]):
        if atribut[j] == 'benefit':
            A_minus[j] = np.min(matriks_berbobot[:, j])  # Solusi ideal negatif untuk benefit
        else:
            A_minus[j] = np.max(matriks_berbobot[:, j])  # Solusi ideal negatif untuk cost

    # Menampilkan solusi ideal negatif
    st.subheader("Solusi Ideal Negatif (A-)")
    st.write(A_minus)

# Menghitung Jarak dari Solusi Ideal jika progres >= 6
if st.session_state.progres >= 6:
    jarak_A_plus = np.zeros(matriks_berbobot.shape[0])
    jarak_A_minus = np.zeros(matriks_berbobot.shape[0])

    for i in range(matriks_berbobot.shape[0]):
        jarak_A_plus[i] = np.sqrt(np.sum((matriks_berbobot[i, :] - A_plus)**2))
        jarak_A_minus[i] = np.sqrt(np.sum((matriks_berbobot[i, :] - A_minus)**2))

    # Menampilkan jarak dari solusi ideal positif dan negatif
    st.subheader("Jarak dari Solusi Ideal Positif (A+)")
    st.write(jarak_A_plus)

    st.subheader("Jarak dari Solusi Ideal Negatif (A-)")
    st.write(jarak_A_minus)

# Menghitung Nilai Preferensi jika progres >= 7
if st.session_state.progres >= 7:
    nilai_preferensi = jarak_A_minus / (jarak_A_plus + jarak_A_minus)

    st.subheader("Nilai Preferensi")
    st.write(nilai_preferensi)

# Menyusun Ranking jika progres >= 8
if st.session_state.progres >= 8:
    ranking = np.argsort(nilai_preferensi)[::-1]  # Ranking berdasarkan nilai preferensi terbesar
    ranked_preferensi = nilai_preferensi[ranking]  # Preferensi diurutkan sesuai ranking
    alternatif_sorted = df['Alternatif'].iloc[ranking]  # Alternatif diurutkan sesuai ranking

    st.subheader("Ranking Alternatif")
    df_ranking = pd.DataFrame({
        'Alternatif': alternatif_sorted.values,
        'Nilai Preferensi': ranked_preferensi,
        'Ranking': np.arange(1, len(nilai_preferensi) + 1)
    })

    st.dataframe(df_ranking)
