# Election Analysis Helper Functions

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import geopandas as gpd

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


def overview_partywise_votes(file_list):
    # Party & Voter’s Vote Analysis
    # Party wise votes Percentage

    # Load the specific dataset
    df_results = pd.read_csv(file_list["results_2024"])
    df_results.columns = df_results.columns.str.strip()  # Clean column names

    parties_won = df_results['Leading Party'].unique()
    parties_lost = df_results['Trailing Party'].unique()
    zero_seats = [party for party in parties_lost if party not in parties_won]

    seats = df_results.groupby('Leading Party')['Leading Party'].count()
    for party in zero_seats:
        if party not in seats:
            seats[party] = 0

    seats = seats.sort_values(ascending=False)

    seats_df = pd.DataFrame({'Party': seats.index, 'Seats': seats.values})
    fig = px.pie(seats_df,
                 values='Seats',
                 names='Party',
                 title='Pie Chart of the Party Wise Vote Percentage',
                 hover_data=['Seats'],
                 labels={'Seats': 'Number of Seats'})

    st.plotly_chart(fig, use_container_width=True)

def Average_Rate(file_list):
    # Average Rate of Change (Electors/Voters)-----

    # 1

    # Load the specific dataset
    df_phases = pd.read_csv(file_list["Phases"])

    # Preview the data
    print(" First few rows of the 'Phases' dataset:")
    print(df_phases.head())

    # Copy for cleaning
    data_imputed = df_phases.copy()

    # List of numeric columns to clean (use exact column names from your CSV)
    numeric_columns = [
        'Count of\nElector*',
        '**Poll (%)',
        'Count of\nVotes***',
        'Count of Elector*',
        '**Poll\n(%)',
        'Count of Votes***'
    ]

    # Fill missing numeric values with mean
    for col in numeric_columns:
        if col in data_imputed.columns and data_imputed[col].dtype in ['float64', 'int64']:
            mean_val = data_imputed[col].mean()
            data_imputed[col] = data_imputed[col].fillna(mean_val)

    # Show how many nulls are left
    print(" Null value summary after imputation:")
    print(data_imputed.isnull().sum())
    # --------------------------------------------
    # 2
    data_imputed = data_imputed.dropna(subset=['State', 'PC Name'], how='all')
    # --------------------------------------------
    # 3
    # Ensure the columns are numeric first
    data_imputed['Count of\nElector*'] = pd.to_numeric(data_imputed['Count of\nElector*'], errors='coerce')
    data_imputed['Count of\nVotes***'] = pd.to_numeric(data_imputed['Count of\nVotes***'], errors='coerce')
    data_imputed['Sl. No.'] = pd.to_numeric(data_imputed['Sl. No.'], errors='coerce')

    # Calculate change between rows (diff)
    data_imputed['Delta Electors'] = data_imputed['Count of\nElector*'].diff()
    data_imputed['Delta Votes'] = data_imputed['Count of\nVotes***'].diff()
    data_imputed['Delta Phase'] = data_imputed['Sl. No.'].diff()

    # Avoid division by zero or nulls in delta phase
    data_imputed['Average Rate of Change (Electors)'] = data_imputed['Delta Electors'] / data_imputed['Delta Phase']
    data_imputed['Average Rate of Change (Votes)'] = data_imputed['Delta Votes'] / data_imputed['Delta Phase']

    # Drop rows with missing data introduced by .diff()
    data_imputed = data_imputed.dropna(subset=[
        'Delta Electors', 'Delta Votes', 'Delta Phase',
        'Average Rate of Change (Electors)', 'Average Rate of Change (Votes)'
    ])

    # Optional: reset index after cleanup
    data_imputed.reset_index(drop=True, inplace=True)

    # Check final nulls (if any)
    print(" Remaining null values:")
    print(data_imputed.isnull().sum())
    # -----------------------------------
    # 4
    x_values = data_imputed['Sl. No.'] if 'Sl. No.' in data_imputed.columns else data_imputed.index

    # Plot: Electors (approximately line 104)
    fig_electors = px.line(data_imputed, x=x_values, y='Average Rate of Change (Electors)',
                           title='Average Rate of Change in Electors per Phase',
                           labels={'Average Rate of Change (Electors)': 'Elector Change Rate',
                                   'x': 'Phase Number'})

    # Plot: Votes (approximately line 110)
    fig_votes = px.line(data_imputed, x=x_values, y='Average Rate of Change (Votes)',
                        title='Average Rate of Change in Votes per Phase',
                        labels={'Average Rate of Change (Votes)': 'Vote Change Rate',
                                'x': 'Phase Number'})

    st.plotly_chart(fig_electors, use_container_width=True) # approximately line 116
    st.plotly_chart(fig_votes, use_container_width=True)    # approximately line 117
