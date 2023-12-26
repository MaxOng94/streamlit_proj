#################################################################################
# Chat2VIS 
# https://chat2vis.streamlit.app/
# Paula Maddigan
#################################################################################

import pandas as pd
import openai
import streamlit as st
from utils import filter_dataframe
#import streamlit_nested_layout
from classes import get_primer_for_plotly,format_question,run_request

import warnings
warnings.filterwarnings("ignore")
st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(page_icon="chat2vis.png",layout="wide",page_title="Chat2VIS")


st.markdown("<h1 style='text-align: center; font-weight:bold;  padding-top: 0rem;'> \
            Streamlit Tech Assessment</h1>", unsafe_allow_html=True)


st.markdown("<h4 >\
                In this assessment, instead of building a streamlit app from scratch, I decided to extend an existing implementation, Chat2vis. Chat2vis is a __ created by __ that allows users to directly display visualization on streamlit.<br><br> I've implemented these additional features:\
                <ol>\
                    <li>Changed visualization to plotly for more interactivity.</li>\
                    <li>\
                        Allow user to edit code generated from LLM.\
                        <ul>\
                            <li>If user is unhappy with the generated plot, they can execute their own code.</li>\
                        </ul>\
                    </li>\
                </ol> \
            </h4>", unsafe_allow_html=True)


available_models = {"ChatGPT-4": "gpt-4","ChatGPT-3.5": "gpt-3.5-turbo","GPT-3": "text-davinci-003",
                        "GPT-3.5 Instruct": "gpt-3.5-turbo-instruct","Code Llama":"CodeLlama-34b-Instruct-hf",
                        "User Input Code":"user-input"}


# List to hold datasets
if "datasets" not in st.session_state:
    datasets = {}
    # Preload datasets
    datasets["Movies"] = pd.read_csv("data/movies.csv")
    datasets["Housing"] =pd.read_csv("data/housing.csv")
    datasets["Cars"] =pd.read_csv("data/usa_cars_datasets.csv")
    # datasets["Colleges"] =pd.read_csv("./colleges.csv")
    # datasets["Customers & Products"] =pd.read_csv("./customers_and_products_contacts.csv")
    # datasets["Department Store"] =pd.read_csv("./department_store.csv")
    # datasets["Energy Production"] =pd.read_csv("./energy_production.csv")
    st.session_state["datasets"] = datasets
else:
    # use the list already loaded
    datasets = st.session_state["datasets"]






with st.sidebar:
    # First we want to choose the dataset, but we will fill it with choices once we've loaded one
    dataset_container = st.empty()

    # Add facility to upload a dataset
    try:
        uploaded_file = st.file_uploader(":computer: Load a CSV file:", type="csv")
        index_no=0
        if uploaded_file:
            # Read in the data, add it to the list of available datasets. Give it a nice name.
            file_name = uploaded_file.name[:-4].capitalize()
            datasets[file_name] = pd.read_csv(uploaded_file)
            # We want to default the radio button to the newly added dataset
            index_no = len(datasets)-1
    except Exception as e:
        st.error("File failed to load. Please select a valid CSV file.")
        print("File failed to load.\n" + str(e))
    # Radio buttons for dataset choice
    chosen_dataset = dataset_container.radio(":bar_chart: Choose your data:",datasets.keys(),index=index_no)#,horizontal=True,)

    # Check boxes for model choice
    st.write(":brain: Choose your model(s):")
    # Keep a dictionary of whether models are selected or not
    use_model = {}
    for model_desc,model_name in available_models.items():
        if model_desc != 'User Input Code':
            label = f"{model_desc} ({model_name})"
            key = f"key_{model_desc}"
            use_model[model_desc] = st.checkbox(label,value=True,key=key)


st.sidebar.markdown('<a style="text-align: center;padding-top: 0rem;" href="mailto: i.build.apps.4.u@gmail.com">:email:</a> Credits to Paula Maddigan and Teo Susnjak, the creator of Chat2VIS', unsafe_allow_html=True)

st.sidebar.markdown('<a style="text-align: center;padding-top: 0rem;" href="https://blog.streamlit.io/chat2vis-ai-driven-visualisations-with-streamlit-and-natural-language">Blog </a> by Paula Maddigan', unsafe_allow_html=True)


# Display the datasets in a list of tabs
# Create the tabs
tab_list = st.tabs(datasets.keys())

# Load up each tab with a dataset
for dataset_num, tab in enumerate(tab_list):
    with tab:
        # Can't get the name of the tab! Can't index key list. So convert to list and index
        dataset_name = list(datasets.keys())[dataset_num]
        st.subheader(dataset_name)
        st.dataframe(filter_dataframe(datasets[dataset_name],dataset_name),hide_index=True)
        # display the dtypes of dataframe in streamlit
        st.write(f"Data Types: {datasets[dataset_name].dtypes}")




