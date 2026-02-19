# !/bin/bash

# Usage:
# ./generate_test_wavs.sh /path/to/target/folder

# Prüfe, ob ein Zielordner übergeben wurde
if [ "$#" -ne 1 ]; then
    echo "Verwendung: $0 /path/to/target/folder"
    exit 1
fi

target_folder="$1"

# Erstelle den Zielordner, falls er nicht existiert
mkdir -p "$target_folder"

# Startzeit: 000000 (00:00:00)
start_hour=0
start_minute=0
# Anzahl der Dateien
count=100
# Minuten pro Datei
duration_minutes=1
# Zeitschritt zwischen Dateien (in Minuten)
time_step_minutes=10

# Schleife für 100 Dateien
for ((i=0; i<$count; i++)); do
    # Gesamtminuten berechnen
    total_minutes=$((start_minute + i * time_step_minutes))

    # Stunden und Minuten berechnen
    hours=$((start_hour + total_minutes / 60))
    minutes=$((total_minutes % 60))

    # Zeitstempel im Format HHMMSS
    timestamp=$(printf "%02d%02d00" "$hours" "$minutes")

    # Dateiname generieren
    filename="${target_folder}/TEST_20260219_${timestamp}.wav"

    # 1 Minute Stille generieren (44100 Hz, 16 Bit, Stereo)
    sox -n -r 44100 -b 16 -c 2 "$filename" trim 00:00:00 00:01:00

    echo "Erstellt: $filename"
done
