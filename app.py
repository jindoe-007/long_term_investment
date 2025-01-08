# app.py

import streamlit as st
from streamlit_option_menu import option_menu
from long_term_investment_programming import run_optimization
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import json
import os
import time

# --- Functions for Data Persistence ---
def load_data():
    """Load projects and budget data from JSON files into session state."""
    if os.path.exists('projects.json'):
        with open('projects.json', 'r') as f:
            st.session_state.projects = json.load(f)
    if os.path.exists('budget.json'):
        with open('budget.json', 'r') as f:
            st.session_state.budget = json.load(f)

def save_data():
    """Save projects and budget data from session state to JSON files."""
    with open('projects.json', 'w') as f:
        json.dump(st.session_state.projects, f)
    with open('budget.json', 'w') as f:
        json.dump(st.session_state.budget, f)

def rerun_app():
    """Attempt to rerun the Streamlit app, if supported."""
    if hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    else:
        st.warning("UI update requires a manual restart of the app.")

# --- Page Configuration ---
st.set_page_config(
    page_title="Long-term Investment Optimization",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Developed with ❤️ by [Your Name](https://your-website.com)"
    }
)

# --- Initialize Session State ---
if 'projects' not in st.session_state:
    st.session_state.projects = {
        "A": {"cost": 100, "benefit": 10},
        "B": {"cost": 110, "benefit": 9},
        "C": {"cost": 100, "benefit": 8},
        "D": {"cost": 120, "benefit": 9},
        "E": {"cost": 90,  "benefit": 11},
        "F": {"cost": 80,  "benefit": 7},
        "G": {"cost": 95,  "benefit": 10},
        "H": {"cost": 200, "benefit": 20},
        "I": {"cost": 105, "benefit": 10},
    }

if 'budget' not in st.session_state:
    st.session_state.budget = [
        {"year": 2024, "amount": 100},
        {"year": 2025, "amount": 100},
        {"year": 2026, "amount": 100},
        {"year": 2027, "amount": 100},
        {"year": 2028, "amount": 100},
        {"year": 2029, "amount": 100},
        {"year": 2030, "amount": 100},
        {"year": 2031, "amount": 100},
        {"year": 2032, "amount": 100},
        {"year": 2033, "amount": 100},
    ]

if 'results' not in st.session_state:
    st.session_state.results = None

# --- Load Data on Start ---
load_data()

# --- Custom Navigation Menu with streamlit-option-menu ---
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",  # Required
        options=["Home", "Manage Projects", "Manage Budget", "Run Optimization", "View Results"],  # Added "Home"
        icons=["house", "clipboard-data", "cash", "gear", "graph-up"],  # Customized Icons
        menu_icon="cast",  # Optional
        default_index=0,  # Optional
        styles={
            "container": {"padding": "5!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "green"},
        }
    )

# --- Page Content ---
if selected == "Home":
    st.title("Welcome to Long-term Investment Optimization")
    st.markdown("""
    ### **About This Software**
    
    This application is designed to help you optimize long-term investment decisions. It allows you to manage projects and budgets, perform optimizations to maximize total benefits, and analyze the results in detail.
    
    ### **Frameworks and Libraries Used**
    
    - **[Streamlit](https://streamlit.io/):** For building the interactive web application.
    - **[Plotly Express](https://plotly.com/python/plotly-express/):** For creating appealing charts and visualizations.
    - **[Pandas](https://pandas.pydata.org/):** For data manipulation and analysis.
    - **[st_aggrid](https://github.com/PablocFonseca/streamlit-aggrid):** For interactive tables and data displays.
    - **[JSON](https://docs.python.org/3/library/json.html):** For data storage and loading.
    
    ### **Mathematical Foundations and Formulas**
    
    The optimization is based on linear programming models aimed at maximizing total benefits while adhering to budget constraints.
    
    **Objective Function:**
    
    \[
    \text{Maximize} \ Z = \sum_{i=1}^{n} B_i \cdot x_i
    \]
    
    **Constraints:**
    
    \[
    \sum_{i=1}^{n} C_i \cdot x_i \leq \text{Budget}_j \quad \forall j \in \text{Years}
    \]
    
    \[
    x_i \in \{0, 1\} \quad \forall i \in \text{Projects}
    \]
    
    - \( B_i \): Benefit of project \( i \)
    - \( C_i \): Cost of project \( i \)
    - \( x_i \): Decision variable (1 = selected, 0 = not selected)
    - \( \text{Budget}_j \): Available budget in year \( j \)
    
    ### **How to Use the Software**
    
    1. **Manage Projects:**
       - **Edit:** Modify existing projects by updating their costs and benefits.
       - **Add:** Add new projects by entering a unique project ID, cost, and benefit.
       - **Delete:** Remove unnecessary or obsolete projects.
    
    2. **Manage Budget:**
       - **Edit:** Adjust existing budget years.
       - **Add:** Add new budget years by specifying the year and corresponding budget.
       - **Delete:** Remove budget years that are no longer needed.
    
    3. **Run Optimization:**
       - Initiate the optimization process to determine the best investment decisions based on available projects and budget.
       - During optimization, project costs and benefits are analyzed to select the optimal combination.
    
    4. **View Results:**
       - After optimization, view the results including total benefits, funded projects, and detailed metrics.
       - Utilize interactive tables and charts to analyze the results and make informed decisions.
    
    ### **Additional Information**
    
    For questions or feedback about the application, please contact [Your Name](https://your-website.com).
    """)

