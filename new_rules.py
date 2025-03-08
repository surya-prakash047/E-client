
import streamlit as st
import json
import os
from src.rules import RuleEngine
from src.api.gmail_api import gmailApi
from src.database import EmailDatabase
import plotly.express as px
from sqlalchemy import func
from datetime import datetime
from email.utils import parsedate_to_datetime


st.set_page_config(layout='wide')

def load_rules():
    with open('config/rules.json', 'r') as f:
        return json.load(f)


if 'rules' not in st.session_state:
    st.session_state.rules = load_rules()

if 'list_rules' not in st.session_state:
    st.session_state.list_rules = []


with st.container(border=True):
    if_rule  =st.selectbox('#### IF', options=['any','all'])
    c1, c2,c3 = st.columns(3)
    with c1:
        field_name = st.selectbox('#### Field Name', options=['from','to','subject','body','attachment','folder'],)
    with c2:
        predicate = st.selectbox('#### Predicate', options=['contains','does not contain','less than'])
    with c3:
        value = st.text_input('#### Value')
    if st.button('Add Condition'):
        st.session_state.list_rules.append({'field_name':field_name,'predicate':predicate,'value':value})

        
st.write(st.session_state.list_rules)



if 'actions_list' not in st.session_state:
    st.session_state.actions_list = []
with st.container(border=True):
    st.write('#### Actions')
    cc1, cc2, = st.columns(2)
    with cc1:
        action = st.selectbox('#### Action', options=['move to folder','mark as read', 'mark as unread'])
    if action == 'move to folder':
        with cc2:
            folder_name = st.text_input('#### Folder Name')
    
    if st.button('Add Action'):
        if action =='move to folder':
            st.session_state.actions_list.append({'action_type':action,'folder':folder_name})
        else:
            st.session_state.actions_list.append({'action_type':action})

if st.button('Apply Rule'):
    st.session_state.rules['rules'].append({
        'predicate_type':if_rule,
        'conditions':st.session_state.list_rules,
        'actions':st.session_state.actions_list })
st.write(st.session_state.actions_list)
if st.toggle('#### Show Rules'):
    st.write(st.session_state.rules)

    
if st.button('Save Rules'):
    save_rules(st.session_state.rules)
def save_rules(rules):
    with open('config/rules.json', 'w') as f:
        json.dump(rules, f, indent=4) st.success('Rules Saved')