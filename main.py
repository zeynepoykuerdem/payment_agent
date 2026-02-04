# streamlit desktop app that controls,
# rent,rundfunkt fees, and other payments

import streamlit as st
import pandas as pd
import datetime as dt
import openai as ai
import json
import os
import gspread
from google.oauth2.service_account import Credentials


scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

sheet_rundfunkt= client.open("rundfunkt_payments").sheet1
sheet_vodafone= client.open("vodafone_payments").sheet1

client = ai.Client(api_key=os.getenv("OPENAPI_KEY"))

def talk_to_agent(chat_input):
    system_prompt= """ You are a helpful payment management assistant. 
             Extract the person's name, paymment category (  Rundfunkt, Vodafone).
             The Rundfunkt fee is always 2.70 euros per person.(Nihal, Li, Mehru, Alexia,Yazan. and Lennart)
             Vodafone fee is 64.90 euros per month.(For WIFI, this is only related to Frau Horlacher).
             Return JSON: {"name": "string", "category": "Rundfunk/Vodafone", 
             "month":"string,"valid": true} """
    response= ai.chat.completions.create(
        model="gpt-4o",
        message=[
            {"role":"system","content":system_prompt},
            {"role":"user","content":chat_input}
        ,
        ],
        response_format={"type":"json_object"}
    )
    return json.loads(response.choices[0].message.content)

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
        month= result["month"].capitalize()

        if category == "Rundfunkt" :
         
         try:
            cell=sheet_rundfunkt.find(name)
            sheet_rundfunkt.update_cell(cell.row,2,"Ödendi")
            
            st.success(f"Updated for {name}!")
        
         except :
            st.error(f"Hata {name} could not found")

        else :
           try: 
            cell=sheet_vodafone.find(month)
            sheet_vodafone.update_cell(cell.row,2,"Ödendi")
            
            st.success(f"Updated for {month}!")
           except :
              st.error(f"Hata:{month} could not found")
              
    st.rerun()         


        

else:
    st.warning("I could not figure it out whic fiule to update")
        










