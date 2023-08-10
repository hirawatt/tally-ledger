import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from yattag import Doc, indent

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

st.set_page_config("Ledger to Tally Prime XML", "📒", "wide")
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
    st.dataframe(df, use_container_width=True)
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

# Testing
with open('data-new/nse_janmangal.xml', 'rb') as file1:
    f1 = file1.read()
    f1_str = f1.decode('utf-16')

# Create XML file
doc, tag, text, line = Doc().ttl()

with tag('ENVELOPE'):
    # 12 entries for each trade
    # TODO: add date/year from excel
    line('DSPVCHDATE', '7-Jul-23')
    line('DSPVCHLEDACCOUNT', 'Stock')
    line('NAMEFIELD', '')
    line('INFOFIELD', '')
    line('INDDEVDCREATDBY', '')
    line('INDDEVDCREATTIME', '')
    line('INDDEVDCHKBY', '')
    line('INDDEVDATEBY', '')
    line('DSPVCHTYPE', 'placeholder')
    line('DSPVCHDRAMT', '')
    line('DSPVCHCRAMT', 'placeholder')
    line('DSPEXPLVCHNUMBER', 'placeholder')
    doc.asis('<!--testing-->')
    # business/investment logic
    if output_type == "Business":
        # TODO: add Sale/Purchase logic
        line('DSPVCHEXPLACCOUNT', 'Sale of Shares')
    elif output_type == "Invetment":
        line('DSPVCHEXPLACCOUNT', 'Invetment in Shares')
    # TODO: add for loop based on number of excel entries
    with tag('DSPVCHEXPLVALUE'):
        line('DSPVCHEXPLDRAMTEXCELEXPORT', '10')
        line('DSPVCHEXPLCRAMTEXCELEXPORT', '')

f2_str = indent(doc.getvalue())

# Display comparison
co1, co2, co3 = st.columns(3)
co1.code(f1_str, language="xml")
co2.code(f2_str, language="xml")