import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


def load_user_log():
    pd.read_feather('user_log.feather')
user_log = load_user_log()

# config page laout
st.set_page_config(layout="wide")
st.table(user_log)

# # initialize session_state
# if 'authentication_status' not in st.session_state:
#     st.session_state['authentication_status'] = False

# Import the YAML file into your script:
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create the authenticator object:
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Render the login widget by providing a name for the form and its location (i.e., sidebar or main):
name, authentication_status, username = authenticator.login('Login', 'main')

# Once you have your authenticator object up and running, use the return values to read the name, authentication_status, and username of the authenticated user.
# You can access the same values through a session state:
if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
    st.button('Create New User')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')