elif selected == "Manage Projects":
    st.header("Manage Projects")
    st.write("In this section, you can edit existing projects, add new projects, or delete existing ones. Each project has specific costs and benefits used for optimization calculations.")

    # --- Edit Existing Projects ---
    st.subheader("Edit Existing Projects")
    for project_id, details in list(st.session_state.projects.items()):
        with st.expander(f"Edit Project {project_id}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_cost = st.number_input(
                    f"Cost (k PLN) for Project {project_id}",
                    value=int(details["cost"]),
                    step=10,
                    key=f"cost_{project_id}"
                )
            with col2:
                new_benefit = st.number_input(
                    f"Benefit for Project {project_id}",
                    value=int(details["benefit"]),
                    step=1,
                    key=f"benefit_{project_id}"
                )
            with col3:
                update_button = st.button(f"Update Project {project_id}", key=f"update_{project_id}")

            # Handle Update Button Click
            if update_button:
                st.session_state.projects[project_id]["cost"] = new_cost
                st.session_state.projects[project_id]["benefit"] = new_benefit
                st.success(f"Project {project_id} has been updated.")
                # Save Data
                save_data()

            # --- Delete Project Section ---
            st.markdown("### Delete Project")
            with st.form(f"delete_form_{project_id}"):
                st.warning(f"Are you sure you want to delete Project {project_id}? This action cannot be undone.")
                confirm = st.checkbox("Yes, delete this project.")
                delete_submit = st.form_submit_button("Delete")

                if delete_submit:
                    if confirm:
                        del st.session_state.projects[project_id]
                        st.success(f"Project {project_id} has been deleted.")
                        # Save Data
                        save_data()
                        # Rerun to update UI
                        rerun_app()
                    else:
                        st.error("Please confirm the deletion by checking the box.")

    st.markdown("---")

    # --- Add New Project ---
    st.subheader("Add New Project")
    st.write("Add a new project by entering a unique Project ID, associated costs, and expected benefits.")
    with st.form("add_project_form"):
        new_project_id = st.text_input("Project ID (e.g., J)")
        new_project_cost = st.number_input("Cost (k PLN)", min_value=0, step=10, key="new_project_cost")
        new_project_benefit = st.number_input("Benefit", min_value=0, step=1, key="new_project_benefit")
        submitted = st.form_submit_button("Add Project")

        if submitted:
            if new_project_id.strip() == "":
                st.error("Project ID cannot be empty.")
            elif new_project_id in st.session_state.projects:
                st.error("Project ID already exists.")
            else:
                st.session_state.projects[new_project_id] = {"cost": new_project_cost, "benefit": new_project_benefit}
                st.success(f"Project {new_project_id} has been successfully added!")
                # Save Data
                save_data()
                # Rerun to display the new project
                rerun_app()

