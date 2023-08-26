import streamlit as st

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd

st.set_page_config(
    page_title="JOB Searching",
    page_icon=":magnifying_glass_tilted_left:",
    layout="wide",
)

uri = "mongodb+srv://jegadeesh:Sara.1974@cluster0.corvt.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi("1"))
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
    db = client["Hackathon"]
    collection1 = db["Company"]
    collection2=db["People"]

except Exception as e:
    print(e)


#tab1, tab2 = st.tabs(["Candidates Recommendation For Your Job Profile"])


#with tab1:

unique_companies = collection1.distinct("company_name")


unique_companies_set = set(unique_companies)
option = st.selectbox(
'Select the Company',
unique_companies_set)
opening=st.text_input("Select the maximum number of openings")

if option and opening :
    query={"company_name":option}
    res1=collection1.find_one(query)
    required_skills=res1['openings']['skills']

    applied_candidates = res1.get("openings", {}).get("applied_candidates", [])
    matching_documents = list(collection2.find({"personal_id": {"$in": applied_candidates}}))
    if len(matching_documents)==0:
        st.write("Candidates are yet to apply for this Role!")
    else:
        res={}
        st.write("The Profile of Applied Candidates")
        st.json(matching_documents)
        st.write("\n")
        for i in matching_documents:
            
            st.write(f"{i['name']} Applied to this Role")
        
        st.write("\n")
        

        for doc in matching_documents:

            v1 = [sentence.lower() for sentence in doc["Skills"]]
            skill_set=set(v1)
            print(v1)


            jd_set = set( [string.lower() for string in required_skills])
            print(jd_set)
            intersection = float(len(jd_set.intersection(skill_set)))
            union = float( len(jd_set.union(skill_set)))

            if union == 0:
                similarity=0

            similarity = float(intersection / union)
            res[doc["name"]] = similarity

        print(res)
        sorted_keys = sorted(res, key=lambda k: res[k], reverse=True)[:int(opening)]
        count=0
        for i in sorted_keys:
            resf=collection2.find_one({"name":i})
            if(res[resf['name']]==0):
                continue
            count+=1
            
            st.write(f"{resf['name']} with an experience of {resf['Experience']} years is a suitable match for this Role with a Score of {res[resf['name']]}")
        
        if(count==0):
            st.write("No candidate applied for this role is a perfect fit")



