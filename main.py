import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET

def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root

def xml_to_df(root):
    data = []
    for element in root:
        row = {}
        for subelement in element:
            row[subelement.tag] = subelement.text
        data.append(row)
    df = pd.DataFrame(data)
    return df

st.set_page_config("Ledger to Tally Prime XML", layout="wide")
# INPUTS
st.sidebar.title("Ledger to Tally Prime XML")
ledger = st.sidebar.file_uploader("Upload Ledger Contract Note", type=["xlsx"])
col1, col2 = st.columns(2)
date = col1.date_input("Select Date")
output_type = col2.radio("Select output type", options=["Business", "Investment"])

# Read uploaded xlsx file
if ledger is not None:
    text_contents = '''This is some text'''
    st.download_button('Download Tally XML', text_contents, use_container_width=True)
    df = pd.read_excel(ledger, sheet_name='Sheet1', header=None)
    st.write(df)
    #xml = df.to_xml()
    #st.download_button('Download Tally XML', xml, 'download.csv', 'text/csv')

st.sidebar.subheader("XML Testing")
xml_file = st.sidebar.file_uploader("Upload Exported Tally XML", type=["xml"])

# Read uploaded xml file
if xml_file is not None:
    xml_file_read = parse_xml(xml_file)
    df = xml_to_df(xml_file_read)
    # Testing XML
    c1, c2 = st.columns(2)
    new_df1 = df[df.iloc[:,0].notna()]
    new_df2 = df[df.iloc[:,1].notna()]
    c2.write(new_df1)
    c1.write(new_df2)