def Trend_Analysis(file_list):
    # Trend Analysis Over Phases'-----

    df_phases = pd.read_csv(file_list["Phases"])

    # Preview the data
    print(" First few rows of the 'Phases' dataset:")
    print(df_phases.head())

    # Copy for cleaning
    data_imputed = df_phases.copy()

    # Fixing column names
    column_map = {
        'Count of\nElector*': 'Electors',
        '**Poll (%)': 'Poll Percentage',
        'Count of\nVotes***': 'Votes',
        'Count of Elector*': 'Electors_Alt',
        '**Poll\n(%)': 'Poll_Percentage_Alt',
        'Count of Votes***': 'Votes_Alt'
    }

    # Rename columns safely (only those present)
    data_imputed = data_imputed.rename(columns={k: v for k, v in column_map.items() if k in data_imputed.columns})

    # Define numeric columns that actually exist
    numeric_cols = [col for col in ['Electors', 'Poll Percentage', 'Votes'] if col in data_imputed.columns]

    # Convert them to numeric
    data_imputed[numeric_cols] = data_imputed[numeric_cols].apply(pd.to_numeric, errors='coerce')

    # Plot
    fig = px.line(data_imputed, x='Sl. No.', y=numeric_cols,
              title='Trend Analysis of Electors, Poll %, and Votes Across Phases',
              labels={'Sl. No.': 'Phase Number', 'value': 'Counts / Percentage', 'variable': 'Metric'},
              markers=True)

    fig.update_layout(yaxis_range=[0, 2500000])

    # Display the interactive chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def Bar_charts(file_list):
    # DATA VISUALIZATION
    # Bar charts for the number of seats won by parties.
    # Load the specific dataset
    df_results = pd.read_csv(file_list["results_2024"])
    df_results.columns = df_results.columns.str.strip()  # Clean column names

    # Get unique parties from winning and losing columns
    won = df_results['Leading Party'].dropna().unique()
    lost = df_results['Trailing Party'].dropna().unique()

    # Find parties that only lost (never won)
    zero_seat_parties = [party for party in lost if party not in won]

    # Print result
    print("Parties that contested but won 0 seats:")
    for p in zero_seat_parties:
        print("-", p)

    seats = df_results.groupby('Leading Party')['Leading Party'].count()
    for party in zero_seat_parties:
        if party not in seats:
            seats[party] = 0

    seats = seats.sort_values(ascending=False)


    # Create a DataFrame for Plotly Express
    seats_df = pd.DataFrame({'Party': seats.index, 'Number of Seats': seats.values})

    # Create the interactive bar chart using Plotly Express
    fig = px.bar(seats_df, x='Party', y='Number of Seats',
                 title='Number of Seats Won by Each Party',
                 labels={'Number of Seats': 'Number of Seats', 'Party': 'Party'})

    # Rotate x-axis labels for better readability
    fig.update_layout(xaxis_tickangle=-45)

    # Display the interactive chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def constituency_wise_top10_parties(file_list):
    # VOTE DISTRIBUTION AND SHARING
    # Votes distribution by parties (overall and state-wise) .
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Step 1: Read individual files
    phase_data = pd.read_csv("D:/eeeaaa/1/phase_data.csv")
    eci_data = pd.read_csv("D:/eeeaaa/1/eci_data_2024.csv", encoding='latin1')
    ge_india_data = pd.read_csv("D:/eeeaaa/1/GE India_2024.csv")

    # Step 2: Keep individual references (optional but useful)
    dataset_list = {
        'phase_data': phase_data,
        'eci_data': eci_data,
        'ge_india_data': ge_india_data
    }

    # Step 3: Concatenate all into a single DataFrame (row-wise)
    data = pd.concat([phase_data, eci_data, ge_india_data], ignore_index=True)

    # Step 4: Clean and transform the data
    data.replace('-', pd.NA, inplace=True)
    data['Total Votes'] = pd.to_numeric(data['Total Votes'], errors='coerce')
    data = data.dropna(subset=['Total Votes'])

    # Step 5: Compute total constituency votes
    data['Total Constituency Votes'] = data.groupby('Constituency')['Total Votes'].transform('sum')

    # Step 6: Calculate vote share for each candidate
    data['Vote Share'] = (data['Total Votes'] / data['Total Constituency Votes']) * 100

    # Step 7: Group by party and normalize vote share
    party_vote_share = data.groupby('Party')['Vote Share'].sum().reset_index()
    party_vote_share['Normalized Vote Share'] = (party_vote_share['Vote Share'] / party_vote_share[
        'Vote Share'].sum()) * 100

    # Step 8: Visualize top parties
    top_parties = party_vote_share.sort_values(by='Normalized Vote Share', ascending=False).head(10)

    fig = px.bar(top_parties,
                 x='Normalized Vote Share',
                 y='Party',
                 orientation='h',
                 color='Party',
                 text='Normalized Vote Share',
                 title='Top 10 Parties by Normalized Vote Share',
                 labels={'Normalized Vote Share': 'Normalized Vote Share (%)', 'Party': 'Party'})

    fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    fig.update_layout(xaxis_range=[0, top_parties['Normalized Vote Share'].max() * 1.1])
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    st.plotly_chart(fig, use_container_width=True)

