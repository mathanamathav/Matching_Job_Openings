import streamlit as st

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
import random

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
    collection2 = db["People"]


except Exception as e:
    print(e)

tab1, tab2 = st.tabs(
    ["Jobs Recommendation For Your Profile", "Apply from Resume: Colab Only"]
)

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
    if "applied_candidates" in result_df.columns:
        result_df.drop(
            columns=["ext_Skills", "openings", "applied_candidates"], inplace=True
        )
    else:
        result_df.drop(columns=["ext_Skills", "openings"], inplace=True)
    return (
        result_df,
        result_df["company_name"].to_list(),
        result_df["Job_Title"].to_list(),
    )


def update_data(user_personal_id, company_name, work_type, experience):
    print(user_personal_id)

    collection.update_one(
        {
            "company_name": company_name,
            "openings.work_type": work_type[0],
            "openings.experience": {"$lte": experience},
        },
        {"$push": {"openings.applied_candidates": user_personal_id}},
    )
    collection2.update_one(
        {
            "name": name,
        },
        {"$push": {"applied_company": company_name}},
    )


with tab1:
    name = st.text_input("Name", "Bartlet")

    button_clicked = st.button("Search")
    if button_clicked:
        query_res = list(collection2.find({"name": name}))[0]

        if query_res:
            user_personal_id = query_res.get("personal_id", 15)

            experience = int(st.text_input("Work Experience", "5"))

            work_type = st.multiselect(
                "work type",
                ["remote", "on-site", "hybrid"],
                max_selections=1,
                label_visibility="visible",
                default=query_res.get("Work-type", "remote"),
            )
            skills = st.multiselect(
                "Skills",
                skills_list,
                max_selections=10,
                label_visibility="visible",
                default=query_res.get("Skills"),
            )

            if work_type and experience and skills:
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

                company_name = st.text_input("company", company[0])
                st.write("You selected:", company_name)

                submitted = st.button(
                    "Applied",
                    on_click=update_data(
                        user_personal_id, company_name, work_type, experience
                    ),
                )


with tab2:
    from IPython.display import HTML
    import nbformat
    from nbconvert import HTMLExporter

    # Load the Colab notebook file
    colab_notebook_file = "notebooks/SPACY_RESUME.ipynb"
    with open(colab_notebook_file, "r", encoding="utf8") as f:
        nb_content = nbformat.read(f, as_version=4)

    # Convert the notebook to HTML
    html_exporter = HTMLExporter()
    html_content, _ = html_exporter.from_notebook_node(nb_content)

    # Display the Colab content in Streamlit
    st.title("Google Colab in Streamlit")
    st.write(
        """
        To address the time constraints, we can extend the keyword extraction approach to automatically extract keywords from uploaded resume documents. The procedure will mirror the steps used in the keyword approach. Due to these limitations, we'll refrain from employing Colab for simulating keyword extraction from resumes.

        Here's an outline of the modified procedure:

        1. **Upload Resumes**: Allow users to upload their resume documents to the Streamlit app.

        2. **Keyword Extraction**: Implement an automated keyword extraction process that analyzes the uploaded resumes and extracts relevant keywords. This can involve techniques like natural language processing (NLP) and text mining.

        3. **Keyword Analysis**: Once the keywords are extracted, proceed with the same analysis steps as in the initial keyword approach. You can generate word clouds, calculate keyword frequencies, and use these insights to understand the skills and experiences highlighted in the resumes.

        4. **Display Insights**: Present the keyword-based insights to the user through Streamlit's interactive visualizations and text displays.

        Remember that automated keyword extraction might not be perfect and can vary depending on the complexity of the resumes and the quality of the extraction techniques used. It's recommended to fine-tune and validate the keyword extraction process to ensure accurate results.

        With this approach, you can provide users with a more streamlined experience, enabling them to quickly understand the key skills and experiences highlighted in their uploaded resumes. 
             """
    )
    st.components.v1.html(html_content, height=8000)
