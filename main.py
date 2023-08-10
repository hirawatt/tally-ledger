import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
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

# TODO: add data validation logic
def data_validation():
    return True

st.set_page_config("Ledger to Tally Prime XML", "📒", "wide")
st.sidebar.title("Ledger to Tally Prime XML")
# INPUTS
col1, col2 = st.columns(2)
date = col1.date_input("Select Date")
output_type = col2.radio("Select output type", options=["Business", "Investment"])

st.info("Testing")
ledger = st.sidebar.file_uploader("Upload Ledger Contract Note", type=["xlsx"])
# Read uploaded xlsx file
if ledger is not None:
    df = pd.read_excel(ledger, sheet_name='Sheet1', header=None)
    st.dataframe(df, use_container_width=True)

    # TODO: Extracting values form Excel
    # FIXME: simplify logic
    col1_value = df[0].str.startswith("Total")
    for i in col1_value:
        if i == True:
            total_index = col1_value.tolist().index(True)
    
    df_subset = df.iloc[(total_index+6):]
    st.write(df_subset)
    date1 = df_subset.iloc[0][0].strftime('%d-%b-%y')
    tick1 = df_subset.iloc[0][4]
    print("First Data: ", date1, tick1)


st.sidebar.info("XML Testing")
xml_file = st.sidebar.file_uploader("Upload Exported Tally XML", type=["xml"])
# Read uploaded xml file
if xml_file is not None:
    xml_file_read = parse_xml(xml_file)
    df = xml_to_df(xml_file_read)
    c1, c2 = st.columns(2)
    new_df1 = df[df.iloc[:,0].notna()]
    new_df2 = df[df.iloc[:,1].notna()]
    c2.write(new_df1)
    c1.write(new_df2)

# FIXME: Testing - remove when complete
with open('data-new/nse_janmangal.xml', 'rb') as file1:
#with open('output/sample3.xml', 'rb') as file1:
    f1 = file1.read()
    f1_str = f1.decode('utf-16')
    #f1_str = f1.decode('utf-8')

# Create XML file
doc, tag, text, line = Doc().ttl()

def create_xml_from_ledger():
    doc.asis('<!--HirawatTech watermark-->')
    with tag('ENVELOPE'):
        # 12 entries for each trade
        # TODO: add date/year from excel
        line('DSPVCHDATE', f'{date1}')
        line('DSPVCHLEDACCOUNT', f'{tick1}')
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
        # FIXME: add number of entries logic
        no_of_entries = 3
        for i in range(0, no_of_entries):
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
    return indent(doc.getvalue())

data_valid = data_validation()
if data_valid:
    f2_str = create_xml_from_ledger()
    #f2_str = indent(doc.getvalue())
    st.download_button('Download Tally XML', f2_str, 'download.xml', 'application/xml', use_container_width=True)
else:
    st.warning(data_valid)

# Display comparison
co1, co2 = st.columns(2)
co1.code(f1_str, language="xml")
co2.code(f2_str, language="xml")