def margin_of_victory(file_list):
    # MARGIN OF VICTORY ANALYSIS

    # Top 10 constituencies with the largest margin of victory.
    import random
    # Load the specific dataset
    df_results = pd.read_csv(file_list["results_2024"])
    df_results.columns = df_results.columns.str.strip()  # Clean column names

    df_results['Margin'] = pd.to_numeric(df_results['Margin'], errors='coerce')  # to avoid typeerror
    df_results = df_results.dropna(subset=['Margin'])

    top_margins = df_results.nlargest(10, 'Margin')
    parties = top_margins['Leading Party'].unique()
    fig = px.bar(top_margins,
                 x='Constituency',
                 y='Margin',
                 color='Leading Party',
                 title='Top 10 Constituencies with the Largest Margin of Victory',
                 labels={'Margin': 'Victory Margin', 'Constituency': 'Constituency', 'Leading Party': 'Leading Party'})

    fig.update_layout(xaxis_tickangle=-45)
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

    st.plotly_chart(fig, use_container_width=True)

def topN_candidates(file_list):
    # Top N candidates with the highest and lowest margins of victory

    df_results = pd.read_csv(file_list["results_2024"])
    df_results.columns = df_results.columns.str.strip()

    # Convert for sorting
    df_results['Margin'] = pd.to_numeric(df_results['Margin'], errors='coerce')

    # Drop rows missing
    df_results = df_results.dropna(subset=['Margin'])

    def top_n_leading_candidates(file_list, n=10):
        top_n_candidates = file_list.nlargest(n, 'Margin')
        fig = px.bar(top_n_candidates,
                     x='Margin',
                     y='Leading Candidate',
                     color='Leading Party',
                     orientation='h',
                     title=f'Top {n} Leading Candidates by Margin of Victory',
                     labels={'Margin': 'Margin', 'Leading Candidate': 'Leading Candidate',
                             'Leading Party': 'Leading Party'})
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        fig.update_layout(legend=dict(title='Leading Party', yanchor="top", y=0.99, xanchor="right", x=0.99))
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig, use_container_width=True)

    top_n_leading_candidates(df_results, n=10)


