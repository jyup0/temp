import os
import pandas as pd
import numpy as np
import streamlit as st
#import the PublicComment Analysis script
from PublicCommentAnalysis import get_open_rules, CleanRule
    

def DisplayRuleInfo(SelectedRule):
    #first we need to create the variables to pull data from our files
    CleanedRule = CleanRule(SelectedRule)
    DirPath = "temp/" + CleanedRule
    DirRPath = DirPath+"/Results/"
    DirRule = DirPath+"/"+CleanedRule+".csv"
    Ruledf = pd.read_csv(DirRule)
    MatchedPages = []
    columns = ['FileName', 'PageNumber']
    df = pd.DataFrame(columns=columns)

    #loop through each file in the results directory
    for file in os.listdir(DirRPath):
        Resultdf = pd.read_csv(DirRPath+file)
        for _, row1 in Resultdf.iterrows():
            for index, row2 in Ruledf.iterrows():
                CommentRule = str(row1[1])
                RulePage = str(row2["text"])
                if CommentRule == RulePage:
                    MatchedPages.append(index+1)
                    new_row = [file, index]
                    df.loc[len(df)] = new_row
                    
    #Create dashboard
    st.title("Info For: " + CleanedRule)
    st.divider()
    unique_values, counts = np.unique(MatchedPages, return_counts=True)
    chart_data = dict(zip(unique_values, counts))
    st.bar_chart(chart_data)
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Highest Positive Sentement")
        st.text("Functionality not within scope for mvp, this is a placeholder")

    with col2:
        st.subheader("Highest Negative Sentement")
        st.text("Functionality not within scope for mvp, this is a placeholder")
    
    return df

def MakeDF(SelectedRule):
    #first we need to create the variables to pull data from our files
    CleanedRule = CleanRule(SelectedRule)
    DirPath = "temp/" + CleanedRule
    DirRPath = DirPath+"/Results/"
    DirRule = DirPath+"/"+CleanedRule+".csv"
    Ruledf = pd.read_csv(DirRule)
    MatchedPages = []
    columns = ['FileName', 'PageNumber']
    df = pd.DataFrame(columns=columns)

    #loop through each file in the results directory
    for file in os.listdir(DirRPath):
        Resultdf = pd.read_csv(DirRPath+file)
        for _, row1 in Resultdf.iterrows():
            for index, row2 in Ruledf.iterrows():
                CommentRule = str(row1[1])
                RulePage = str(row2["text"])
                if CommentRule == RulePage:
                    MatchedPages.append(index+1)
                    new_row = [file, index]
                    df.loc[len(df)] = new_row
    
    return df

def ShowPage(SelectedRule, SelectedPage, df):
    #first we need to create the variables to pull data from our files
    CleanedRule = CleanRule(SelectedRule)
    DirPath = "temp/" + CleanedRule
    DirRPath = DirPath+"/Results/"
    DirRule = DirPath+"/"+CleanedRule+".csv"
    Ruledf = pd.read_csv(DirRule)
    
    Matchingdf = df[df['PageNumber'] == SelectedPage]
    st.write(Matchingdf)
    unique_values = Matchingdf['FileName'].unique()

    #create the page for ther user
    st.subheader("Abreiviated Page")
    ruletext = str(Ruledf.iloc[SelectedPage])
    st.text(ruletext)
    st.subheader("Matching Public Comments")
    for comment in unique_values:
        
        #create a download button for the comment

        # Split the string by dots and keep all but the last part
        parts = comment.rsplit('.', 1)

        # Join the parts (except the last one) back together
        comment = '.'.join(parts[:-1])

        st.write(comment)

        with open(DirPath+"/PublicComments/"+comment, "rb") as pdf_file:
            document = pdf_file.read()

        st.download_button(
            label="Download Public Comment For Viewing",
            data=document,
            file_name=comment,
        )

#first we will create the page
def main():
    url = 'http://www.fdic.gov/resources/regulations/federal-register-publications/'
    index = 'index.html'
    indexHTML = url + index
    OpenRules = get_open_rules(indexHTML)

    SelectedRule = st.sidebar.selectbox("Select The Ruleset For the Public Comments", OpenRules)
    
    IndividualPageAnalysis = st.sidebar.toggle("Analyze by Page")

    if SelectedRule and not IndividualPageAnalysis:
        df = DisplayRuleInfo(SelectedRule)

    if IndividualPageAnalysis:
        df = MakeDF(SelectedRule)
        max_value_column1 = df['PageNumber'].max()
        PageList = list(range(1, max_value_column1 + 1))
        SelectedPage = st.sidebar.selectbox("Select the Page to be Analyzed", PageList)
        if SelectedPage:
            ShowPage(SelectedRule, SelectedPage, df)

    if SelectedRule:
        CleanedRule = CleanRule(SelectedRule)
        DirPath = "temp/" + CleanedRule
        with open(DirPath+"/"+CleanedRule+".pdf", "rb") as pdf_file:
            document = pdf_file.read()

        st.sidebar.download_button(
            label="Download Ruleset",
            data=document,
            file_name=CleanedRule+".pdf",
        )
            

if __name__ == "__main__":
    main()