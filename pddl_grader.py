import os
import requests
import csv
from tqdm import tqdm
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import threading

ACCEPTED_SOLUTIONS = set() # Set of accepted solutions (filled interactively)
REJECTED_SOLUTIONS = set() # Set of rejected solutions (filled interactively)

SOLUTION_LOCK = threading.Lock() 

def rename_files(directory):

    for filename in tqdm(os.listdir(directory)):
        try:
            file_path = os.path.join(directory, filename)

            processed_filename = "_".join(filename.split("_")[3:])

            processed_file_path = os.path.join(directory, processed_filename)

            os.rename(file_path, processed_file_path)

        except Exception as e:
            print(f"Error renaming file {filename}: {e}")

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
            return None

    return plan

def compare_plans(student_plan, baseline_plan):
    """
    Compare the student's plan with the baseline plan.
    """
    return student_plan == baseline_plan

def process_student_file(student_file_path, baseline_file_path, baseline_plan, mode):
    """
    Processes a single student's PDDL file.
    """

    student = os.path.splitext(os.path.basename(student_file_path))[0]
    student_name = student.split("_")[:2]

    if mode == 1:
        student_plan = solve_pddl(student_file_path, baseline_file_path)
    else: 
        student_plan = solve_pddl(baseline_file_path, student_file_path)

    # Determine pass/fail
    if student_plan is None: 
        result = "Fail"
        reason = "Runtime Error"

    elif compare_plans(student_plan, baseline_plan):
        result = "Pass"
        reason = ""

    else:
        result = "Fail"
        reason = "Wrong Answer (Unknown)"

    return student_name[0], student_name[1], result, reason, student_plan

def handle_unknown_solution(solution):
    with SOLUTION_LOCK:
        if solution in REJECTED_SOLUTIONS:
            return "Fail", "Rejected"
        
        elif solution in ACCEPTED_SOLUTIONS:
            return "Pass", ""

        print(f"\nUnknown solution encountered:\n{solution}\n")

        user_input = input("Accept this solution? (y/n): ").strip().lower()
        while user_input not in ('y', 'n'):
            user_input = input("Please enter 'y' for yes or 'n' for no: ").strip().lower()

        if user_input == 'y':
            ACCEPTED_SOLUTIONS.add(solution)
            return "Pass", ""
        else:
            REJECTED_SOLUTIONS.add(solution)
            return "Fail", "Rejected"


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
    student_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".pddl")]
        
    # Process files in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_file = {
            executor.submit(process_student_file, file, baseline_file_path, baseline_plan, mode): file
            for file in student_files
        }

        for future in tqdm(as_completed(future_to_file), total=len(student_files)):
            try: 
                student_last_name, student_first_name, result, reason, student_plan = future.result()

                if result == "Fail" and reason == "Wrong Answer (Unknown)":
                    result, reason = handle_unknown_solution(student_plan)

                
                results.append([student_last_name, student_first_name, result, reason])
                
            except Exception as e:
                print(f"Error processing file {future_to_file[future]}: {e}")
            
    return results    

def main(mode, file, rename, init_solutions):
    pddl_1_submissions = "./pddl_1_submissions"  # Directory with student domain files
    pddl_2_submissions = "./pddl_2_submissions" # Directory with student problem files
    pddl_1_grades = "pddl_1_grades.csv"  # Output CSV file for PDDL 1
    pddl_2_grades = "pddl_2_grades.csv" # Output CSV file for PDDL 2

    baseline_problem_1_file = "./baseline_problem_1.pddl"  # Fixed baseline problem file (for PDDL 1)
    baseline_problem_2_file = "./baseline_problem_2.pddl"  # Fixed baseline problem file (for PDDL 2)
    baseline_domain_file = "./baseline_domain.pddl" # Fixed baseline domain file (for PDDL 1 and 2)   

    accepted_solutions_file_1 = "accepted_solutions_1.json"
    rejected_solutions_file_1 = "rejected_solutions_1.json"
    accepted_solutions_file_2 = "accepted_solutions_2.json"
    rejected_solutions_file_2 = "rejected_solutions_2.json"

    if mode == 1:
        baseline_plan = solve_pddl(baseline_domain_file, baseline_problem_1_file)
        accepted_solutions_file = accepted_solutions_file_1
        rejected_solutions_file = rejected_solutions_file_1  
        if file:
            print(process_student_file(file, baseline_problem_1_file, baseline_plan, mode))
            #student_plan = solve_pddl(file, baseline_problem_1_file)
            #print(f"Student Plan:\n{student_plan}")
            return
        else:
            student_dir = pddl_1_submissions
            baseline_file = baseline_problem_1_file
            output_csv = pddl_1_grades

    else: 
        baseline_plan = solve_pddl(baseline_domain_file, baseline_problem_2_file)
        accepted_solutions_file = accepted_solutions_file_2
        rejected_solutions_file = rejected_solutions_file_2
        if file:
            print(process_student_file(file, baseline_domain_file, baseline_plan, mode))
            #student_plan = solve_pddl(baseline_domain_file, file)
            #print(f"Student Plan:\n{student_plan}")
            return
        else:
            student_dir = pddl_2_submissions
            baseline_file = baseline_domain_file
            output_csv = pddl_2_grades            
        
    if init_solutions:
        print("Initializing accepted and rejected solutions from file...")
        if os.path.exists(accepted_solutions_file):
            with open(accepted_solutions_file, "r") as f:
                ACCEPTED_SOLUTIONS = set(json.load(f))
            print(f"Loaded {len(ACCEPTED_SOLUTIONS)} accepted solutions.")
        else:
            print("Accepted solutions file not found. Initializing empty set.")

        # Load rejected solutions
        if os.path.exists(rejected_solutions_file):
            with open(rejected_solutions_file, "r") as f:
                REJECTED_SOLUTIONS = set(json.load(f))
            print(f"Loaded {len(REJECTED_SOLUTIONS)} rejected solutions.")
        else:
            print("Rejected solutions file not found. Initializing empty set.")

    if baseline_plan is None:
        print("Error: Could not retrieve baseline solution.")
        return

    # Preprocess the files to follow the requested naming convention.
    if(rename):
        rename_files(student_dir)

    # Grade files
    results = grade_pddl_files(student_dir, baseline_file, baseline_plan, mode)

    # Sort the students by their Last Name
    sorted_results = sorted(results, key = lambda x: x[0].lower())

     # Save accepted and rejected solutions to files
    with open(accepted_solutions_file, 'w') as accepted_output:
        json.dump(list(ACCEPTED_SOLUTIONS), accepted_output, indent=4)

    with open(rejected_solutions_file, 'w') as rejected_output:
        json.dump(list(REJECTED_SOLUTIONS), rejected_output, indent=4)

    # Write results to a CSV file
    with open(output_csv, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Last Name", "First Name", "Result", "Reason"])
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
    parser.add_argument(
        "--file",
        type=str,
        help="Path to a single PDDL file to be graded."
    )
    parser.add_argument(
        "--rename",
        action="store_true",
        help="Rename the Canvas Dump files before grading."
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize the accepted and rejected solutions."
    )
    
    # Parse arguments
    args = parser.parse_args()

    # Call main with parsed mode
    main(mode=args.mode, file=args.file, rename=args.rename, init_solutions=args.init)
