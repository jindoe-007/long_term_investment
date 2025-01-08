# long_term_investment_programming.py

import pulp

def run_optimization(projects, budget):
    """
    Runs the optimization to maximize total benefit given projects and budget.

    Parameters:
    - projects (dict): Dictionary where keys are project IDs and values are dicts with 'cost' and 'benefit'.
    - budget (list): List of dictionaries with 'year' and 'amount'.

    Returns:
    - dict: Contains 'status', 'objective', and 'projects' with detailed results.
    """

    # Check for unique project IDs
    if len(projects) != len(set(projects.keys())):
        raise ValueError("Project IDs are not unique. Please ensure each project ID is distinct.")

    # Sort budget by year
    sorted_budget = sorted(budget, key=lambda x: x['year'])
    years = [entry["year"] for entry in sorted_budget]
    annual_budgets = [entry["amount"] for entry in sorted_budget]
    num_years = len(years)
    T = range(1, num_years + 1)  # Years 1 to num_years

    # Map year index to budget
    B = {t: annual_budgets[t - 1] for t in T}

    # Map year index to calendar year
    year_mapping = {t: years[t - 1] for t in T}

    # Define optimization model
    model = pulp.LpProblem("Project_Financing", pulp.LpMaximize)

    # Decision variables
    x = { (i, t): pulp.LpVariable(f"x_{i}_{t}", lowBound=0, cat=pulp.LpContinuous)
           for i in projects for t in T }

    z = { (i, t): pulp.LpVariable(f"z_{i}_{t}", cat=pulp.LpBinary)
           for i in projects for t in T }

    y = { i: pulp.LpVariable(f"y_{i}", cat=pulp.LpBinary) for i in projects }

    # Constraints

    # 1. Complete financing for each selected project
    for i in projects:
        model += pulp.lpSum(x[(i, t)] for t in T) <= projects[i]["cost"] * y[i], f"Financing_{i}"

    # 2. Annual budget constraint
    for t in T:
        model += pulp.lpSum(x[(i, t)] for i in projects) <= B[t], f"Budget_{t}"

    # 3. Linking completion status and financing
    for i in projects:
        cost_i = projects[i]["cost"]
        for t in T:
            # z[i,t] can only be 1 if the project is selected and sufficiently financed by year t
            model += z[(i, t)] <= y[i], f"CompletionLink_y_{i}_{t}"
            model += z[(i, t)] <= (1.0 / cost_i) * pulp.lpSum(x[(i, tau)] for tau in range(1, t + 1)), f"Completion_{i}_{t}"

    # 4. Monotonicity of completion status
    for i in projects:
        for t in range(1, num_years):
            model += z[(i, t)] <= z[(i, t + 1)], f"Monotonicity_{i}_{t}"

    # Objective function: Maximize total benefit
    model += pulp.lpSum(
        proj["benefit"] * z[(i, t)]
        for i, proj in projects.items()
        for t in T
        if t < num_years  # Benefit starts the year after completion
    ), "Total_Benefit"

    # Solve the model
    model.solve(pulp.PULP_CBC_CMD(msg=0))  # msg=0 suppresses solver details

    # Check status
    status = pulp.LpStatus[model.status]

    if status != "Optimal":
        return {
            "status": status,
            "objective": None,
            "projects": None
        }

    # Compile results
    results = {
        "status": status,
        "objective": pulp.value(model.objective),
        "projects": {}
    }

    for i in projects:
        project_info = {}

        # Determine completion year
        done_t = next((t for t in T if pulp.value(z[(i, t)]) > 0.9999), None)

        if done_t and pulp.value(y[i]) > 0.5:
            actual_year = year_mapping[done_t]
            project_info["completion_year"] = actual_year
        else:
            project_info["completion_year"] = "NOT FUNDED"

        # Annual expenditures
        expenditures = []
        for t in T:
            val_x = pulp.value(x[(i, t)])
            if val_x and val_x > 1e-6:
                actual_year = year_mapping[t]
                expenditures.append({"year": actual_year, "expenditure": val_x})

        project_info["expenditures"] = expenditures

        # Total benefit of the project
        if done_t and pulp.value(y[i]) > 0.5:
            total_benefit = projects[i]["benefit"] * (num_years - done_t)
        else:
            total_benefit = 0
        project_info["total_benefit"] = total_benefit  # Numerical value

        # ROI Calculation
        project_info["ROI"] = (projects[i]["benefit"] / projects[i]["cost"]) * 100 if projects[i]["cost"] > 0 else 0

        results["projects"][i] = project_info

    return results