def topN_constituencies(file_list):
    # Top N constituencies with largest margin of victory
    df_results = pd.read_csv(file_list["results_2024"])
    df_results.columns = df_results.columns.str.strip()

    def plot_top_n_margins(df_results, n=10):
        df_results['Margin'] = df_results['Margin'].replace('-', '0')
        df_results['Margin'] = df_results['Margin'].str.replace(',', '').astype(int)

        top_n_margin = df_results.nlargest(n, 'Margin')

        plt.figure(figsize=(12, 6))
        sns.barplot(x='Margin', y='Constituency', data=top_n_margin, hue='Leading Party')
        plt.title(f'Top {n} Constituencies with the Largest Margin of Victory')
        plt.xlabel('Margin')
        plt.ylabel('Constituency')
        plt.legend(title='Leading Party')
        st.pyplot()
    plot_top_n_margins(df_results, n=10)


def distribution_of_margin_victory(file_list):
    # Distribution of margin of victory by leading parties.
    df_results = pd.read_csv(file_list["results_2024"])
    def party_wise_margin_distribution(df_results):
        plt.figure(figsize=(14, 8))

        # Clean up
        df_results['Leading Party'] = df_results['Leading Party'].str.strip()
        unique_parties = df_results['Leading Party'].unique()

        default_palette = sns.color_palette("husl", len(unique_parties))
        color = dict(zip(unique_parties, default_palette))

        # Plot
        fig = px.box(df_results,
                     x='Leading Party',
                     y='Margin',
                     color='Leading Party',
                     title='Distribution of Margin of Victory by Leading Party',
                     labels={'Margin': 'Margin', 'Leading Party': 'Leading Party'})

        fig.update_layout(xaxis_tickangle=-45)
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        st.plotly_chart(fig, use_container_width=True)

    party_wise_margin_distribution(df_results)


def mean_victory_margin(file_list):
    # Mean victory margin vs. mean loss margin.

    df_results = pd.read_csv(file_list["results_2024"])
    df_results.columns = df_results.columns.str.strip()

    # Convert 'Margin' to numeric
    df_results['Margin'] = pd.to_numeric(df_results['Margin'], errors='coerce')

    df_results.dropna(subset=['Margin', 'Leading Party', 'Trailing Party'], inplace=True)

    # Compute average margins
    winning = df_results.groupby('Leading Party')['Margin'].mean().reset_index()
    winning = winning.rename(columns={'Leading Party': 'Party', 'Margin': 'Average Winning Margin'})

    losing = df_results.groupby('Trailing Party')['Margin'].mean().reset_index()
    losing = losing.rename(columns={'Trailing Party': 'Party', 'Margin': 'Average Losing Margin'})

    # Set figure size
    # Merge the two dataframes
    merged_margins = pd.merge(winning, losing, on='Party', how='outer').fillna(0)

    # Melt the dataframe for easier plotting with Plotly Express
    melted_margins = pd.melt(merged_margins,
                             id_vars=['Party'],
                             value_vars=['Average Winning Margin', 'Average Losing Margin'],
                             var_name='Margin Type',
                             value_name='Average Margin')

    # Create the grouped bar chart using Plotly Express
    fig = px.bar(melted_margins,
                 x='Party',
                 y='Average Margin',
                 color='Margin Type',
                 barmode='group',
                 title="Average Margin by Party (Winning vs Losing)",
                 labels={'Average Margin': 'Average Margin', 'Party': 'Party', 'Margin Type': 'Margin Type'})

    fig.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)
