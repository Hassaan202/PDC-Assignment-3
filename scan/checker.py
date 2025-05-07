#!/usr/bin/env python3

import subprocess
import os
import re
import sys
import json
import platform

element_counts = ["1000000", "10000000", "20000000", "40000000"]
perf_points = 1.25

# Set up logs directories
os.makedirs("logs/test", exist_ok=True)
os.makedirs("logs/ref", exist_ok=True)
subprocess.run("rm -rf logs/*", shell=True)
os.makedirs("logs/test", exist_ok=True)
os.makedirs("logs/ref", exist_ok=True)
if os.environ.get("GRADING_TOKEN"):
    subprocess.run("chown -R nobody:nogroup logs", shell=True)

# Command-line argument check
if len(sys.argv) != 2 or sys.argv[1] not in ["find_repeats", "scan"]:
    print("Usage: python3 checker.py <test>: test = scan, find_repeats")
    sys.exit(1)
else:
    test = sys.argv[1]
    print(f"Test: {test}")

print("\n--------------")
print("Running tests:")
print("--------------")

def check_correctness(test, element_count):
    cmd = f"./cudaScan -m {test} -i random -n {element_count} > ./logs/test/{test}_correctness_{element_count}.log"
    if os.environ.get("GRADING_TOKEN"):
        result = subprocess.run(cmd, shell=True, user="nobody", env={})
    else:
        result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def get_time(command):
    if os.environ.get("GRADING_TOKEN"):
        result = subprocess.run(command, shell=True, capture_output=True, user="nobody", env={})
    else:
        result = subprocess.run(command, shell=True, capture_output=True)
    out = result.stdout.decode()
    match = re.search(r"\d+(\.\d+)?", out)
    return float(match.group()) if match else None


def run_tests():
    correct = {}
    your_times = {}
    fast_times = {}

    for element_count in element_counts:
        print(f"\nElement Count: {element_count}")

        # Check correctness
        correct[element_count] = check_correctness(test, element_count)
        print("Correctness passed!" if correct[element_count] else "Correctness failed")

        # Student time
        student_cmd = (
            f"./cudaScan -m {test} -i random -n {element_count} | grep 'Student GPU time:'"
        )
        your_times[element_count] = get_time(student_cmd)
        print(f"Student Time: {your_times[element_count]}")

        # Reference binary selection
        ref_binary = (
            "cudaScan_ref_x86" if platform.machine() == "x86_64" else "cudaScan_ref"
        )
        # Reference time
        ref_cmd = (
            f"./{ref_binary} -m {test} -i random -n {element_count} | grep 'Student GPU time:'"
        )
        fast_times[element_count] = get_time(ref_cmd)
        print(f"Ref Time: {fast_times[element_count]}")

    return correct, your_times, fast_times


def calculate_scores(correct, your_times, fast_times):
    scores = []
    total_score = 0.0

    for element_count in element_counts:
        ref_time = fast_times.get(element_count)
        stu_time = your_times.get(element_count)

        if not correct.get(element_count, False):
            score = 0.0
        elif ref_time is None or stu_time is None:
            print(f"Warning: Missing timing for element count {element_count}, assigning score 0.")
            score = 0.0
        else:
            if stu_time <= 1.20 * ref_time:
                score = perf_points
            else:
                score = perf_points * (ref_time / stu_time)

        scores.append({
            "element_count": element_count,
            "correct": correct[element_count],
            "ref_time": ref_time,
            "stu_time": stu_time,
            "score": score,
        })
        total_score += score

    max_total = perf_points * len(element_counts)
    return scores, total_score, max_total


def print_score_table(scores, total, max_total):
    print("\n-------------------------")
    print(f"{test.capitalize()} Score Table:")
    print("-------------------------")
    header = f"| {'Element Count':<15} | {'Ref Time':<15} | {'Student Time':<15} | {'Score':<15} |"
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    for s in scores:
        elem = s['element_count']
        rt = s['ref_time'] if s['ref_time'] is not None else 'N/A'
        st = s['stu_time'] if s['stu_time'] is not None else 'N/A'
        sc = s['score']
        print(f"| {elem:<15} | {rt:<15} | {st:<15} | {sc:<15} |")
    print("-" * len(header))
    print(f"| {'':<33} | {'Total score:':<15} | {total}/{max_total:<15} |")
    print("-" * len(header))


# Main execution
correct, your_times, fast_times = run_tests()
scores, total_score, max_total_score = calculate_scores(correct, your_times, fast_times)

if not os.environ.get("GRADING_TOKEN"):
    print_score_table(scores, total_score, max_total_score)
else:
    print(os.environ.get("GRADING_TOKEN") + json.dumps(scores))
