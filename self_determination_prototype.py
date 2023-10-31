import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import yaml
import datetime as dt
import plotly.express as px
from yaml.loader import SafeLoader

# username = 'eskeans'
# name = 'Elii Skeans'

# definitions
# numeric grade values
grade_values = {'A':4,'B':3,'C':2,'D':1,'F':0}

## Functions #####################################################
# def load_user_log():
#     user_log = pd.read_csv('user_log.csv')
#     return user_log

def load_grades():
    grades = pd.read_csv('grades.csv')
    return grades

def load_goals():
    goals = pd.read_csv('goals.csv')
    return goals

############################################################################
## Load Data #####################################################
# user_log = load_user_log()
grades = load_grades()
goals = load_goals()
##################################################################

# config page laout
st.set_page_config(layout="wide")

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

# # Render the login widget by providing a name for the form and its location (i.e., sidebar or main):
name, authentication_status, username = authenticator.login('Login', 'main')
# # Once you have your authenticator object up and running, use the return values to read the name, authentication_status, and username of the authenticated user.
# # You can access the same values through a session state:
if st.session_state["authentication_status"]: # login good
    authenticator.logout('Logout', 'main')
    ##### column 1 #################################################################
    # subset the grades
    user_grades = grades[grades['username'] == username]
    user_goals = goals[goals['username'] == username]
    st.title('{}\'s Student Dashboard'.format(name))
    col1, col2 = st.columns(2)
    ### Grades column, column 1
    # add button statefulness
    if 'addgrades' not in st.session_state:
        st.session_state['addgrades'] = False
    if 'submitgrades' not in st.session_state:
        st.session_state['submitgrades'] = False

    col1.header('Grades')
    col1.write('My Current Grades Are:')
    col1.table(user_grades[user_grades['date']==user_grades['date'].max()][['ELA','Math','Science','History','Phys. Ed.']].T.rename(columns={2:'Grades',3:'Grades'}))
    if col1.button("Add Grades"):
        # change button state
        st.session_state['addgrades'] = not st.session_state['addgrades']
    if st.session_state['addgrades']:
        ela = col1.selectbox('What is your current ELA grade?', ('A','B','C','D','F'))
        math = col1.selectbox('What is your current Math grade?', ('A','B','C','D','F'))
        science = col1.selectbox('What is your current Science grade?', ('A','B','C','D','F'))
        history = col1.selectbox('What is your current History grade?', ('A','B','C','D','F'))
        physed = col1.selectbox('What is your current Phys. Ed. grade?', ('A','B','C','D','F'))
        new_grades = pd.DataFrame({
            'username':[username],
            'name': [name],
            'date':[dt.datetime.now().strftime("%m/%d/%Y %H:%M")],
            'ELA': [ela], 
            'Math': [math],
            'Science': [science],
            'History': [history],
            'Phys. Ed.': [physed]
            })
        if col1.button('Submit Grades'):
            st.session_state['submitgrades'] = not st.session_state['submitgrades']
    if st.session_state['submitgrades']:
        pd.concat([grades,new_grades], ignore_index =True, axis = 0).to_csv('grades.csv', index = None)
        st.session_state['addgrades'] = False
        st.session_state['submitgrades'] = False
        st.rerun()

    # show current grades
    col1.write('Below Shows My Grade History')

    # try except bc you get n error when empty
    try:
        melt_grades = pd.melt(user_grades, id_vars = ['username','name','date'],var_name = 'Subject',value_name = 'Grade')
        fig = px.bar(melt_grades.sort_values("Grade"), 
                    x='date', 
                    y="Grade",
                    color='Subject', 
                    barmode='group',
                    category_orders = {'Grade':['A','B','C','D','F',' ']},
                    facet_col = 'Subject',
                    width = 500)
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
        col1.plotly_chart(fig)
    except Exception as e:
        col1.write('\**No Grade History**')
    ######### column 2 ###############################################################################################
    with col2:
        c = st.container()
        c.header('Goals')
        if user_goals.shape[0]>0:
            c.markdown('My Current Goal is: :blue["{}"]'.format(user_goals[['date','Goal']].sort_values('date').iloc[-1:]['Goal'].values[0]))
        else:
            c.write("No Goals Made Yet")
        new_goal = c.text_input('Type a new goal...')
        if c.button('Add New Goal'):
            new_goal_df = pd.DataFrame({'username':[username],
                                        'name':[name],
                                        'date':[dt.datetime.now().strftime("%m/%d/%Y %H:%M")],
                                        'Goal':[new_goal]})
            pd.concat([goals,new_goal_df],ignore_index=True, axis = 0).to_csv('goals.csv', index=None)
            st.rerun()
        c.write('My Previous Goals were:')
        c.table(user_goals[['date','Goal']].sort_values('date').iloc[:-1])
        c.divider()
        #### column 2 second container ##########
        c = st.container()
        c.header('Attendance')
        c.divider()
        #### column 2 third container ##########
        c = st.container()
        c.header('Behavior')
        c.write('Horrible!')
        c.divider()

elif st.session_state["authentication_status"] == False: # bad login result
    st.error('Username/password is incorrect')
    st.button('Create New User -- not developed yet')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')