def state_wise_leading_party(file_list):
    #

    df_results = pd.read_csv(file_list["results_2024"])
    df_results.columns = df_results.columns.str.strip()

    # Missing
    df_results = df_results.dropna(subset=['Leading Party'])

    #df_results['Party Color'] = df_results['Leading Party']
    leading_party_counts = df_results['Leading Party'].value_counts().reset_index()
    leading_party_counts.columns = ['Leading Party', 'Number of Wins']
    fig = px.bar(leading_party_counts,
                 y='Leading Party',
                 x='Number of Wins',
                 color='Leading Party',
                 orientation='h',
                 title='Distribution of Leading Parties',
                 labels={'Number of Wins': 'Number of Wins', 'Leading Party': 'Leading Party'})

    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig.update_layout(showlegend=False)
    fig.update_layout(uniformtext_minsize=2, uniformtext_mode='hide')

    st.plotly_chart(fig, use_container_width=True)



def state_total_seats_map(file_list):
    df_results = pd.read_csv(file_list["results_2024"])
    state_seats = df_results.groupby('State').agg({'Constituency_ID': 'count', 'Alliance': lambda x: x.mode()[0]}).reset_index()
    fig = px.choropleth(state_seats, locations="State", locationmode="country names", color="Constituency_ID",
                        hover_data=["Alliance"], title="Total Seats and Majority Alliance")
    st.plotly_chart(fig)

def constituency_winning_map(file_list):
    df_results = pd.read_csv(file_list["results_2024"])
    winning_df = df_results.loc[df_results.groupby('Constituency_ID')['Total_Votes'].idxmax()]
    fig = px.scatter(winning_df, x="Constituency_Name", y="Total_Votes", color="Party",
                     size="Margin", hover_data=["Candidate", "Alliance"],
                     title="Winning Candidate and Party by Constituency")
    st.plotly_chart(fig)

def state_max_seats_map(file_list):
    df_results = pd.read_csv(file_list["results_2024"])
    alliance_seats = df_results.groupby(['State', 'Alliance']).size().reset_index(name='Seats')
    max_seats = alliance_seats.loc[alliance_seats.groupby('State')['Seats'].idxmax()]
    fig = px.choropleth(max_seats, locations="State", locationmode="country names", color="Alliance",
                        hover_data=["Seats"], title="Maximum Seats by Alliance")
    st.plotly_chart(fig)

def womens_top10(file_list):
    # Use the correct header row — in your case it's row 3 (0-indexed = 2)
    df = pd.read_csv(file_list['women_candidates'], header=2)
    df.columns = df.columns.str.strip()  # Clean up any extra spaces

    # Keep only rows where Constituency Type == 'State Total'
    df_state_total = df[df['Constituency Type'] == 'State Total']

    df_state_total = df_state_total[["State /UT", "Contestants", "Elected"]]
    df_state_total = df_state_total.sort_values("Elected", ascending=False)

    print(df_state_total.head(10))  # Top 10 states with most women winners

    # visuals for women electors
    fig = px.bar(df_state_total,
                 x="Elected",
                 y="State /UT",
                 orientation='h',
                 color="State /UT",
                 title="Top 10 States by Women Winners",
                 labels={"Elected": "Number of Women Elected", "State /UT": "State /UT"})

    fig.update_layout(showlegend=False)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True)

    region_map = {
        "Punjab": "North", "Haryana": "North", "Uttar Pradesh": "North", "Delhi": "North",
        "Rajasthan": "West", "Gujarat": "West", "Maharashtra": "West",
        "Kerala": "South", "Tamil Nadu": "South", "Andhra Pradesh": "South", "Telangana": "South", "Karnataka": "South",
        "Bihar": "East", "Jharkhand": "East", "West Bengal": "East", "Odisha": "East",
        "Assam": "North-East", "Meghalaya": "North-East",
        # Add more states as needed
    }

    df_state_total["Region"] = df_state_total["State /UT"].map(region_map)

    st.write(df_state_total[["State /UT", "Region"]].head(10))


