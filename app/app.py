
import streamlit as st
import pandas as pd
from llama_index.llms.gemini import Gemini
from dotenv import load_dotenv
import os
from llama_index.core.query_pipeline import (
    QueryPipeline as QP,
    Link,
    InputComponent,
)
from llama_index.core.query_engine.pandas import PandasInstructionParser
from llama_index.core import PromptTemplate
load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

llm = Gemini(api_key=GOOGLE_API_KEY)
df=pd.read_csv("course_information.csv")

instruction_str = (
    "1. Convert the query to executable Python code using Pandas.\n"
    "2. The final line of code should be a Python expression that can be called with the `eval()` function.\n"
    "3. The code should represent a solution to the query.\n"
    "4. PRINT ONLY THE EXPRESSION.\n"
    "5. Do not quote the expression.\n"
    "6. The line of code only use the provided keys : course_code,course_name,credits,L_T_P_split,total_contact_hours,module_1_info,module_2_info,module_3_info,module_4_info,studio_lab_work,recommended_learning_resources\n"
)

pandas_prompt_str = (
    "You are working with a pandas dataframe in Python.\n"
    "The name of the dataframe is `df`.\n"
    "This is the result of `print(df.head())`:\n"
    "{df_str}\n\n"
    "Follow these instructions:\n"
    "{instruction_str}\n"
    "Query: {query_str}\n\n"
    "Expression:"
)
response_synthesis_prompt_str = (
    """Given an input question, synthesize a response from the query results, your name is ReLU
    the AIS Chatbot that helps answer queries related to courses, provided by the college Bennett University.
    You are created by Aviral Jain\n
    """
    "Query: {query_str}\n\n"
    "Pandas Instructions (optional):\n{pandas_instructions}\n\n"
    "Pandas Output: {pandas_output}\n\n"
    "Response: "
)

pandas_prompt = PromptTemplate(pandas_prompt_str).partial_format(
    instruction_str=instruction_str, df_str=df.head(5)
)
pandas_output_parser = PandasInstructionParser(df)
response_synthesis_prompt = PromptTemplate(response_synthesis_prompt_str)

qp = QP(
    modules={
        "input": InputComponent(),
        "pandas_prompt": pandas_prompt,
        "llm1": llm,
        "pandas_output_parser": pandas_output_parser,
        "response_synthesis_prompt": response_synthesis_prompt,
        "llm2": llm,
    },
    verbose=True,
)
qp.add_chain(["input", "pandas_prompt", "llm1", "pandas_output_parser"])
qp.add_links(
    [
        Link("input", "response_synthesis_prompt", dest_key="query_str"),
        Link(
            "llm1", "response_synthesis_prompt", dest_key="pandas_instructions"
        ),
        Link(
            "pandas_output_parser",
            "response_synthesis_prompt",
            dest_key="pandas_output",
        ),
    ]
)
# add link from response synthesis prompt to llm2
qp.add_link("response_synthesis_prompt", "llm2")


def perform_query(query):
    response = qp.run(
    query_str=query
)
    return response

st.title("Specialization Week FAQ Query System")

query_input = st.text_input("Enter your query:")

if st.button("Search"):
    if query_input:
        response = perform_query(query_input)
        st.write("Response:")
        st.write(response)
    else:
        st.write("Please enter a query.")