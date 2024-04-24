# Import convention
import streamlit as st
import sys
import os
sys.path.insert(1, '.'+ os.sep)
import benchmark_dataset_creator as bc

st.set_page_config(
    page_title='Benchmark Dataset Creator',
)
st.title('Benchmark Dataset Creator')

# Add image
#print(os.path.exists('.'+os.sep+ os.path.join('docs', 'illustrations', '‎method_schematicV2.png')))
#st.image('.' + os.sep + os.path.join('docs', 'illustrations', '‎method_schematicV2.png'),
#         channels="RGB", output_format="auto")

st.write('Welcome to the Benchmark Dataset Creator')