elif selected == "Manage Budget":
    st.header("Manage Budget")
    st.write("In this section, you can manage the annual budget. Edit existing budget years, add new ones, or delete existing budget entries. These data are used for optimization calculations.")

    # --- Edit Existing Budget Entries ---
    st.subheader("Edit Existing Budget Entries")
    for entry in st.session_state.budget:
        with st.expander(f"Edit Budget Year {entry['year']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_year = st.number_input(
                    "Year",
                    value=int(entry["year"]),
                    step=1,
                    key=f"year_edit_{entry['year']}"
                )
            with col2:
                new_amount = st.number_input(
                    f"Budget (k PLN) for Year {entry['year']}",
                    value=int(entry["amount"]),
                    step=10,
                    key=f"amount_edit_{entry['year']}"
                )
            with col3:
                update_button = st.button(f"Update Budget Year {entry['year']}", key=f"update_budget_{entry['year']}")

            # Handle Update Button Click
            if update_button:
                # Check if the new year is unique or the same as the current
                if new_year != entry["year"] and any(b['year'] == new_year for b in st.session_state.budget):
                    st.error(f"Year {new_year} already exists.")
                else:
                    # Find and update the budget entry
                    for b in st.session_state.budget:
                        if b['year'] == entry['year']:
                            b['year'] = new_year
                            b['amount'] = new_amount
                            break
                    st.success(f"Budget Year {new_year} has been updated.")
                    # Save Data
                    save_data()

            # --- Delete Budget Year Section ---
            st.markdown("### Delete Budget Year")
            with st.form(f"delete_budget_form_{entry['year']}"):
                st.warning(f"Are you sure you want to delete Budget Year {entry['year']}?")
                confirm_budget = st.checkbox("Yes, delete this budget year.")
                delete_budget_submit = st.form_submit_button("Delete Budget Year")

                if delete_budget_submit:
                    if confirm_budget:
                        # Remove the budget entry
                        st.session_state.budget = [b for b in st.session_state.budget if b['year'] != entry['year']]
                        st.success(f"Budget Year {entry['year']} has been deleted.")
                        # Save Data
                        save_data()
                        # Rerun to update UI
                        rerun_app()
                    else:
                        st.error("Please confirm the deletion by checking the box.")

    st.markdown("---")

    # --- Add New Budget Entry ---
    st.subheader("Add New Budget Entry")
    st.write("Add a new budget entry by specifying the year and the corresponding budget in thousand PLN (k PLN).")
    with st.form("add_budget_form"):
        new_budget_year = st.number_input("Year (e.g., 2035)", min_value=1900, max_value=2100, step=1, key="new_budget_year")
        new_budget_amount = st.number_input("Budget (k PLN)", min_value=0, step=10, key="new_budget_amount")
        submitted_budget = st.form_submit_button("Add Budget Entry")

        if submitted_budget:
            if any(b['year'] == new_budget_year for b in st.session_state.budget):
                st.error(f"A budget for the year {new_budget_year} already exists.")
            else:
                st.session_state.budget.append({"year": new_budget_year, "amount": new_budget_amount})
                st.session_state.budget = sorted(st.session_state.budget, key=lambda x: x['year'])
                st.success(f"Budget for the year {new_budget_year} has been successfully added!")
                # Save Data
                save_data()
                # Rerun to display the new budget entry
                rerun_app()

