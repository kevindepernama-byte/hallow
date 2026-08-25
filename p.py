import sqlite3
import os
import glob

def pecah_database(source_db, prefix_target, jumlah_pecahan=2):
    if not os.path.exists(source_db):
        print(f"[-] File {source_db} tidak ditemukan, dilewati.")
        return

    conn_src = sqlite3.connect(source_db)
    cursor_src = conn_src.cursor()

    cursor_src.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor_src.fetchall() if row[0] != "sqlite_sequence"]

    for table in tables:
        cursor_src.execute(f"SELECT * FROM `{table}`")
        rows = cursor_src.fetchall()
        
        if not rows:
            print(f"[-] Tabel {table} di {source_db} kosong, dilewati.")
            continue

        cursor_src.execute(f"PRAGMA table_info(`{table}`)")
        cols = [f"`{col[1]}` {col[2]}" for col in cursor_src.fetchall()]
        cols_def = ", ".join(cols)

        # Hitung pembagian data per pecahan
        total_rows = len(rows)
        chunk_size = (total_rows + jumlah_pecahan - 1) // jumlah_pecahan
        placeholders = ", ".join(["?" for _ in range(len(rows[0]))])

        for i in range(jumlah_pecahan):
            start = i * chunk_size
            end = start + chunk_size
            chunk_data = rows[start:end]

            if not chunk_data:
                continue

            target_db = f"db/{prefix_target}{i+1}.db"
            
            # Buat/sambung ke database pecahan baru
            conn_target = sqlite3.connect(target_db)
            cur_target = conn_target.cursor()
            cur_target.execute(f"CREATE TABLE IF NOT EXISTS `{table}` ({cols_def})")
            cur_target.executemany(f"INSERT INTO `{table}` VALUES ({placeholders})", chunk_data)
            conn_target.commit()
            conn_target.close()

            print(f"[+] Berhasil mengisi {target_db} dengan {len(chunk_data)} baris dari {source_db}")

    conn_src.close()

# Eksekusi pemecahan untuk nikindo1 sampai nikindo5
# Contoh: nikindo1.db dipecah jadi 2 bagian (nikindo11.db, nikindo12.db)
# Kamu bisa atur jumlah pecahan sesuai kebutuhan ukuran file-nya
for i in range(1, 6):
    src = f"db/nikindo{i}.db"
    # Misal prefix target jadi nikindo11, nikindo12 (untuk file 1), dst.
    # Format nama: prefix angka asli + urutan pecahan (contoh: nikindo11, nikindo12)
    if os.path.exists(src):
        print(f"\nMulai memecah {src}...")
        # Kita pecah jadi 2 bagian per file (ubah angka 2 jika ingin lebih banyak pecahan)
        pecah_database(src, f"nikindo{i}", jumlah_pecahan=2)

print("\nSemua proses pemecahan database Nikindo selesai!")

