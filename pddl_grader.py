import os
import requests
import csv
from tqdm import tqdm
import time
import argparse

def solve_pddl(domain_path, problem_path):
    """
    Sends a domain and problem PDDL file to the solver API and retrieves the plan.
    """
    with open(domain_path, 'r') as domain_file, open(problem_path, 'r') as problem_file:
        domain_data = domain_file.read()
        problem_data = problem_file.read()

    json_data = {
        'domain': domain_data,
        'problem': problem_data,
    }

    response = requests.post('https://solver.planning.domains:5001/package/dual-bfws-ffparser/solve', json=json_data)

    plan_url_prefix = 'https://solver.planning.domains:5001'
    plan_url_suffix = response.json()['result']
    plan_url = plan_url_prefix + plan_url_suffix

    plan = None
    while plan is None:
        time.sleep(1.)
        response = requests.post(plan_url, json={'adaptor': 'planning_editor_adaptor'})
        try:
            if response.json()['status'] == 'error':
                return ''
            plan = '\n'.join([
                action['name']
                for action in response.json()['plans'][0]['result']['plan']
            ])
        except Exception as e:
            print(f"Exception solving domain {domain_path}: {e}")
            return None

    return plan

def compare_plans(student_plan, baseline_plan):
    """
    Compare the student's plan with the baseline plan.
    """
    return student_plan == baseline_plan

def grade_pddl_files(directory, baseline_file_path, baseline_plan, mode):
    """
    Grades all the PDDL files in a directory.

    Args:
        directory (str): Path to the directory containing the PDDL files
        baseline_file_path (str): The baseline problem or domain file's path.
        baseline_plan (str): The baseline solution.
        mode (int): Mode of correction (PDDL 1 or PDDL 2)

    Returns:
        list: Grading results for each student file.
    """
    results = []
    # Process each student's submission
    for filename in tqdm(os.listdir(directory)):
        if filename.endswith(".pddl"):
            student = os.path.splitext(filename)[0]
            student_name = student.split("_")[:2]
            # Solve the student's problem using their domain/problem and fixed problem/domain
            student_file_path = os.path.join(directory, filename)
            if mode == 1:
                student_plan = solve_pddl(student_file_path, baseline_file_path)
            else: 
                student_plan = solve_pddl(baseline_file_path, student_file_path)

            # Determine pass/fail
            if student_plan is not None and compare_plans(student_plan, baseline_plan):
                results.append([student_name[0], student_name[1], "Pass"])
            else:
                results.append([student_name[0], student_name[1], "Fail"])

def grade_problem_files(directory, domain_file_path, baseline_plan):
    """
    Grades all the PDDL files in a directory.

    Args:
        directory (str): Path to the directory containing the PDDL files
        problem_file (str): The problem file's path.
        baseline_plan (str): The baseline solution.

    Returns:
        list: Grading results for each student file.
    """
    results = []
    # Process each student's submission
    for filename in tqdm(os.listdir(directory)):
        if filename.endswith(".pddl"):
            student = os.path.splitext(filename)[0]
            student_name = student.split("_")[:2]
            # Solve the student's problem using their problem and fixed domain
            student_problem_path = os.path.join(directory, filename)
            student_plan = solve_pddl(domain_file_path, student_problem_path)

            # Determine pass/fail
            if student_plan is not None and compare_plans(student_plan, baseline_plan):
                results.append([student_name[0], student_name[1], "Pass"])
            else:
                results.append([student_name[0], student_name[1], "Fail"])

def main(mode):
    pddl_1_submissions = "./pddl_1_submissions"  # Directory with student domain files
    pddl_2_submissions = "./pddl_2_submissions" # Directory with student problem files
    pddl_1_grades = "pddl_1_grades.csv"  # Output CSV file for PDDL 1
    pddl_2_grades = "pddl_2_grades.csv" # Output CSV file for PDDL 2

    baseline_problem_1_file = "./baseline_problem_1.pddl"  # Fixed baseline problem file (for PDDL 1)
    baseline_problem_2_file = "./baseline_problem_2.pddl"  # Fixed baseline problem file (for PDDL 2)
    baseline_domain_file = "./baseline_domain.pddl" # Fixed baseline domain file (for PDDL 1 and 2)

    baseline_solutions_path = "./pddl_accepted_solutions.txt"  # Directory of baseline solutions, in case the solution is not unique
    
    if mode == 1:
        student_dir = pddl_1_submissions
        baseline_plan = solve_pddl(baseline_domain_file, baseline_problem_1_file)
        baseline_file = baseline_problem_1_file
        output_csv = pddl_1_grades
    else: 
        student_dir = pddl_2_submissions
        baseline_plan = solve_pddl(baseline_domain_file, baseline_problem_2_file)
        baseline_file = baseline_domain_file
        output_csv = pddl_2_grades

    if baseline_plan is None:
        print("Error: Could not retrieve baseline solution.")
        return

    # Grade files
    results = grade_pddl_files(student_dir, baseline_file, baseline_plan, mode)

    # Sort the students by their Last Name
    sorted_results = sorted(results, key = lambda x: x[0].lower())

    # Write results to a CSV file
    with open(output_csv, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Last Name", "First Name", "Result"])
        csv_writer.writerows(sorted_results)

    print(f"Grading completed. Results saved to {output_csv}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Grade PDDL student submissions.")
    parser.add_argument(
        "--mode", 
        type=int, 
        choices=[1, 2], 
        required=True, 
        help="Select grading mode: 1 for PDDL 1, 2 for PDDL 2."
    )
    
    # Parse arguments
    args = parser.parse_args()

    # Call main with parsed mode
    main(mode=args.mode)
