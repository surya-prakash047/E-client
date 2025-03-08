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
from src.utils.stats import EmailStats

def load_rules():
    with open('config/rules.json', 'r') as f:
        return json.load(f)

def save_rules(rules):
    with open('config/rules.json', 'w') as f:
        json.dump(rules, f, indent=4)

def main():
    # Initialize session states at the start of the app
    if 'email_stats' not in st.session_state:
        st.session_state.email_stats = EmailStats()
    if 'rules' not in st.session_state:
        st.session_state.rules = load_rules()
    if 'list_rules' not in st.session_state:
        st.session_state.list_rules = []
    if 'actions_list' not in st.session_state:
        st.session_state.actions_list = []
    if 'rule_name' not in st.session_state:
        st.session_state.rule_name = ''

    st.title("E-Client Manager")
    
    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Select Page",
        ["Rules Manager", "Email Dashboard"]
    )
    
    if page == "Rules Manager":
        st.header("Rules Manager")
        # Initialize session states
        if 'rules' not in st.session_state:
            st.session_state.rules = load_rules()
        if 'list_rules' not in st.session_state:
            st.session_state.list_rules = []
        if 'actions_list' not in st.session_state:
            st.session_state.actions_list = []
        if 'rule_name' not in st.session_state:
            st.session_state.rule_name = ''
        
        with st.container(border=True):
            st.write('#### Conditions')
            st.session_state.rule_name = st.text_input("#### Rule Name")
            if_rule  =st.selectbox('#### IF', options=['any','all'])
            c1, c2,c3 = st.columns(3)
            with c1:
                field_name = st.selectbox('#### Field Name', options=['from','to','subject','body','date received'],)
            with c2:
                if field_name == 'date received':
                    predicate = st.selectbox('#### Predicate', options=['less than','greater than'])
                else:
                    predicate = st.selectbox('#### Predicate', options=['contains','does not contain','less than'])
            with c3:
                if field_name == 'date received':
                    value = st.text_input('#### Days')
                else:
                    value = st.text_input('#### Value')
                    value = value.replace(' ','_')
            if st.button('Add Condition'):
                st.session_state.list_rules.append({'field':field_name.replace(' ','_'),'predicate':predicate.replace(' ','_'),'value':value})

                
        st.write(st.session_state.list_rules)



        if 'actions_list' not in st.session_state:
            st.session_state.actions_list = []
        with st.container(border=True):
            st.write('#### Actions')
            cc1, cc2, = st.columns(2)
            with cc1:
                action = st.selectbox('#### Action', options=['move message','mark as read', 'mark as unread'])
            if action == 'move message':
                with cc2:
                    folder_name = st.text_input('#### Folder Name')
            
            if st.button('Add Action'):
                if action =='move message':
                    st.session_state.actions_list.append({'type':action.replace(' ','_'),'folder':folder_name.replace(' ','_')})
                else:
                    st.session_state.actions_list.append({'type':action.replace(' ','_')})

        if st.button('Apply Rule'):
            st.session_state.rules['rules'].append({
                'name':st.session_state.rule_name,
                'predicate_type':if_rule,
                'conditions':st.session_state.list_rules,
                'actions':st.session_state.actions_list })
            st.session_state.list_rules = []
            st.session_state.actions_list = []   
        st.write(st.session_state.actions_list)
       
        if st.toggle('#### Show Rules'):
            st.write(st.session_state.rules)

            
        if st.button('Save Rules'):
            save_rules(st.session_state.rules)
            st.success("Rules Saved Sucessfully!")
            
    elif page == "Email Dashboard":
        st.header("Email Dashboard")
        
        # Initialize email stats
        if 'email_stats' not in st.session_state:
            st.session_state.email_stats = EmailStats()
        
        # Control Section
        with st.container():
            st.subheader("Email Controls")
            col1, col2 = st.columns(2)
            
            with col2:
                action = st.selectbox("Action", 
                    ["Display Messages", "Mark All as Read", "Mark All as Unread", "Apply Rules"])
            
            
            with col1:
                email_count = st.number_input("Number of emails to fetch", min_value=1, max_value=100, value=10)
            if st.button("Execute Action"):
                gmail = gmailApi()
                db = EmailDatabase()
                rule_engine = RuleEngine()
                
                try:
                    with st.spinner('Fetching emails...'):
                        emails = gmail.fetch_emails(count=email_count)
                    if emails:
                        # Update statistics
                        st.session_state.email_stats.update_from_emails(emails)
                        
                        if action == "Display Messages":

                            st.write("### Email Messages")
                            for email in emails:
                                with st.expander(f"From: {email['from']} - Subject: {email['subject']}"):
                                    st.write(f"**To:** {email['to']}")
                                    st.write(f"**Date:** {email['date']}")
                                    st.write(f"**Labels:** {', '.join(email['labels'])}")
                                    st.write(f"**Is Read:** {'✓' if email['is_read'] else '✗'}")
                                    st.write("**Snippet:**")
                                    st.write(email['snippet'])
                                    if email.get('has_attachment'):
                                        st.write(f"**Attachments:** {', '.join(email['attachment_types'])}")
                        elif action == "Mark All as Read":
                            with st.spinner('Marking emails as read...'):
                                for email in emails:
                                    gmail.mark_as_read(email['id'])
                            st.session_state.email_stats.mark_all_read(len(emails))
                            st.success(f"Marked {len(emails)} emails as read")
                        elif action == "Mark All as Unread":
                            with st.spinner('Marking emails as unread...'):
                                for email in emails:
                                    gmail.mark_as_unread(email['id'])
                            st.session_state.email_stats.mark_all_unread(len(emails))
                            st.success(f"Marked {len(emails)} emails as unread")
                         
                        elif action == "Apply Rules":
                            with st.spinner('Applying rules...'):
                                for email in emails:
                                    db.store_email(email)
                                rule_engine.process_emails(count =email_count)
                            st.success("Rules applied successfully")
                            
                        # Show analytics
                        st.write("### Email Analytics")
                        stats = st.session_state.email_stats.get_basic_stats()
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Total Emails", stats['total'])
                        col2.metric("Read Emails", stats['read'])
                        col3.metric("With Attachments", stats['attachments'])
                        
                        # Folder Distribution
                        folder_stats = db.get_folder_stats(count=email_count)
                        if folder_stats:
                        # Filter out system labels
                            system_labels = {'CATEGORY_UPDATES','INBOX', 'CATEGORY_FORUMS', 
                                        'IMPORTANT', 'CATEGORY_PROMOTIONS', 'CATEGORY_PERSONAL',
                                        'CATEGORY_SOCIAL', 'SENT', 'DRAFT', 'SPAM', 'TRASH','READ','UNREAD'}
                            
                            filtered_stats = [(folder, count) for folder, count in folder_stats 
                                            if folder not in system_labels]
                            
                            if filtered_stats:  # Only create chart if there are user labels
                                folders, counts = zip(*filtered_stats)
                                fig3 = px.bar(
                                    data_frame={"Folders": folders, "Count": counts},
                                    x="Folders",
                                    y="Count",
                                    title='Email Distribution by User Labels',
                                    labels={'Folders': 'Label', 'Count': 'Number of Emails'},
                                    color="Folders",
                                    color_discrete_sequence=px.colors.qualitative.Set3
                                )
                                fig3.update_layout(
                                    xaxis_tickangle=-45,
                                    bargap=0.2,
                                    height=500,
                                    margin=dict(t=50, b=100),
                                    xaxis=dict(
                                        tickfont=dict(size=12),
                                        title=dict(text="Email Labels", font=dict(size=14)),
                                        title_font=dict(size=14, color="white"),
                                    ),
                                    yaxis=dict(
                                        tickfont=dict(size=12),
                                        title_font=dict(size=14, color="white"),
                                    ),
                                    title=dict(
                                        text='Email Distribution by User Labels',
                                        font=dict(size=16, color='white')  # Changed title color to a blue shade
                                    )
                                )
                                fig3.update_traces(
                                textposition='outside',
                                texttemplate='%{y}',
                                hovertemplate='Label: %{x}<br>Count: %{y}<extra></extra>'
                                )
                                st.plotly_chart(fig3, use_container_width=True)
                    else:
                        st.warning("No emails found")
                
                except Exception as e:
                    st.error(f"Error: {e}")
                
                finally:
                    db.close()
                    rule_engine.close()
if __name__ == "__main__":
    main()