def womens_representation_map(file_list):
    # Load CSV
    df = pd.read_csv(file_list['women_candidates'], header=2)
    df.columns = df.columns.str.strip()

    # Filter for state totals only
    df_state_total = df[df['Constituency Type'] == 'State Total'][["State /UT", "Contestants", "Elected"]]
    df_state_total = df_state_total.sort_values("Elected", ascending=False)

    # Add Region mapping
    region_map = {
        "Punjab": "North", "Haryana": "North", "Uttar Pradesh": "North", "Delhi": "North",
        "Rajasthan": "West", "Gujarat": "West", "Maharashtra": "West", "Goa": "West",
        "Kerala": "South", "Tamil Nadu": "South", "Andhra Pradesh": "South", "Telangana": "South", "Karnataka": "South",
        "Bihar": "East", "Jharkhand": "East", "West Bengal": "East", "Odisha": "East",
        "Assam": "North-East", "Manipur": "North-East", "Meghalaya": "North-East", "Arunachal Pradesh": "North-East"
    }
    df_state_total["Region"] = df_state_total["State /UT"].map(region_map)

    # Prepare state names for merging
    df_state_total['State_clean'] = df_state_total['State /UT'].str.strip().str.lower()
    maps = {
        'andaman & nicobar islands': 'andaman and nicobar islands',
        'arunachal pradesh': 'arunāchal pradesh',
        'bihar': 'bihār',
        'chandigarh': 'chandīgarh',
        'chhattisgarh': 'chhattīsgarh',
        'dadra & nagar haveli': 'dādra and nagar haveli and damān and diu',
        'jammu & kashmir': 'jammu and kashmīr',
        'jharkhand': 'jhārkhand',
        'karnataka': 'karnātaka',
        'maharashtra': 'mahārāshtra',
        'meghalaya': 'meghālaya',
        'mizoram': 'mizoram',
        'nagaland': 'nāgāland',
        'odisha': 'odisha',
        'puducherry': 'puducherry',
        'rajasthan': 'rājasthān',
        'tamil nadu': 'tamil nādu',
        'telangana': 'telangāna',
        'uttarakhand': 'uttarākhand',
        'himachal pradesh': 'himāchal pradesh',
        'uttar pradesh': 'uttar pradesh',
        'delhi': 'delhi',
        'gujarat': 'gujarāt',
        'haryana': 'haryāna',
        'kerala': 'kerala',
        'ladakh': 'ladākh',
        'lakshadweep': 'lakshadweep',
        'manipur': 'manipur',
        'tripura': 'tripura',
        'sikkim': 'sikkim',
        'west bengal': 'west bengal',
        'punjab': 'punjab'
    }
    df_state_total['State_clean'] = df_state_total['State_clean'].replace(maps)

    # Load and prepare map
    india_map = gpd.read_file(r"D:\EA\csv\Indian_State_geoboundary.geojson")
    india_map['state_clean'] = india_map['shapeName'].str.strip().str.lower()

    merged = india_map.merge(df_state_total, left_on='state_clean', right_on='State_clean', how='left')
    merged['Elected'] = pd.to_numeric(merged['Elected'], errors='coerce').fillna(0)

    # Draw map
    fig_map = px.choropleth_mapbox(merged,
                                   geojson=merged.geometry.__geo_interface__,
                                   locations=merged.index,
                                   color='Elected',
                                   color_continuous_scale="OrRd",
                                   center={"lat": 20.5937, "lon": 78.9629},
                                   zoom=3,
                                   opacity=0.8,
                                   title="Women's Participation by State (Elected Women)",
                                   labels={'Elected': 'Number of Women Elected'})
    fig_map.update_layout(mapbox_style="carto-positron")
    fig_map.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)

    return df_state_total


