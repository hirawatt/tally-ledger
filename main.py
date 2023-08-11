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
    #st.dataframe(df, use_container_width=True)

    # Extracting values form Excel
    # FIXME: simplify logic
    col1_value = df[0].str.startswith("Total")
    for i in col1_value:
        if i == True:
            total_index = col1_value.tolist().index(True)
    
    df_subset = df.iloc[(total_index+6):]
    #st.write(df_subset)
    # Column 1 of excel sheet
    df_subset_c1 = df_subset.loc[:, 1].dropna()
    df_subset_c4 = df_subset.loc[:, 4].dropna()
    #st.write(df_subset_c1)
    st.write(df_subset_c4)
    # journal entry
    df_subset_c1_j = df_subset_c1[df_subset_c1.str.startswith("J")]
    df_journal = df.iloc[df_subset_c1_j.index]
    st.write(df_journal)
    # bank entry
    df_subset_c1_b = df_subset_c1[df_subset_c1.str.startswith("B")]
    df_bank = df.iloc[df_subset_c1_b.index]
    st.write(df_bank)
    # trades entry
    df_subset_c1_date = df_subset_c1[df_subset_c1.str.contains("/")]
    df_trades = df.iloc[df_subset_c1_date.index]
    st.write(df_trades)
    # FIXME: edge case: 2 trades with summed up charges | trades entry alternative
    df_subset_c4_trades = df_subset_c4[df_subset_c4.str.contains("Dl", case=True)]
    st.write(df.iloc[df_subset_c4_trades.index])

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

def create_xml_from_ledger():
    # Create XML file
    doc, tag, text, line = Doc().ttl()
    doc.asis('<!--HirawatTech watermark-->')
    with tag('ENVELOPE'):
        # 12 Tally XML entries for bank entry
        doc.asis('<!--Bank Entry-->')
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
        doc.asis('<!--Trades Entry-->')
        # FIXME: add number of entries logic
        print("test")
        no_of_trades = df_trades.shape[0]
        for i in range(0, no_of_trades):
            # Business/Investment logic
            if output_type == "Business":
                # Sale/Purchase of shares logic
                if df_trades[6].iloc[i] > 0:
                    line('DSPVCHEXPLACCOUNT', 'Purchase of Shares')
                else:
                    line('DSPVCHEXPLACCOUNT', 'Sale of Shares')
            elif output_type == "Investment":
                line('DSPVCHEXPLACCOUNT', 'Invetment in Shares')
            # TODO: add for loop based on number of excel entries
            with tag('DSPVCHEXPLVALUE'):
                line('DSPVCHEXPLDRAMTEXCELEXPORT', '10')
                line('DSPVCHEXPLCRAMTEXCELEXPORT', '')
    return indent(doc.getvalue())

data_valid = data_validation()
if data_valid:
    f2_str = create_xml_from_ledger()
    st.download_button('Download Tally XML', f2_str, 'download.xml', 'application/xml', use_container_width=True)
    # Display comparison
    co1, co2 = st.columns(2)
    co1.code(f1_str, language="xml")
    co2.code(f2_str, language="xml")
else:
    st.warning(data_valid)