elif selected == "Run Optimization":
    st.header("Run Optimization")
    st.write("""
    **What Happens During Optimization?**
    
    In this section, you initiate the optimization process aimed at determining the best possible selection of projects to maximize total benefits while considering the available budget over the years. The optimization relies on mathematical models that analyze costs, benefits, and budget constraints.
    
    **Optimization Goals:**
    - **Maximize Total Benefits:** Select projects that offer the highest overall value (benefit).
    - **Adhere to Budget Constraints:** Ensure that the total costs of selected projects do not exceed the available budget per year.
    - **Efficient Resource Allocation:** Optimal distribution of financial resources across different years.
    
    ### **Mathematical Foundations**
    
    The optimization is based on linear programming with the following objective function and constraints:
    
    **Objective Function:**
    
    \[
    \text{Maximize} \ Z = \sum_{i=1}^{n} B_i \cdot x_i
    \]
    
    **Constraints:**
    
    \[
    \sum_{i=1}^{n} C_i \cdot x_i \leq \text{Budget}_j \quad \forall j \in \text{Years}
    \]
    
    \[
    x_i \in \{0, 1\} \quad \forall i \in \text{Projects}
    \]
    
    - \( B_i \): Benefit of project \( i \)
    - \( C_i \): Cost of project \( i \)
    - \( x_i \): Decision variable (1 = selected, 0 = not selected)
    - \( \text{Budget}_j \): Available budget in year \( j \)
    """)

    # --- Start Optimization ---
    if st.button("Start Optimization"):
        with st.spinner("Running optimization..."):
            # Sort the budget by year
            sorted_budget = sorted(st.session_state.budget, key=lambda x: x['year'])
            try:
                start_time = time.time()
                results = run_optimization(st.session_state.projects, sorted_budget)
                end_time = time.time()
                computation_time = end_time - start_time
                results['computation_time'] = computation_time  # Add computation time to results
                results['funded_projects_count'] = len([
                    k for k, v in results.get('projects', {}).items() 
                    if v.get('completion_year') != "NOT FUNDED"
                ])
                results['average_roi'] = (
                    sum([v.get("ROI", 0) for v in results.get('projects', {}).values()]) / 
                    len(results.get('projects', {})) if results.get('projects') else 0
                )
                st.session_state.results = results
                if results["status"] == "Optimal":
                    st.success("Optimization completed successfully.")
                else:
                    st.warning("Optimization completed, but no optimal solution was found.")
            except Exception as e:
                st.error(f"Error during optimization: {e}")
                st.session_state.results = None

    # --- Display Optimization Results ---
    if st.session_state.results:
        results = st.session_state.results
        st.subheader("Optimization Results")
        st.write("""
        **Optimization Status:** Indicates whether the optimization found an optimal solution.
        """)

        st.write(f"**Status:** {results['status']}")
        st.write("**Interpretation:** This status indicates whether the optimization found an optimal solution.")

        if results["status"] == "Optimal":
            st.subheader("Optimization Summary")
            st.write("""
            **Total Benefits:** The maximum benefits achieved through the selected projects.
            **Computation Time:** The time taken to perform the optimization.
            **Number of Projects:** How many projects were considered in the optimization.
            """)

            # Summary Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Total Benefits (Units)", value=f"{results['objective']:.2f}")
            with col2:
                st.metric(label="Computation Time (Seconds)", value=f"{results['computation_time']:.2f}")
            with col3:
                st.metric(label="Number of Projects", value=f"{len(st.session_state.projects)}")

            # Total Benefits Bar Chart
            fig_total_benefit = px.bar(
                x=["Total Benefits"],
                y=[results['objective']],
                labels={'x': '', 'y': 'Benefits'},
                title='Total Benefits from Optimization',
                template='plotly_white'
            )
            fig_total_benefit.update_layout(title_x=0.5)
            st.plotly_chart(fig_total_benefit, use_container_width=True)

            # Extended Metrics
            st.subheader("Extended Metrics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Average ROI (%)", value=f"{results.get('average_roi', 0):.2f}")
            with col2:
                st.metric(label="Number of Funded Projects", value=f"{results.get('funded_projects_count', 0)}")

            # Download Button for Results as CSV
            st.download_button(
                label="Download Results as CSV",
                data=pd.DataFrame([
                    {
                        "Status": results["status"],
                        "Total Benefits": results["objective"],
                        "Computation Time (Seconds)": results["computation_time"],
                        "Number of Projects": len(st.session_state.projects),
                        "Average ROI (%)": results.get("average_roi", 0),
                        "Number of Funded Projects": results.get("funded_projects_count", 0)
                    }
                ]).to_csv(index=False),
                file_name='optimization_results.csv',
                mime='text/csv',
            )
        else:
            st.error("The optimization model did not find an optimal solution. Please review your input data and constraints.")