def womens_barplot(file_list):
    # Load CSV
    df = pd.read_csv(file_list['women_candidates'], header=2)
    df.columns = df.columns.str.strip()

    # Filter for state totals only
    df_state_total = df[df['Constituency Type'] == 'State Total'][["State /UT", "Contestants", "Elected"]]
    df_state_total = df_state_total.sort_values("Elected", ascending=False)

    # Add Region mapping
    region_map = {
        "Punjab": "North", "Haryana": "North", "Uttar Pradesh": "North", "Delhi": "North",
        "Rajasthan": "West", "Gujarat": "West", "Maharashtra": "West", "Goa": "West",
        "Kerala": "South", "Tamil Nadu": "South", "Andhra Pradesh": "South", "Telangana": "South", "Karnataka": "South",
        "Bihar": "East", "Jharkhand": "East", "West Bengal": "East", "Odisha": "East",
        "Assam": "North-East", "Manipur": "North-East", "Meghalaya": "North-East", "Arunachal Pradesh": "North-East"
    }
    df_state_total["Region"] = df_state_total["State /UT"].map(region_map)

    # Region-wise Aggregation & display
    df_region = df_state_total.groupby("Region")[["Contestants", "Elected"]].sum()
    df_region["Win Rate (%)"] = (df_region["Elected"] / df_region["Contestants"]) * 100
    print(df_region)

    # Reset index to make 'Region' a column
    df_region.reset_index(inplace=True)

    # Barplot: Women Winners by Region
    fig = px.bar(df_region,
                 x="Elected",
                 y="Region",  # Now 'Region' is a column after reset_index()
                 color="Region",  # Now we can use 'Region' in the color argument
                 orientation='h',
                 title="Women Winners by Region",
                 labels={"Elected": "Number of Women Elected", "Region": "Region"})

    fig.update_layout(showlegend=False)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True)

    # Return the processed DataFrame if needed (optional)
    return df_state_total


def womens_winrate(file_list):
    # Load CSV
    df = pd.read_csv(file_list['women_candidates'], header=2)
    df.columns = df.columns.str.strip()

    # Filter for state totals only
    df_state_total = df[df['Constituency Type'] == 'State Total'][["State /UT", "Contestants", "Elected"]]
    df_state_total = df_state_total.sort_values("Elected", ascending=False)

    # Add Region mapping
    region_map = {
        "Punjab": "North", "Haryana": "North", "Uttar Pradesh": "North", "Delhi": "North",
        "Rajasthan": "West", "Gujarat": "West", "Maharashtra": "West", "Goa": "West",
        "Kerala": "South", "Tamil Nadu": "South", "Andhra Pradesh": "South", "Telangana": "South", "Karnataka": "South",
        "Bihar": "East", "Jharkhand": "East", "West Bengal": "East", "Odisha": "East",
        "Assam": "North-East", "Manipur": "North-East", "Meghalaya": "North-East", "Arunachal Pradesh": "North-East"
    }
    df_state_total["Region"] = df_state_total["State /UT"].map(region_map)

    # Group by Region and calculate Win Rate
    df_region = df_state_total.groupby("Region")[["Contestants", "Elected"]].sum()
    df_region["Win Rate (%)"] = (df_region["Elected"] / df_region["Contestants"]) * 100

    # Reset index to make 'Region' a column again
    df_regions = df_region.reset_index()

    # Plotting the barplot using seaborn
    fig= px.bar(df_regions,
                x="Win Rate (%)",
                y="Region",
                color="Region",
                orientation='h',
                title="Women's Win Rate (%) by Region",
                labels={"Win Rate (%)": "Win Rate (%)", "Region": "Region"})


    fig.update_layout(showlegend=False)
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True)




