# Import convention
import streamlit as st
import sys
import os
sys.path.insert(1, '.'+ os.sep)

st.set_page_config(
    page_title='Benchmark Dataset Creator',
)
st.title('Benchmark Dataset Creator')

# Add image
#print(os.path.exists('.'+os.sep+ os.path.join('docs', 'illustrations', '‎method_schematicV2.png')))
#st.image('.' + os.sep + os.path.join('docs', 'illustrations', '‎method_schematicV2.png'),
#         channels="RGB", output_format="auto")

st.write('Welcome to the Benchmark Dataset Creator')

link_to_metadata = "pages" + os.sep + "1_Project_creator.py"
st.page_link(link_to_metadata, label=":green[Start with Project Creator]", icon="➡️")