with st.container():

    key_col1,key_col2 = st.columns(2)
    openai_key = key_col1.text_input(label = ":key: OpenAI Key:", help="Required for ChatGPT-4, ChatGPT-3.5, GPT-3, GPT-3.  5 Instruct.",type="password")
    hf_key = key_col2.text_input(label = ":hugging_face: HuggingFace Key:",help="Required for Code Llama",  type="password")




    # Initialize a session state variable for the run_id
    if 'run_id' not in st.session_state:
        st.session_state['run_id'] = 0

    # Initialize a session state variable for the show_code flag
    if 'show_code' not in st.session_state:
        st.session_state['show_code'] = False

    if 'edit_code' not in st.session_state:
        st.session_state['edit_code'] = False

    if 'generated_code' not in st.session_state:
        st.session_state['generated_code'] = ""

    if 'model_answer_dict' not in st.session_state:
        st.session_state['model_answer_dict'] = {}

    if 'go_id' not in st.session_state:
        st.session_state['go_id'] = 0

    if 'user_input_code' not in st.session_state:
        st.session_state['user_input_code'] = False







    # Make a list of the models which have been selected
    selected_models = [model_name for model_name, choose_model in use_model.items() if choose_model]
    model_count = len(selected_models)

     # Text area for query
    # add default text in st.text area

    question_default_text = 'Give me a bar chart of the the top 10 grossing movie in ascending order'
    question = st.text_area("Describe what visualization you want in simple english",height=10,value=question_default_text)
    if st.button("Go...",key=f"go_btn{st.session_state.run_id}"):
        st.session_state['go_id'] +=1



    # Execute chatbot query
    if st.session_state['go_id'] and model_count > 0:

        # ========================== api key ========================
        api_keys_entered = True
        # Check API keys are entered.
        if  "ChatGPT-4" in selected_models or "ChatGPT-3.5" in selected_models or "GPT-3" in selected_models or "GPT-3.5 Instruct" in selected_models:
            if not openai_key.startswith('sk-'):
                st.error("Please enter a valid OpenAI API key.")
                api_keys_entered = False
        if "Code Llama" in selected_models:
            if not hf_key.startswith('hf_'):
                st.error("Please enter a valid HuggingFace API key.")
                api_keys_entered = False
        if api_keys_entered:
            # Place for plots depending on how many models
            plots = st.columns(model_count)
            # Get the primer for this dataset
            desc_primer,code_primer = get_primer_for_plotly(datasets[chosen_dataset],'datasets["'+ chosen_dataset + '"]') 
            # Create model, run the request and print the results
               
            run_id = st.session_state['run_id']
            go_id = st.session_state['go_id']

            for plot_num, model_type in enumerate(selected_models):
                with plots[plot_num]:

                    if st.session_state['model_answer_dict'].get(model_type, None):
                        answer = st.session_state['model_answer_dict'][model_type]

                    else:
                        model= available_models[model_type]
                            # Format the question 
                        question_to_ask = format_question(desc_primer, code_primer, question, model_type)   

                        # Run the question
                        answer = run_request(question_to_ask, model,
                                                 go_id, 
                                                 key=openai_key,alt_key=hf_key)
                        answer = code_primer + answer

                    try:
                    #     if st.session_state['user_input_code']:
                    #         subheader_add_on = ' (user_modified)'
                    #     else: 
                    #         subheader_add_on = None

                        st.subheader(model_type)
                        st.session_state['model_answer_dict'][model_type] = answer
                        # the answer is the completed Python script so add to the beginning of the script to it.
                        print("Model: " + model_type)
                        print(answer)
                        st.session_state["generated_code"]= answer
                        if st.session_state.generated_code:
                            exec(answer)  # outputs a plotly visualization in streamlit


                    except Exception as e:
                        if model_type!= 'User Input Code':
                            st.write(e)
                            if type(e) == openai.error.APIError:
                                st.error("OpenAI API Error. Please try again a short time later. (" + str(e) + ")")
                            elif type(e) == openai.error.Timeout:
                                st.error("OpenAI API Error. Your request timed out. Please try again a short time later. (" + str(e) + ")")
                            elif type(e) == openai.error.RateLimitError:
                                st.error("OpenAI API Error. You have exceeded your assigned rate limit. (" + str(e) + ")")
                            elif type(e) == openai.error.APIConnectionError:
                                st.error("OpenAI API Error. Error connecting to services. Please check your network/proxy/  firewall settings. (" + str(e) + ")")
                            elif type(e) == openai.error.InvalidRequestError:
                                st.error("OpenAI API Error. Your request was malformed or missing required parameters. (" + str(e) + ")")
                            elif type(e) == openai.error.AuthenticationError:
                                st.error("Please enter a valid OpenAI API Key. (" + str(e) + ")")
                            elif type(e) == openai.error.ServiceUnavailableError:
                                st.error("OpenAI Service is currently unavailable. Please try again a short time later. (" +    str(e) + ")")
                            else: 
                                st.error("Unfortunately the code generated from the model contained errors and was unable to execute.")
                        else:
                            st.write(e)

                    
                    if st.session_state.show_code:
                        st.code(answer,language="python")
                        revised_code = st.text_area("Insert code changes here",height=10, key =f"user_code_{model_type}_{st.session_state.run_id}")
                        
                        # trigger run user_code under which model_type
                        if st.button(f"Run code",key=f"run_code_btn_{model_type}_{st.session_state.run_id}"):

                            st.session_state['model_answer_dict'][model_type] = revised_code
                            
                            st.session_state.user_input_code = not st.session_state.user_input_code

                            st.rerun()
            
            # Create a button that toggles the show_code flag
             # clicking the btn changes show_code to true
            if st.button("Show/Hide Code",key=f"show_code_btn_{model_type}_{st.session_state.run_id}"):
                 st.session_state.show_code = not st.session_state.show_code
                 st.rerun()

        # Create a button that increments the run_id
        if st.button("Reset App",key=f"reset_btn_{st.session_state.run_id}"):
            st.session_state.clear()
            st.rerun()


            


# Insert footer to reference dataset origin  
footer="""<style>.footer {position: fixed;left: 0;bottom: 0;width: 100%;text-align: center;}</style><div class="footer">
<p> <a style='display: block; text-align: center;'> Datasets courtesy of NL4DV, nvBench and ADVISor </a></p></div>"""
st.caption("Datasets courtesy of NL4DV, nvBench and ADVISor")

# Hide menu and footer
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
