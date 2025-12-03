import streamlit as st
import pandas as pd
from itertools import combinations
import io

st.set_page_config(page_title="NGS Barcode Clash Checker", layout="wide")

st.title("🧬 NGS Barcode Clash Checker")
st.write(
    "Check for conflicts and clashes between different sets of next-generation sequencing index barcodes."
)

# Sidebar for configuration
st.sidebar.header("Configuration")
max_mismatch = st.sidebar.number_input(
    "Maximum Hamming distance to consider as clash:",
    min_value=0,
    max_value=10,
    value=1,
    help="Barcodes within this Hamming distance are considered clashing"
)

def hamming_distance(s1, s2):
    """Calculate Hamming distance between two strings of equal length"""
    if len(s1) != len(s2):
        return float('inf')
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def check_barcodes_within_set(barcodes, max_distance):
    """Check for clashes within a single barcode set"""
    clashes = []
    barcode_list = list(set(barcodes))  # Remove duplicates
    
    for bc1, bc2 in combinations(barcode_list, 2):
        distance = hamming_distance(bc1, bc2)
        if distance <= max_distance:
            clashes.append({
                'Barcode 1': bc1,
                'Barcode 2': bc2,
                'Hamming Distance': distance
            })
    
    return clashes, barcode_list

def check_barcodes_between_sets(set1, set2, max_distance, set1_name="Set 1", set2_name="Set 2"):
    """Check for clashes between two barcode sets"""
    clashes = []
    
    for bc1 in set1:
        for bc2 in set2:
            distance = hamming_distance(bc1, bc2)
            if distance <= max_distance:
                clashes.append({
                    f'{set1_name} Barcode': bc1,
                    f'{set2_name} Barcode': bc2,
                    'Hamming Distance': distance
                })
    
    return clashes

def validate_barcodes(barcodes):
    """Validate that barcodes are valid DNA sequences"""
    valid = []
    invalid = []
    
    for bc in barcodes:
        bc_clean = bc.strip().upper()
        if bc_clean and all(c in 'ACGT' for c in bc_clean):
            valid.append(bc_clean)
        else:
            invalid.append(bc)
    
    return valid, invalid

# Main interface tabs
tab1, tab2, tab3 = st.tabs(["Single Set Check", "Multi-Set Comparison", "Upload Files"])

with tab1:
    st.header("Check for clashes within a single barcode set")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        barcode_input = st.text_area(
            "Enter barcodes (one per line):",
            height=200,
            placeholder="ACGTACGT\nTGCATGCA\nACGTTGCA\n..."
        )
    
    with col2:
        st.write("**Input Format:**")
        st.info("- One barcode per line\n- Valid DNA bases: A, C, G, T\n- Case-insensitive\n- Duplicates will be removed")
    
    if st.button("Check for Clashes", key="single_set"):
        if barcode_input.strip():
            barcodes = [bc.strip() for bc in barcode_input.split('\n') if bc.strip()]
            valid_barcodes, invalid_barcodes = validate_barcodes(barcodes)
            
            if invalid_barcodes:
                st.warning(f"⚠️ Invalid barcodes (skipped): {', '.join(invalid_barcodes[:5])}")
            
            if valid_barcodes:
                clashes, unique_barcodes = check_barcodes_within_set(valid_barcodes, max_mismatch)
                
                st.write(f"**Total unique barcodes:** {len(unique_barcodes)}")
                
                if clashes:
                    st.warning(f"⚠️ Found {len(clashes)} potential clashes:")
                    df_clashes = pd.DataFrame(clashes)
                    st.dataframe(df_clashes, use_container_width=True)
                    
                    # Download option
                    csv = df_clashes.to_csv(index=False)
                    st.download_button(
                        label="Download clashes as CSV",
                        data=csv,
                        file_name="barcode_clashes.csv",
                        mime="text/csv"
                    )
                else:
                    st.success("✅ No clashes found within this barcode set!")
            else:
                st.error("No valid barcodes to check")
        else:
            st.warning("Please enter at least one barcode")