elif selected == "View Results":
    st.header("View Results")
    st.write("""
    Here you can view the results of the performed optimization. You will receive a detailed breakdown of the selected projects, their benefits, ROI, and interactive visualizations for better data interpretation.
    """)

    if st.session_state.results is None:
        st.info("Please run the optimization in the 'Run Optimization' section first.")
    else:
        results = st.session_state.results
        st.subheader("Optimization Status")
        st.write(f"**Status:** {results['status']}")
        st.write("**Interpretation:** This status indicates whether the optimization found an optimal solution.")

        if results["status"] == "Optimal":
            st.subheader("Total Benefits")
            st.write(f"**{results['objective']:.2f} Units**")
            st.write("**Interpretation:** This is the maximum benefit achieved by the selected projects.")

            # --- Summary Metrics ---
            st.subheader("Summary Metrics")
            total_cost = sum([v["cost"] for v in st.session_state.projects.values()])
            total_benefit = results["objective"]
            average_roi = results.get("average_roi", 0)
            funded_projects_count = results.get("funded_projects_count", 0)

            # Display Metrics in Columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(label="Total Costs (k PLN)", value=f"{total_cost:.0f}")
                st.write("**Interpretation:** The total costs of all projects amount to this value.")
            with col2:
                st.metric(label="Total Benefits (Units)", value=f"{total_benefit:.2f}")
                st.write("**Interpretation:** The total benefit achieved through the selected projects.")
            with col3:
                st.metric(label="Average ROI (%)", value=f"{average_roi:.2f}")
                st.write("**Interpretation:** This is the average Return on Investment (ROI) of the selected projects.")
            with col4:
                st.metric(label="Number of Funded Projects", value=f"{funded_projects_count}")
                st.write("**Interpretation:** This number indicates how many projects were funded.")

            # --- Detailed Project Results ---
            st.subheader("Detailed Project Results")
            project_details = []
            for project, info in results.get('projects', {}).items():
                expenditures = ", ".join([
                    f"{exp['year']}: {exp['expenditure']:.1f}k PLN" 
                    for exp in info.get("expenditures", [])
                ]) if info.get("expenditures") else "No Expenditures"
                project_details.append({
                    "Project": project,
                    "Completion Year": info.get("completion_year", "N/A"),
                    "Total Benefit": info.get("total_benefit", 0),
                    "Annual Expenditures": expenditures,
                    "ROI (%)": info.get("ROI", 0)
                })

            project_details_df = pd.DataFrame(project_details)
            # Ensure numeric types are correct
            project_details_df["Total Benefit"] = pd.to_numeric(project_details_df["Total Benefit"], errors='coerce')
            project_details_df["ROI (%)"] = pd.to_numeric(project_details_df["ROI (%)"], errors='coerce')

            # --- Interactive Data Table with AgGrid ---
            st.write("**Note:** You can filter, sort, and select rows to view detailed project information.")
            gb = GridOptionsBuilder.from_dataframe(project_details_df)
            gb.configure_pagination(paginationAutoPageSize=True)  # Add pagination
            gb.configure_side_bar()  # Add sidebar
            gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")
            gb.configure_column("Annual Expenditures", editable=False, filter=True, sortable=True, wrapText=True, autoHeight=True)
            gridOptions = gb.build()

            st.subheader("Project Details Table")
            AgGrid(
                project_details_df,
                gridOptions=gridOptions,
                enable_enterprise_modules=False,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                allow_unsafe_jscode=True,
                theme='streamlit',  # Other themes available
                height=300,
                fit_columns_on_grid_load=True
            )

            # --- Interactive Visualizations ---
            st.subheader("Interactive Visualizations")
            st.write("These visualizations help you better understand the financial aspects and benefits of the selected projects.")

            # Dropdown to select projects for detailed view, all projects selected by default
            selected_projects = st.multiselect(
                "Select Projects for Visualization",
                options=project_details_df["Project"],
                default=project_details_df["Project"].tolist()  # All projects selected by default
            )

            if selected_projects:
                # Filter results for selected projects
                filtered_results = {
                    k: v for k, v in results.get('projects', {}).items() if k in selected_projects
                }

                # Prepare data for visualization
                viz_data = []
                for project, info in filtered_results.items():
                    if info.get("completion_year") != "NOT FUNDED":
                        years = sorted([exp["year"] for exp in info.get("expenditures", [])])
                        expenditures = sorted([exp["expenditure"] for exp in info.get("expenditures", [])])
                        cumulative_expenditures = pd.Series(expenditures).cumsum().tolist()
                        for i, year in enumerate(years):
                            viz_data.append({
                                "Project": project,
                                "Year": year,
                                "Expenditures": expenditures[i],
                                "Cumulative Expenditures": cumulative_expenditures[i],
                                "Benefit": info.get("total_benefit", 0)
                            })

                viz_df = pd.DataFrame(viz_data)

                # Expenditures Over Time
                fig_expenditure = px.line(
                    viz_df,
                    x='Year',
                    y='Cumulative Expenditures',
                    color='Project',
                    markers=True,
                    title='Cumulative Expenditures Over Years',
                    labels={'Cumulative Expenditures': 'Cumulative Expenditures (k PLN)'},
                    template='plotly_white'
                )
                fig_expenditure.update_layout(title_x=0.5)
                st.plotly_chart(fig_expenditure, use_container_width=True)
                st.write("**Interpretation:** This chart shows how the expenditures for each project accumulate over the years.")

                # Benefit Comparison
                fig_benefit = px.bar(
                    pd.DataFrame([
                        {"Project": project, "Total Benefit": info.get("total_benefit", 0), "ROI (%)": info.get("ROI", 0)}
                        for project, info in filtered_results.items()
                    ]),
                    x='Project',
                    y=['Total Benefit', 'ROI (%)'],
                    barmode='group',
                    title='Total Benefit and ROI of Selected Projects',
                    labels={'value': 'Value', 'variable': 'Metric'},
                    template='plotly_white',
                    hover_data=['ROI (%)']
                )
                fig_benefit.update_layout(title_x=0.5)
                st.plotly_chart(fig_benefit, use_container_width=True)
                st.write("**Interpretation:** This bar chart compares the total benefit and Return on Investment (ROI) of the selected projects.")
            else:
                st.warning("Please select at least one project for visualization.")

            # --- Download Detailed Results ---
            st.subheader("Download Detailed Results")
            st.write("You can download the detailed project results as a CSV file for offline analysis.")
            if st.button("Download Complete Results as CSV"):
                csv = project_details_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name='detailed_results.csv',
                    mime='text/csv',
                )

            # --- Project Comparison ---
            st.subheader("Compare Projects")
            st.write("Compare the financial metrics and benefits of different projects side by side to make informed decisions.")
            comparison_projects = st.multiselect(
                "Select Projects to Compare",
                options=project_details_df["Project"],
                default=project_details_df["Project"].tolist()  # All projects selected by default
            )

            if len(comparison_projects) >= 2:
                comparison_df = pd.DataFrame([
                    {
                        "Project": project,
                        "Completion Year": results["projects"][project].get("completion_year", "N/A"),
                        "Total Benefit": results["projects"][project].get("total_benefit", 0),
                        "ROI (%)": results["projects"][project].get("ROI", 0),
                        "Expenditures": ", ".join([
                            f"{exp['year']}: {exp['expenditure']:.1f}k PLN" 
                            for exp in results["projects"][project].get("expenditures", [])
                        ]) if results["projects"][project].get("expenditures") else "No Expenditures"
                    }
                    for project in comparison_projects
                ])

                # AgGrid for Comparison
                st.subheader("Comparison Table")
                st.write("**Interpretation:** This table allows for a direct comparison of the selected projects regarding their completion year, total benefit, ROI, and annual expenditures.")
                gb_comp = GridOptionsBuilder.from_dataframe(comparison_df)
                gb_comp.configure_pagination(paginationAutoPageSize=True)
                gb_comp.configure_side_bar()
                gb_comp.configure_column("Expenditures", editable=False, filter=True, sortable=True, wrapText=True, autoHeight=True)
                gridOptions_comp = gb_comp.build()

                AgGrid(
                    comparison_df,
                    gridOptions=gridOptions_comp,
                    enable_enterprise_modules=False,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    allow_unsafe_jscode=True,
                    theme='streamlit',
                    height=300,
                    fit_columns_on_grid_load=True
                )

                # Visualization: Side-by-Side Bar Chart
                fig_comparison = px.bar(
                    comparison_df,
                    x='Project',
                    y=['Total Benefit', 'ROI (%)'],
                    barmode='group',
                    title='Project Comparison: Total Benefit and ROI',
                    labels={'value': 'Value', 'variable': 'Metric'},
                    template='plotly_white'
                )
                fig_comparison.update_layout(title_x=0.5)
                st.plotly_chart(fig_comparison, use_container_width=True)
                st.write("**Interpretation:** This bar chart compares the total benefit and ROI of the selected projects side by side to identify differences and similarities.")

            elif len(comparison_projects) == 1:
                st.warning("Please select at least two projects for comparison.")
            else:
                st.info("Select projects from the dropdown list to compare their performance.")

        else:
            st.error("The optimization model did not find an optimal solution. Please review your input data and constraints.")