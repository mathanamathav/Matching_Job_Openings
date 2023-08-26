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
    collection = db["Company"]

except Exception as e:
    print(e)

tab1, tab2 = st.tabs(["Jobs Recommendation For Your Profile", "Enter Your Skill Set"])

skills_list = [
    "Python",
    "Java",
    "C++",
    "JavaScript",
    "Ruby",
    "PHP",
    "Swift",
    "Kotlin",
    "C#",
    "Go",
    "HTML",
    "CSS",
    "React",
    "Angular",
    "Vue.js",
    "Node.js",
    "Express.js",
    "Django",
    "Flask",
    "iOS Development",
    "Android Development",
    "Flutter",
    "Xamarin",
    "React Native",
    "Machine Learning",
    "Data Analysis",
    "Data Visualization",
    "SQL",
    "R",
    "MATLAB",
    "AWS",
    "Azure",
    "Google Cloud Platform",
    "Docker",
    "Kubernetes",
    "CI/CD",
    "User Interface Design",
    "User Experience Design",
    "Adobe XD",
    "Sketch",
    "Figma",
    "Adobe Photoshop",
    "Adobe Illustrator",
    "CorelDRAW",
    "InDesign",
    "Writing",
    "Editing",
    "Blogging",
    "Copywriting",
    "Social Media Management",
    "Agile Methodologies",
    "Scrum",
    "Kanban",
    "Jira",
    "Network Administration",
    "Cybersecurity",
    "Ethical Hacking",
    "Digital Marketing",
    "SEO",
    "SEM",
    "Social Media Marketing",
    "Sales Strategy",
    "CRM",
    "Negotiation",
]


def skills_to_string(skills_list):
    return " ".join(skills_list)


def calc_jacard(filtered_df, skills):
    res = {}
    skill_set = set([sentence.lower() for sentence in skills])

    for index, row in filtered_df.iterrows():
        jd_set = set(row["ext_Skills"].lower().split())
        intersection = len(jd_set.intersection(skill_set))
        union = len(jd_set.union(skill_set))
        if union == 0:
            similarity = 0

        similarity = intersection / union
        res[index] = similarity

    sorted_keys = sorted(res, key=lambda k: res[k], reverse=True)[:10]
    result_df = filtered_df.loc[sorted_keys]
    result_df.drop(columns=["ext_Skills", "openings"], inplace=True)
    return (
        result_df,
        result_df["company_name"].to_list(),
        result_df["Job_Title"].to_list(),
    )


with tab1:
    with st.form("my_form"):
        name = st.text_input("Name", "mathan")
        experience = int(st.text_input("Work Experience", "5"))

        work_type = st.multiselect(
            "work type",
            ["remote", "on-site", "hybrid"],
            max_selections=1,
            label_visibility="visible",
        )
        skills = st.multiselect(
            "Skills", skills_list, max_selections=10, label_visibility="visible"
        )
        submitted = st.form_submit_button("Submit")

    if submitted and skills and work_type:
        query = {
            "openings.work_type": work_type[0],
            "openings.experience": {"$lte": experience},
            # "openings.skills": {
            #     "$all": skills
            # }
        }
        matching_documents = collection.find(query)
        documents = list(matching_documents)
        jd = pd.DataFrame(documents)

        jd.drop(columns=["_id"], inplace=True)
        jd["Skills"] = jd["openings"].apply(lambda x: x["skills"])
        jd["Job_Title"] = jd["openings"].apply(lambda x: x["name"])
        jd["Experience"] = jd["openings"].apply(lambda x: x["experience"])
        jd["Type"] = jd["openings"].apply(lambda x: x["work_type"])
        jd["location"] = jd["openings"].apply(lambda x: x["location"])
        jd["pay"] = jd["openings"].apply(lambda x: x["pay"])
        jd["Skills"] = jd["Skills"].apply(skills_to_string)

        jd["ext_Skills"] = jd["Skills"].apply(skills_to_string)
        jobs_df, company, job_title = calc_jacard(jd, skills)

        st.table(jobs_df)

        with st.form("my_form_2"):
            company_name = st.selectbox("company", company, label_visibility="visible")
            st.write("You selected:", company_name)

            apply = st.form_submit_button("apply")

        if apply and company_name:
            print("here")
            query = {
                "openings.work_type": work_type[0],
                "openings.experience": {"$lte": experience},
                "company_name": company_name,
            }
            matching_documents = collection.find(query)
            st.success("Applied", icon="✅")

with tab2:
    name = st.text_input("Movie title", "Life of Brian")
