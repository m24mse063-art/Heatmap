import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Heatmap Explorer", layout="wide")
st.title("Heatmap Explorer")

# Find CSV files in the repo
csv_paths = sorted([p for p in Path(".").glob("**/*.csv") if p.is_file() and ".git" not in str(p)])
if not csv_paths:
    st.warning("No CSV files found in the repository. Add CSVs or change path.")
    st.stop()

csv_names = [str(p) for p in csv_paths]
selected = st.selectbox("Choose a CSV file", csv_names)

if selected:
    try:
        df = pd.read_csv(selected)
    except Exception as e:
        st.error(f"Failed to read {selected}: {e}")
        st.stop()

    st.write("Preview (first 100 rows):")
    st.dataframe(df.head(100))

    # auto-detect numeric columns
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not num_cols:
        st.info("No numeric columns found for a correlation heatmap.")
    else:
        cols = st.multiselect("Columns to include in heatmap (choose 2+)", num_cols, default=num_cols[:6])
        if len(cols) >= 2:
            corr = df[cols].corr()
            fig = px.imshow(
                corr,
                text_auto=True,
                color_continuous_scale="RdBu_r",
                aspect="auto",
                title=f"Correlation heatmap — {Path(selected).name}",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Select at least two numeric columns to display the heatmap.")

    st.download_button("Download CSV", df.to_csv(index=False), file_name=Path(selected).name)
