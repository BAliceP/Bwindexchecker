# 🧬 NGS Barcode Clash Checker

A Streamlit app to detect conflicts and clashes between different sets of next-generation sequencing (NGS) index barcodes.

## Features

- **Single Set Analysis**: Check for clashes within a single barcode set
- **Multi-Set Comparison**: Compare barcodes between two different index sets
- **File Upload**: Analyze barcodes from CSV or TXT files
- **Hamming Distance Detection**: Identifies barcodes that differ by a specified number of positions
- **CSV Export**: Download clash reports for further analysis

## How It Works

The app uses **Hamming distance** to detect barcode clashes:
- Barcodes within the specified distance threshold are flagged as potential clashes
- Helps prevent cross-contamination in multiplexed NGS experiments
- Supports standard DNA bases (A, C, G, T)

## Installation

1. Install the requirements

   ```bash
   pip install -r requirements.txt
   ```

2. Run the app

   ```bash
   streamlit run streamlit_app.py
   ```

## Usage

### Single Set Check
Enter barcodes from one index set to identify internal conflicts.

### Multi-Set Comparison
Compare barcodes between two different index sets to find potential cross-contamination risks.

### Upload Files
Upload CSV or TXT files containing barcode sequences for batch analysis.

### Configuration
Use the sidebar to adjust the maximum Hamming distance threshold for clash detection (0-10).

## Input Format

- One barcode per line
- Valid DNA bases: A, C, G, T (case-insensitive)
- Duplicates are automatically removed
- Invalid sequences are skipped with a warning