with tab2:
    st.header("Compare multiple barcode sets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Set 1:**")
        set1_name = st.text_input("Set 1 name:", value="Set 1")
        set1_input = st.text_area(
            "Enter barcodes for Set 1 (one per line):",
            height=150,
            key="set1",
            placeholder="ACGTACGT\nTGCATGCA\n..."
        )
    
    with col2:
        st.write("**Set 2:**")
        set2_name = st.text_input("Set 2 name:", value="Set 2")
        set2_input = st.text_area(
            "Enter barcodes for Set 2 (one per line):",
            height=150,
            key="set2",
            placeholder="ACGTACGT\nGGGGGGGG\n..."
        )
    
    if st.button("Compare Sets", key="compare_sets"):
        set1 = [bc.strip().upper() for bc in set1_input.split('\n') if bc.strip()]
        set2 = [bc.strip().upper() for bc in set2_input.split('\n') if bc.strip()]
        
        set1_valid, set1_invalid = validate_barcodes(set1)
        set2_valid, set2_invalid = validate_barcodes(set2)
        
        if set1_invalid:
            st.warning(f"⚠️ Invalid barcodes in Set 1: {', '.join(set1_invalid[:3])}")
        if set2_invalid:
            st.warning(f"⚠️ Invalid barcodes in Set 2: {', '.join(set2_invalid[:3])}")
        
        if set1_valid and set2_valid:
            clashes = check_barcodes_between_sets(set1_valid, set2_valid, max_mismatch, set1_name, set2_name)
            
            st.write(f"**Set 1 unique barcodes:** {len(set(set1_valid))}")
            st.write(f"**Set 2 unique barcodes:** {len(set(set2_valid))}")
            
            if clashes:
                st.warning(f"⚠️ Found {len(clashes)} potential clashes between sets:")
                df_clashes = pd.DataFrame(clashes)
                st.dataframe(df_clashes, use_container_width=True)
                
                csv = df_clashes.to_csv(index=False)
                st.download_button(
                    label="Download clashes as CSV",
                    data=csv,
                    file_name="cross_set_clashes.csv",
                    mime="text/csv"
                )
            else:
                st.success("✅ No clashes found between these barcode sets!")
        else:
            st.error("Please provide valid barcodes for both sets")

with tab3:
    st.header("Upload barcode files")
    
    uploaded_file = st.file_uploader(
        "Upload a CSV or TXT file with barcodes",
        type=['csv', 'txt'],
        help="Format: One barcode per line (for TXT) or in a column (for CSV)"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.txt'):
                barcodes = [line.decode('utf-8').strip() for line in uploaded_file if line.strip()]
            else:  # CSV
                df = pd.read_csv(uploaded_file)
                # Assume first column contains barcodes
                barcodes = df.iloc[:, 0].astype(str).tolist()
            
            valid_barcodes, invalid_barcodes = validate_barcodes(barcodes)
            
            st.write(f"**Total barcodes read:** {len(barcodes)}")
            st.write(f"**Valid barcodes:** {len(valid_barcodes)}")
            
            if invalid_barcodes:
                st.warning(f"**Invalid barcodes:** {len(invalid_barcodes)}")
            
            if st.button("Analyze Uploaded Barcodes"):
                clashes, unique_barcodes = check_barcodes_within_set(valid_barcodes, max_mismatch)
                
                st.write(f"**Unique barcodes:** {len(unique_barcodes)}")
                
                if clashes:
                    st.warning(f"⚠️ Found {len(clashes)} potential clashes:")
                    df_clashes = pd.DataFrame(clashes)
                    st.dataframe(df_clashes, use_container_width=True)
                    
                    csv = df_clashes.to_csv(index=False)
                    st.download_button(
                        label="Download clashes as CSV",
                        data=csv,
                        file_name="uploaded_clashes.csv",
                        mime="text/csv"
                    )
                else:
                    st.success("✅ No clashes found!")
        
        except Exception as e:
            st.error(f"Error reading file: {e}")

# Footer
st.divider()
st.markdown("""
**About this tool:**
- Detects barcode clashes using Hamming distance (number of differing positions)
- Useful for NGS experiments to avoid cross-contamination
- Supports DNA barcodes (A, C, G, T bases)
""")
