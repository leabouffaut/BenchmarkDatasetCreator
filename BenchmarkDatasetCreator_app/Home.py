# Import convention
import streamlit as st
import sys
import os
sys.path.insert(1, '.'+ os.sep)
import benchmark_dataset_creator as bc

st.set_page_config(
    page_title='Benchmark Dataset Creator',
    #page_icon="👋",
)
st.title('Benchmark Dataset Creator')

# Add image
st.image('.'+os.sep+ os.path.join('docs','illustrations', '‎method_schematicV2.png'), caption=None, width=None, use_column_width=True, clamp=False,
         channels="RGB", output_format="auto")
