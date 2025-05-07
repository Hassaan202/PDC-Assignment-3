#!/usr/bin/env python3

import subprocess
import os
import json
import shutil
import re
import math

# perf_pts = 7 # Retained for potential future use, but not used in current scoring
correctness_pts = 2

# scene_names = ["rgb", "rgby", "rand10k", "rand100k", "biglittle", "littlebig", "pattern","bouncingballs", "hypnosis", "fireworks", "snow", "snowsingle", "rand1M", "micro2M"]
# score_scene_names_list = ["rgb", "rand10k", "rand100k", "pattern", "snowsingle", "biglittle", "rand1M", "micro2M"]
scene_names = [
    "rgb",
    "rand10k",
    "rand100k",
    "pattern",
    "snowsingle",
    "biglittle",
    "rand1M",
    "micro2M",
]
score_scene_names_list = [ # Scenes for which student's time will be measured and displayed
    "rgb",
    "rand10k",
    "rand100k",
    "pattern",
    "snowsingle",
    "biglittle",
    "rand1M",
    "micro2M",
]
score_scene_names = set(score_scene_names_list)

#### LOGS MANAGEMENT ####
# Set up a new logs dir (remove old logs dir, create new logs dir)
if os.path.isdir("logs"):
    shutil.rmtree("logs")
os.mkdir("logs")
if os.environ.get("GRADING_TOKEN"):
    subprocess.run("chown -R nobody:nogroup logs", shell=True)


# Helper functions to convert scene names to appropriate log file names
def correctness_log_file(scene):
    return "./logs/correctness_%s.log" % scene


def time_log_file(scene):
    # This log file will now only be for the student's render times
    return "./logs/time_student_%s.log" % scene


#### END OF LOGS MANAGEMENT ####


#### RUNNING THE RENDERERS ####
def check_correctness(render_cmd, scene):
    # This function now only runs the student's renderer ("render")
    cmd_string = "./%s -c %s -s 1024 -f logs/output > %s" % (
        render_cmd, # Should always be "render"
        scene,
        correctness_log_file(scene),
    )
    # print("Checking correctness: %s" % cmd_string)

    # Actually run it
    if os.environ.get("GRADING_TOKEN"):
        result = subprocess.run([cmd_string], shell=True, user="nobody", env={})
    else:
        result = subprocess.run([cmd_string], shell=True)

    return result.returncode == 0


# Run a renderer one time and get the time taken
def get_time(render_cmd, scene):
    # This function now only gets time for the student's renderer ("render")
    # print("get_time %s %s" % (render_cmd, scene))
    cmd_string = (
        "./%s -r cuda -b 0:4 %s -s 1024 -f logs/output | tee %s | grep Total:"
        % (
            render_cmd, # Should always be "render"
            scene,
            time_log_file(scene), # Log file named for student
        )
    )

    # Actually run the renderer
    if os.environ.get("GRADING_TOKEN"):
        result = subprocess.run(
            [cmd_string], shell=True, capture_output=True, user="nobody", env={}
        )
    else:
        result = subprocess.run([cmd_string], shell=True, capture_output=True)

    # Extract the time taken
    # This assumes the student's "./render" command outputs a line like "Total: <time_float>"
    search_result = re.search(r"\d+\.\d+", str(result.stdout))
    if search_result:
        time = float(search_result.group())
    else:
        print(f"WARNING: Could not parse time for {render_cmd} on scene {scene}. Output: {result.stdout}")
        time = -1.0 # Placeholder for error
    return time


#### END OF RUNNING THE RENDERERS ####


# Run all scenes for the student's solution.
def run_scenes(n_runs):
    correct = {}
    stu_times = {}
    for scene in scene_names:
        print("\nRunning scene: %s..." % (scene))

        # Check for correctness using student's renderer
        correct[scene] = check_correctness("render", scene)
        if not correct[scene]:
            print(
                "[%s] Correctness failed ... Check %s"
                % (scene, correctness_log_file(scene))
            )
        else:
            print("[%s] Correctness passed!" % scene)

        # Get student's performance times
        if scene in score_scene_names:
            current_scene_times = []
            for _ in range(n_runs):
                time_val = get_time("render", scene)
                if time_val >= 0: # Add time only if successfully parsed
                    current_scene_times.append(time_val)
            
            if current_scene_times: # only populate if we got valid times
                 stu_times[scene] = current_scene_times
            else: # if all runs failed to get time
                 stu_times[scene] = [-1.0] * n_runs # or some other error indicator

            print("[%s] Student times: " % (scene), stu_times.get(scene, "N/A (Time parsing failed)"))

    return correct, stu_times


# Calculate scores based on student's correctness and time
def score_calculate(correct, stu_times):
    scores = []
    for scene in score_scene_names_list:
        min_stu_time_val = "N/A"
        if scene in stu_times and stu_times[scene]:
            valid_times = [t for t in stu_times[scene] if t >= 0]
            if valid_times:
                min_stu_time_val = min(valid_times)
            else: # All time measurements failed for this scene
                min_stu_time_val = "Error"
        
        current_score = 0
        is_correct = correct.get(scene, False)
        if is_correct:
            current_score = correctness_pts
        
        scores.append(
            {
                "scene": scene,
                "correct": is_correct,
                "stu_time": min_stu_time_val,
                "score": current_score, # Score is now based only on correctness_pts
            }
        )
    return scores

# Display score table with student information only
def score_table(correct, stu_times):
    print("---------------------------------------------------------") # Adjusted dashes for new table width
    print("Score table (Student Information Only):")
    print("---------------------------------------------------------")
    header = "| %-15s | %-11s | %-20s | %-7s |" % (
        "Scene Name",
        "Correct",
        "Your Time (T) (sec)", # Clarified unit
        "Score",
    )
    dashes = "-" * len(header)
    print(dashes)
    print(header)
    print(dashes)

    scores_data = score_calculate(correct, stu_times)
    total_score = 0

    for item in scores_data:
        scene = item["scene"]
        is_correct_str = "Passed" if item["correct"] else "Failed"
        
        stu_time_val = item["stu_time"]
        
        if item["correct"]:
            if isinstance(stu_time_val, float):
                 actual_stu_time_display = "%.4f" % stu_time_val
            else: # Handles "N/A" or "Error"
                 actual_stu_time_display = str(stu_time_val)
        else:
            actual_stu_time_display = "(Correctness Failed)"

        score_val = item["score"]

        print("| %-15s | %-11s | %-20s | %-7s |" % (scene, is_correct_str, actual_stu_time_display, score_val))
        total_score += score_val

    print(dashes)

    max_total_score = correctness_pts * len(score_scene_names_list)
    score_string = "%s/%s" % (total_score, max_total_score)
    print("| %-15s   %-11s | %-20s | %-7s |" % ("", "", "Total score:", score_string))

    print(dashes)


# Main execution block
correct, stu_times = run_scenes(3) # Only student's data is returned

GRADING_TOKEN = os.environ.get("GRADING_TOKEN")
if not GRADING_TOKEN:
    score_table(correct, stu_times) # Pass only student's data
else:
    # When a grading token is present, output JSON
    # The score_calculate function now produces data without ref_times
    scores_data_for_grading = score_calculate(correct, stu_times)
    print(f"{GRADING_TOKEN}{json.dumps(scores_data_for_grading)}")