# streamlit desktop app that controls,
# rent,rundfunkt fees, and other payments

import streamlit as st
import pandas as pd
import datetime as dt
import google.generativeai as genai
import json
import gspread
from google.oauth2.service_account import Credentials


scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client_googlesheets= gspread.authorize(creds)

sheet_rundfunkt= client_googlesheets.open("rundfunkt_payments").sheet1
sheet_vodafone= client_googlesheets.open("vodafone_payments").sheet1

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
client_ai = genai.GenerativeModel("gemini-2.5-flash")

def talk_to_agent(chat_input):
    system_prompt= f""" 
    
    
    You are a helpful payment management assistant. 

    Extract:
    -the person's name, 
    -paymment category (Rundfunk, Vodafone).
    -month (if Vodafone)

    Rules:
    - Vodafone is ONLY related to Frau Horlacher
             
    Return JSON format : 
    {{"name": "string",
      "category": "Rundfunk/Vodafone", 
      "month": "string", 
      "valid": true
      
      }}

      User input: {chat_input}
               """
    response= client_ai.generate_content(
       system_prompt,
       generation_config={
          "temperature": 0,
          "response_mime_type":"application/json"
       }
    )
    return json.loads(response.text)
st.set_page_config(page_title="Payment Management App", layout="wide")
st.title("Payment Management App")

col1,col2=st.columns(2)
with col1:
   st.subheader("Rundfunk Table")
   df_r= pd.DataFrame(sheet_rundfunkt.get_all_records())
   st.dataframe(df_r)

with col2:
   st.subheader("Vodafone Table")
   df_v= pd.DataFrame(sheet_vodafone.get_all_records())
   st.dataframe(df_v)

user_input= st.chat_input("What happened ?")

if user_input:
    result= talk_to_agent(user_input)

    if result["valid"]:
        name= result["name"].capitalize()
        category= result["category"]
        

        if "Rundfunk" in category :
         
         try:
            cell=sheet_rundfunkt.find(name,in_column=1)
            cell_status= sheet_rundfunkt.cell(cell.row,2).value
            if cell_status == "Ödendi":
               st.info(f"{name} is already marked as Ödendi")
               st.stop()
    
            sheet_rundfunkt.update_cell(cell.row,2,"Ödendi")
            st.rerun()
            st.success(f"Updated Rundfunk Table for {name}!")
          
         except :
            st.error(f"Hata {name} could not found")
            st.stop()

        elif "Vodafone" in category :
           month= result["month"].capitalize()
           try: 
            cell=sheet_vodafone.find(month,in_column=1)
            sheet_vodafone.update_cell(cell.row,2,"Ödendi")
            st.rerun()
            st.success(f"Updated Vodafone Table for {month}!")
  
           except :
              st.error(f"Hata:{month} could not found")
              st.stop()
              
    if not result["valid"]:
       st.warning("I could not figure it out which table to update")
       st.stop()
                     


    
        










