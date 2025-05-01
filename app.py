import streamlit as st
import pandas as pd
import helper as helper


st.set_page_config(layout="wide")
#********************
# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#********************

# File mapping (used inside helper functions)
global file_list
# Read the Data
file_list = {
    "results_2024": "D:/eeeaaa/1/election_results_2024.csv",
    "electors_by_state": "D:/eeeaaa/1/9-State-Wise-Number-Of-Electors.csv",
    "voters_info": "D:/eeeaaa/1/10-Voters-Information.csv",
    "turnout": "D:/eeeaaa/1/12-State-Wise-Voters-Turn-Out.csv",
    "party_votes": "D:/eeeaaa/1/18-Party-Wise-Seat-Won-&-Valid-Votes-Polled-in-Each-State20241225122257.csv",
    "women_poll_participation": "D:/eeeaaa/1/23-Participation-Of-Women-Electors-In-Polls.csv",
    "women_candidates": "D:/eeeaaa/1/24-Participation-of-Women-Candidates.csv",
    "detailed_results": "D:/eeeaaa/1/33-Constituency-Wise-Detailed-Result.csv",
    "pc_summary": "D:/eeeaaa/1/7-Constituency-(PC)-Wise-Summary.csv",
    "successful_candidates": "D:/eeeaaa/1/4-List-Of-Successful-Candidate.csv",
    "Phases": "D:/eeeaaa/1/phase_data.csv"
}

# Read each file and handle potential errors
for key, file_path in file_list.items():
    try:
        df = pd.read_csv(file_path)
        print(f"Successfully read {key}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")


st.sidebar.title(" India's General Election Analysis 2024" )
st.markdown("""
# Election Analysis 2024- Voting Pattern <img src="https://upload.wikimedia.org/wikipedia/en/thumb/4/41/Flag_of_India.svg/800px-Flag_of_India.svg.png" alt="Indian Flag" style="height: 30px; vertical-align: middle;">
""", unsafe_allow_html=True)
st.sidebar.image("https://img.etimg.com/thumb/msid-109402922,width-480,height-360,imgsize-1940716,resizemode-75/lok-sabha-general-elections-2024.jpg")
# Sidebar Navigation
st.sidebar.title("Navigation")


section = st.sidebar.selectbox("Choose Analysis Section", [
    "Overview",
    "Constituency-wise Analysis",
    "State-wise Analysis",
    "Details Grid-Women's Representation"
])
#nav = st.sidebar.radio("Go to", section)

# --------- OVERVIEW ---------
if section == "Overview":
    insight = st.sidebar.selectbox("Select Insight", [
        "Party-wise Vote Share (Pie Chart)",
        "Seats Won by Party (Bar Chart)",
        "Average Rate of Change (Electors/Votes)",
        "Trend Analysis over Phases"
    ])

    st.title("Overview")
    st.write("Here's an Overview with the analysis of Votes,  Party Shares,  Average Rate & Trend Analysis ")

    if insight == "Party-wise Vote Share (Pie Chart)":
        helper.overview_partywise_votes(file_list)
    elif insight == "Seats Won by Party (Bar Chart)":
        helper.Bar_charts(file_list)
    elif insight == "Average Rate of Change (Electors/Votes)":
        helper.Average_Rate(file_list)
    elif insight == "Trend Analysis over Phases":
        helper.Trend_Analysis(file_list)

# --------- CONSTITUENCY-WISE ANALYSIS ---------
elif section == "Constituency-wise Analysis":
    insight = st.sidebar.selectbox("Select Insight", [
        "Top 10 Parties by Vote Share",
        "Top 10 Victory Margins (Constituencies)",
        "Top 10 Candidates by Margin",
        "Distribution of Victory Margin by Party",
        "Mean Victory vs Loss Margin by Party"
    ])

    st.title("Constituency-wise Analysis")
    st.write("Here's an Constituency-wise analysis of Votes and their impact on party performance, votes perference to part choices &  to what margin votes are distributed leading to their victory/loss")
    if insight == "Top 10 Parties by Vote Share":
        helper.constituency_wise_top10_parties(file_list)
    elif insight == "Top 10 Victory Margins (Constituencies)":
        helper.margin_of_victory(file_list)
    elif insight == "Top 10 Candidates by Margin":
        helper.topN_candidates(file_list)
    elif insight == "Distribution of Victory Margin by Party":
        helper.distribution_of_margin_victory(file_list)
    elif insight == "Mean Victory vs Loss Margin by Party":
        helper.mean_victory_margin(file_list)

# --------- STATE-WISE ANALYSIS ---------
elif section == "State-wise Analysis":
    insight = st.sidebar.selectbox("Select Insight", [
        "State-wise Winning Party Distribution",
        "Total Seats, Alliance with Majority Seats",
        "Winning Candidate and Winning Party by Constituency",
        "State with the Maximum Seats won by Alliance"
    ])

    st.title("State-wise Analysis")
    st.write("Here's a data-driven analysis of State-wide voting patterns, revealing insights into vote distribution, party performance shifts, and the marginal votes that significantly impacted the state's political landscape.")

    if insight == "State-wise Winning Party Distribution":
        helper.state_wise_leading_party(file_list)
    elif insight == "Total Seats, Alliance with Majority Seats":
        helper.state_total_seats_map(file_list)
    elif insight == "Winning Candidate and Winning Party by Constituency":
        helper.constituency_winning_map(file_list)
    elif insight == "State with the Maximum Seats won by Alliance":
        helper.state_max_seats_map(file_list)

# --------- WOMEN'S REPRESENTATION ---------
elif section == "Details Grid-Women's Representation":
    insight = st.sidebar.selectbox("Select Insight", [
        "Top 10 States by Women Winners",
        "Women Winners by Region",
        "Win Rate by Region",
        "Women's Representation Map"
    ])

    st.title("Women's Representation")
    if insight == "Top 10 States by Women Winners":
        helper.womens_top10(file_list)
    elif insight == "Women Winners by Region":
        helper.womens_barplot(file_list)
    elif insight == "Win Rate by Region":
        helper.womens_winrate(file_list)
    elif insight == "Women's Representation Map":
        helper.womens_representation_map(file_list)
