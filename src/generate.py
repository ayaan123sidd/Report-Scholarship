import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pdfkit
from PyPDF2 import PdfMerger
from services import ExerciseService, ReportService
from utils.helpers import (
    generate_front_page,
    split_label,
    get_class_and_test_id,
    process_question_data,
    calculate_sum_marks,
    calculate_counts,
    calculate_passing_probability,
    calculate_time_efficiency,
    get_qualification_data,
    get_scholarship_data
)
from utils.constants import LMS_API_HEADERS, WKHTMLTOPDF_PATH, CUSTOM_TOP_10_STUDENTS_TIME_TAKEN
import traceback


try:
    student_id = ""
    qualification = ""
    scholarship = ""

    if len(sys.argv) != 4:
        raise Exception("Incorrect number of arguments")
        
    student_id = sys.argv[1]
    qualification = sys.argv[2]
    scholarship = sys.argv[3]

    classId, testId = get_class_and_test_id(qualification, scholarship)

    exercise_service = ExerciseService(LMS_API_HEADERS)

    data = exercise_service.get_attempt_data(testId, classId, student_id)

    if data["code"] == 200 and data["message"] == "Exercise Retrieved":
        attempt_id = data["exercises"][0]["attempt_id"]
    else:
        raise Exception("Failed to retrieve exercises")

    exercise_data = exercise_service.get_exercise_data(attempt_id)
    test_parts = exercise_data["exercise"]["test_parts"]
    marks_array, time_taken_array = process_question_data(test_parts, qualification, scholarship)

    qualification_data = get_qualification_data(qualification)
    if qualification_data is None:
        raise Exception("Qualification data not found")
    
    subject_data = get_scholarship_data(qualification, scholarship)
    if subject_data is None:
        raise Exception("Subject data not found")

    topics = qualification_data.get("topics", [])
    max_time = subject_data.get("max_time", 60)
    max_subject_marks = subject_data.get("total_marks", 50)

    # Extract the total questions for each topic
    topic_question_idx = 0
    total_questions_per_topic = [
        len(topic.get("total_questions", [])) for topic in topics
    ]

    topics_data = []
    for topic in topics:
        topic_name = topic["name"]
        topic_questions = int(topic["total_questions"] or 0)
        topic_marks = marks_array[
            topic_question_idx : topic_question_idx + topic_questions
        ]
        topic_time_taken = time_taken_array[
            topic_question_idx : topic_question_idx + topic_questions
        ]
        topic_question_idx += topic_questions

        (
            total,
            correct,
            incorrect,
            unattempted,
            correct_percentage,
            incorrect_percentage,
            unattempted_percentage,
        ) = calculate_counts(topic_marks)

        total_marks = calculate_sum_marks(topic_marks)
    
        avg_time_taken = sum(topic_time_taken) / len(topic_time_taken)
        
        # Calculate time efficiency for the topic
        max_marks = total  
        marks_scored = total_marks
        time_taken = avg_time_taken 

        efficiency = calculate_time_efficiency(max_marks, marks_scored, max_time, time_taken)

        topics_data.append(
            {
                "name": topic_name,
                "total": total,
                "marks_array": topic_marks,
                "time_taken": topic_time_taken,
                "correct_counts": correct,
                "incorrect_counts": incorrect,
                "unattempted_counts": unattempted,
                "marks": calculate_sum_marks(topic_marks),
                "correct_percentage": correct_percentage,
                "incorrect_percentage": incorrect_percentage,
                "unattempted_percentage": unattempted_percentage,
                "avg_time": sum(topic_time_taken) / len(topic_time_taken),
                "time_efficiency": efficiency,
            }
        )

    report_service = ReportService(LMS_API_HEADERS)
    class_progress_report_data = report_service.get_class_progress_report(
        classId
    )  # PER PAGE DATA IS HARDCODED
    users_array_size = len(class_progress_report_data["class_report"]["user_marks"])

    # Extract user data
    users_data = class_progress_report_data["class_report"]["users"]
    users_df = pd.DataFrame(
        users_data, columns=["student_id", "student_name", "student_username"]
    )

    # Extract user marks data
    user_marks_data = class_progress_report_data["class_report"]["user_marks"]

    given_student_id = int(student_id)

    def rank_students():
        marks_dict = {}  # Dictionary to store students based on their marks
        for student_id in users_df["student_id"]:
            marks = marks_analysis(student_id)
            if marks not in marks_dict:
                marks_dict[marks] = []
            marks_dict[marks].append(student_id)

        # Sort the dictionary keys in descending order
        sorted_marks = sorted(marks_dict.keys(), reverse=True)

        ranked_students = []  # List to store (student_id, rank) tuples
        
        rank = 1  # HARDCODED DATA
        for marks in sorted_marks:
            student_ids = marks_dict[marks]
            for student_id in student_ids:
                ranked_students.append((student_id, rank))
            rank += len(student_ids)
        return ranked_students

    def find_student_rank(student_id):
        ranked_students = rank_students()
        for student, rank in ranked_students:
            if student == student_id:
                return rank
        raise Exception("Student ID not found in ranked list")

    def average_marks():
        marks_list = [
            marks_analysis(student_id) for student_id in users_df["student_id"]
        ]
        return round(sum(marks_list) / len(marks_list), 2)

    def average_time_taken():
        time_list = [
            time_taken_analysis(student_id) for student_id in users_df["student_id"]
        ]
        return round(sum(time_list) / len(time_list), 2)

    def average_accuracy():
        accuracy_list = [
            accuracy_analysis(student_id) for student_id in users_df["student_id"]
        ]
        return round(sum(accuracy_list) / len(accuracy_list), 2)

    def average_percent():
        accuracy_list = [
            percent_analysis(student_id) for student_id in users_df["student_id"]
        ]
        return round(sum(accuracy_list) / len(accuracy_list), 2)

    def average_time_efficiency():
        time_efficiency_list = [
            time_efficiency(student_id)
            for student_id in users_df["student_id"]
            if time_efficiency(student_id) is not None
        ]
        if len(time_efficiency_list) == 0:
            return None  # or return 0 or any other value as appropriate
        else:
            return round(sum(time_efficiency_list) / len(time_efficiency_list), 2)

    # Create a DataFrame for user data
    users_df = pd.DataFrame(
        users_data, columns=["student_id", "student_name", "student_username"]
    )

    # Define a function to extract marks data for a given student
    def extract_marks(student_id):
        marks_data = user_marks_data[str(student_id)]
        return marks_data

    # Define a function to get student name by ID
    def get_student_name(student_id):
        for user in users_data:
            if user[0] == student_id:
                return user[1]
        return None

    def rank_students():
        marks_dict = {}  # Dictionary to store students based on their marks
        for student_id in users_df["student_id"]:
            marks = marks_analysis(student_id)
            if marks not in marks_dict:
                marks_dict[marks] = []
            marks_dict[marks].append(student_id)

        # Sort the dictionary keys in descending order
        sorted_marks = sorted(marks_dict.keys(), reverse=True)

        ranked_students = []  # List to store (student_id, rank) tuples

        rank = 1
        for marks in sorted_marks:
            student_ids = marks_dict[marks]
            for student_id in student_ids:
                ranked_students.append((student_id, rank))
            rank += len(student_ids)
        return ranked_students

    def find_student_rank(student_id):
        ranked_students = rank_students()
        for student, rank in ranked_students:
            if student == student_id:
                return rank
        return None  # Student ID not found in ranked list

    # Define a function to sort users based on maximum marks
    def sort_users_by_max_marks():
        marks_dict = {}
        for user in users_data:
            marks_data = extract_marks(user[0])
            marks_dict[user[0]] = int(marks_data[0]["mk"])
        sorted_users = sorted(marks_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        sorted_user_ids = [user[0] for user in sorted_users]
        return sorted_user_ids

    # Define functions to get performance metrics for a given student ID
    def percent_analysis(student_id):
        marks_data = extract_marks(student_id)
        accuracy = (int(marks_data[0]["mk"]) * 100) / 50  # change marks here
        return accuracy
    
    def percent_analysis_for_current_student():
        correct_counts = sum(topic.get("correct_counts", 0) for topic in topics_data)
        total_counts = sum(topic.get("total", 0) for topic in topics_data)

        return (correct_counts/total_counts) * 100

    def accuracy_analysis(student_id):
        marks_data = extract_marks(student_id)
        # HARD CODED (only take 1st array)
        accuracy = int(float(marks_data[0]["gr"]))
        return accuracy
    
    def accuracy_analysis_for_current_student():
        correct_counts = sum(topic.get("correct_counts") for topic in topics_data)
        incorrect_counts = sum(topic.get("incorrect_counts") for topic in topics_data)
        total_counts = correct_counts + incorrect_counts

        return (correct_counts/total_counts) * 100

    def marks_analysis(student_id):
        marks_data = extract_marks(student_id)
        marks = int(marks_data[0]["mk"])
        return marks

    # Define a function to analyze marks for a given student
    def marks_analysis2(student_id):
        marks_data = extract_marks(student_id)

        if not marks_data:
            return 0, 0

        marks_scored = sum(int(mark.get("mk", 0) or 0) for mark in marks_data)
        total_marks = sum(int(mark.get("tm", 0) or 0) for mark in marks_data)
        return marks_scored, total_marks


    def points_percentage_analysis(student_id):
        marks_data = extract_marks(student_id)
        points_percentage = float(marks_data[0]["pt"])
        return points_percentage

    def time_taken_analysis(student_id):
        marks_data = extract_marks(student_id)
        time_taken_seconds = int(marks_data[0]["tttm"])
        time_taken_minutes = time_taken_seconds / 60  # Convert seconds to minutes
        return time_taken_minutes

    def sort_users_by_time_taken():
        time_dict = {}
        for user in users_data:
            time_data = time_taken_analysis(user[0])
            time_dict[user[0]] = time_data
        sorted_users = sorted(time_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        sorted_user_ids = [user[0] for user in sorted_users]
        return sorted_user_ids

    def custom_visualize_time_taken_top_users():
        candidate_name = get_student_name(given_student_id)
        candidate_time = time_taken_analysis(given_student_id)
        
        # Combine candidate's data with the rest of the students' data
        time_taken_students = CUSTOM_TOP_10_STUDENTS_TIME_TAKEN.copy()
        time_taken_students.append(candidate_time)
        time_taken_students.sort(reverse=True)

        fig = plt.figure(figsize=(8.35, 6))
        ax = fig.add_subplot(111)

        # Plot the combined data
        sns.lineplot(ax=ax, x=range(len(time_taken_students)), y=time_taken_students, marker="o")

        # Highlight the candidate's point
        ax.plot(
            time_taken_students.index(candidate_time),
            candidate_time,
            "ro",
            label=f"Candidate: ({candidate_name})",
        )

        # Add max time horizontal line
        ax.axhline(max_time, color='blue', linestyle='--', label=f'Max Time: {max_time} minutes')

        ax.set_title("Time Taken Analysis (Top 10 Students)", fontweight="bold")
        ax.set_xlabel("Students")
        ax.set_ylabel("Time Taken (minutes)")
        ax.set_xticks([])
        ax.legend(loc="best")
        
        return fig


    # Define a function to visualize time taken for top users using seaborn
    def visualize_time_taken_top_users():
        sorted_user_ids = sort_users_by_time_taken()
        time_data = {
            get_student_name(student_id): time_taken_analysis(student_id)
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(8.82, 6))
        ax = fig.add_subplot(111)

        # Get the reversed list of data points
        reversed_data = list(time_data.values())[::-1]
        reversed_names = list(time_data.keys())[::-1]

        ax.plot(
            [get_student_name(given_student_id)],
            [time_taken_analysis(given_student_id)],
            "ro",
            label=f"Candidate: ({get_student_name(given_student_id)})",
        )

        sns.lineplot(ax=ax, x=reversed_names, y=reversed_data, marker="o")

        ax.set_title("Time Taken Analysis (Top 10 Students)", fontweight="bold")
        ax.set_xlabel("Students")
        ax.set_ylabel("Time Taken (minutes)")
        ax.set_xticks(range(len(time_data)))
        # ax.set_xticklabels(reversed_names, rotation=45)
        ax.set_xticks([])
        ax.legend()
        return fig

    # Call the function to get the figure object
    time_taken_fig = visualize_time_taken_top_users()

    def time_efficiency(student_id):
        marks_data = marks_analysis2(student_id)
        if marks_data is None:
            return None
        marks_scored, total_marks = marks_data
        time_taken = time_taken_analysis(student_id)

        # Calculate efficiency within 100%
        efficiency = calculate_time_efficiency(total_marks, marks_scored, max_time, time_taken)
        return efficiency

    def visualize_time_efficiency_top_users():
        sorted_user_ids = sort_users_by_time_taken()
        efficiency_data = {
            get_student_name(student_id): time_efficiency(student_id)
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(9.52, 6))
        ax = fig.add_subplot(111)
        sorted_names = list(efficiency_data.keys())
        sorted_values = list(efficiency_data.values())
        ax.barh(sorted_names, sorted_values, color="skyblue")
        # Plot for given student
        given_student_name = get_student_name(given_student_id)
        given_student_efficiency = time_efficiency(given_student_id)
        ax.barh(
            [given_student_name],
            [given_student_efficiency],
            color="red",
            label=f"Candidate: ({given_student_name})",
        )
        xPos = "right" if (given_student_efficiency - 0.5) > 25 else "left"
        ax.text(
            given_student_efficiency - 0.5,
            given_student_name,
            f"{given_student_efficiency:.2f}%",
            color="black",
            va="center",
            ha=xPos,
        )  # Write value inside the bar
        ax.set_title("Time Efficiency Analysis (Top 10 Students)", fontweight="bold")
        ax.set_xlabel("Time Efficiency (%)")
        ax.set_ylabel("Students")
        ax.legend(loc='best')
        ax.set_yticks([])
        return fig


    def visualize_points_percentage_top_users():
        sorted_user_ids = sort_users_by_max_marks()
        points_data = {
            get_student_name(student_id): points_percentage_analysis(student_id)
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(8.23, 6))
        ax = fig.add_subplot(555)
        for student_id in sorted_user_ids:
            student_name = get_student_name(student_id)
            ax.bar([student_name], [points_data[student_name]], color="skyblue")
        # Plot for given student
        ax.bar(
            [get_student_name(given_student_id)],
            [points_percentage_analysis(given_student_id)],
            color="red",
            label=f"Candidate: ({get_student_name(given_student_id)})",
        )
        ax.set_title("Points Percentage Analysis (Top 10 Students)")
        ax.set_xlabel("Students")
        ax.set_ylabel("Points Percentage")
        ax.set_xticks([])
        ax.legend()
        return fig

    def visualize_marks_top_users():
        sorted_user_ids = sort_users_by_max_marks()
        total_students = len(sorted_user_ids)
        marks_data = {
            get_student_name(student_id): marks_analysis(student_id)
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(9.5, 6))
        ax = fig.add_subplot(111)
        sorted_names = list(marks_data.keys())
        sorted_values = list(marks_data.values())
        ax.barh(sorted_names, sorted_values, color="skyblue")
        # Write values on the side of bars
        for index, (name, value) in enumerate(zip(sorted_names, sorted_values)):
            ax.text(value, index, str(value), va="center")  # Write value inside the bar
        # Plot for given student
        given_student_name = get_student_name(given_student_id)
        given_student_marks = marks_analysis(given_student_id)
        ax.barh(
            [given_student_name],
            [given_student_marks],
            color="red",
            label=f"Candidate: ({given_student_name})",
        )
        ax.text(
            given_student_marks,
            given_student_name,
            str(given_student_marks),
            color="black",
            va="center",
        )  # Write value inside the bar
        ax.set_title(f"Marks Analysis (Top {total_students} Students)", fontweight="bold")
        ax.set_xlabel("Marks Obtained")
        ax.set_ylabel(f"Top {total_students} Student")
        ax.legend()
        ax.set_yticks([])
        return fig, total_students

    def visualize_accuracy_top_users1():
        sorted_user_ids = sort_users_by_max_marks()
        accuracy_data = {
            get_student_name(student_id): accuracy_analysis(student_id)
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(8.82, 6))
        ax = fig.add_subplot(111)

        # Plot data points
        for student_id in sorted_user_ids:
            student_name = get_student_name(student_id)
            ax.plot(
                [student_name],
                [accuracy_data[student_name]],
                marker="o",
                color="skyblue",
            )

        # Include the given student's data point in the list
        sorted_names = [get_student_name(student_id) for student_id in sorted_user_ids]
        sorted_values = [accuracy_data[name] for name in sorted_names]
        sorted_names.append(
            get_student_name(given_student_id)
        )  # Add given student's name
        sorted_values.append(
            accuracy_analysis_for_current_student()
        )  # Add given student's data
        ax.plot(
            sorted_names, sorted_values, linestyle="--", color="grey"
        )  # Dotted line, grey color

        # Plot for given student
        ax.plot(
            [get_student_name(given_student_id)],
            [accuracy_analysis_for_current_student()],
            "ro",
            label=f"Candidate: ({get_student_name(given_student_id)})",
        )

        ax.set_title("Accuracy Analysis (Top 10 Students)")
        ax.set_xlabel("Students")
        ax.set_ylabel("Accuracy (%)")
        ax.set_xticks([])
        ax.legend()
        return fig

    def visualize_accuracy_top_users2():
        sorted_user_ids = sort_users_by_max_marks()
        accuracy_data = {
            get_student_name(student_id): accuracy_analysis(student_id) or 0
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(8.82, 6))
        ax = fig.add_subplot(111)

        # Plot data points
        for student_id in sorted_user_ids:
            student_name = get_student_name(student_id)
            if student_id == given_student_id and student_name in accuracy_data:
                # Plot the given student's data point only if they are in the top 10
                ax.plot(
                    [student_name],
                    [accuracy_data[student_name]],
                    "ro",
                    label=f"Candidate: ({student_name})",
                )
            else:
                ax.plot(
                    [student_name],
                    [accuracy_data[student_name]],
                    marker="o",
                    color="skyblue",
                )

        # Plot the line
        sorted_names = [get_student_name(student_id) for student_id in sorted_user_ids]
        sorted_values = [accuracy_data[name] for name in sorted_names]
        ax.plot(
            sorted_names, sorted_values, linestyle="--", color="grey"
        )  # Dotted line, grey color

        ax.set_title("Accuracy Analysis (Top 10 Students)")
        ax.set_xlabel("Students")
        ax.set_ylabel("Accuracy (%)")
        ax.set_xticks([])
        ax.legend()
        return fig

    def visualize_percent_top_users():
        sorted_user_ids = sort_users_by_max_marks()
        accuracy_data = {
            get_student_name(student_id): percent_analysis(student_id)
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(8.39, 6))
        ax = fig.add_subplot(111)

        # Plot data points
        for student_id in sorted_user_ids:
            student_name = get_student_name(student_id)
            ax.plot(
                [student_name],
                [accuracy_data[student_name]],
                marker="o",
                color="skyblue",
            )

        # Include the given student's data point in the list
        sorted_names = [get_student_name(student_id) for student_id in sorted_user_ids]
        sorted_values = [accuracy_data[name] for name in sorted_names]
        sorted_names.append(
            get_student_name(given_student_id)
        )  # Add given student's name
        sorted_values.append(
            percent_analysis_for_current_student()
        )  # Add given student's data
        sorted_values.sort(reverse=True)
        ax.plot(
            sorted_names, sorted_values, linestyle="--", color="grey"
        )  # Dotted line, grey color

        # Plot for given student
        ax.plot(
            [get_student_name(given_student_id)],
            [percent_analysis_for_current_student()],
            "ro",
            label=f"Candidate: ({get_student_name(given_student_id)})",
        )

        ax.set_title("Percentage Analysis (Top 10 Students)", fontweight="bold")
        ax.set_xlabel("Students")
        ax.set_ylabel("Accuracy (%)")
        ax.set_xticks([])
        ax.legend()
        return fig

    # Define a function to visualize performance for a given student ID
    def visualize_student_performance(student_id):
        # visualize_accuracy_top_users()
        visualize_percent_top_users()
        visualize_marks_top_users()
        visualize_points_percentage_top_users()
        visualize_time_taken_top_users()
        visualize_time_efficiency_top_users()

    # Call the function to visualize performance for the given student ID
    visualize_student_performance(given_student_id)

    # Set the style for seaborn plots
    sns.set(style="whitegrid")

    # Bar chart for sum of marks per topic
    topic_names = [topic.get("name", "").upper() for topic in topics]
    sum_marks = [topic.get("marks") for topic in topics_data]
    correct_counts = [topic.get("correct_counts") for topic in topics_data]
    incorrect_counts = [topic.get("incorrect_counts") for topic in topics_data]
    unattempted_counts = [topic.get("unattempted_counts") for topic in topics_data]

    plt.pie(
        correct_counts,
        labels=topic_names,
        autopct="%1.1f%%",
        colors=["lightgreen", "lightcoral", "lightblue", "lightyellow"],
    )
    # plt.title('Percentage of Correct Answers')

    # plt.subplot(1, 2, 2)
    plt.pie(
        incorrect_counts,
        labels=topic_names,
        autopct="%1.1f%%",
        colors=["lightcoral", "lightgreen", "lightblue", "lightyellow"],
    )

    topic_marks = [topic.get("marks_array") for topic in topics_data]
    total_marks_topicwise = [topic.get("marks") for topic in topics_data]
    average_time_taken_a = [np.mean(topic.get("time_taken")) for topic in topics_data]

    # Calculate percentages of correct, incorrect, and unattempted questions
    total_questions = len(marks_array)
    percent_correct = (marks_array.count(1) / total_questions) * 100
    percent_incorrect = (marks_array.count(0) / total_questions) * 100
    percent_unattempted = (marks_array.count(2) / total_questions) * 100

    # Plot Pie Chart for Percentage Correct, Incorrect, and Unattempted
    total_questions = len(marks_array)
    percent_correct = (marks_array.count(1) / total_questions) * 100
    percent_incorrect = (marks_array.count(0) / total_questions) * 100
    percent_unattempted = (marks_array.count(2) / total_questions) * 100

    # Plot Pie Chart for Percentage Correct, Incorrect, and Unattempted
    # labels = ['Correct', 'Incorrect', 'Unattempted']
    sizes = [percent_correct, percent_incorrect, percent_unattempted]
    colors = ["lightcoral", "lightskyblue", "lightgreen"]

    # Define section names
    sections = topic_names
    total_times = [sum(topic.get("time_taken")) / 60 for topic in topics_data]
    topicwise_marks = [topic.get("marks_array") for topic in topics_data]
    # Calculate the percentage of correct answers for each topic
    total_questions_per_topic = [len(topic_marks) for topic_marks in topicwise_marks]
    total_correct_per_topic = [
        sum(1 for mark in topic_marks if mark == 1) for topic_marks in topicwise_marks
    ]
    percentage_correct_topicwise = [
        (correct / total_questions) * 100
        for correct, total_questions in zip(
            total_correct_per_topic, total_questions_per_topic
        )
    ]

    def percentage_formatter(x, pos):
        return "{:.0f}%".format(x)

    plt.gca().yaxis.set_major_formatter(FuncFormatter(percentage_formatter))

    # Percentage
    total_questions_per_topic = [len(topic_marks) for topic_marks in topicwise_marks]
    total_correct_per_topic = [
        sum(1 for mark in topic_marks if mark == 1) for topic_marks in topicwise_marks
    ]
    percentage_correct_topicwise = [
        (correct / total_questions) * 100
        for correct, total_questions in zip(
            total_correct_per_topic, total_questions_per_topic
        )
    ]

    # Calculate percentage of incorrect answers for each topic
    total_incorrect_per_topic = [
        sum(1 for mark in topic_marks if mark == 0) for topic_marks in topicwise_marks
    ]
    percentage_incorrect_topicwise = [
        (incorrect / total_questions) * 100
        for incorrect, total_questions in zip(
            total_incorrect_per_topic, total_questions_per_topic
        )
    ]

    # Plot Percentage of Correct and Incorrect Answers Topic-wise
    bar_width = 0.35
    topics_bar = np.arange(len(topic_names))

    # Define the path to the file
    file_path = 'assets/pdfs/graphs_summary.pdf'
    directory = os.path.dirname(file_path)
    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    # Create the file if it does not exist
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as file:
            pass

    # Create a PDF file to save the plots
    with PdfPages(file_path) as pdf:
        plt.figure(figsize=(8.82, 6))
        bars = plt.barh(
            topic_names, total_marks_topicwise, color="skyblue", height=0.5
        )  # Use plt.barh for horizontal bar plot
        plt.title("Topic-Wise Total Marks (Correct Answers)", fontweight="bold")
        plt.xlabel("Total Correct Answers")
        plt.ylabel("Topics")

        # Split y-tick labels into two lines after a certain character limit
        ytick_labels = [
        (label.split(' ', 1)[0] + "\n" + label.split(' ', 1)[1]) if ' ' in label else label
        for label in topic_names
        ]
        ytick_labels = [label for label in ytick_labels]
        # Set y-tick labels with margin on the top
        plt.yticks(
            range(len(topic_names)), ytick_labels, rotation=0, ha="right", fontsize=8
        )

        plt.grid(axis="x", linestyle="--", alpha=0.7)  # Adjust grid lines along x-axis
        plt.tight_layout(pad=3.5)  # Add padding/margins around the plot

        summary = (
            "This graph indicates the total number of correct answers for each topic."
        )
        plt.figtext(0.5, 0.01, summary, wrap=True, ha="center", fontsize=8)
        plt.subplots_adjust(bottom=0.15)
        pdf.savefig(bbox_inches="tight", pad_inches=0.3)
        plt.close()

        plt.figure(figsize=(8.82, 6))
        bars = plt.barh(
            topic_names, average_time_taken_a, color="lightgreen", height=0.5
        )  # Use plt.barh for horizontal bar plot
        plt.title("Topic-Wise Average Time Taken Per Question", fontweight="bold")
        plt.xlabel("Average Time Taken (seconds)")
        plt.ylabel("Topics")

        # Set y-tick labels in uppercase and split into two lines after a certain character limit
        ytick_labels = [
        (label.split(' ', 1)[0] + "\n" + label.split(' ', 1)[1]) if ' ' in label else label
        for label in topic_names
        ]
        ytick_labels = [label for label in ytick_labels]

        # Set y-tick labels with margin on the right
        plt.yticks(
            range(len(topic_names)), ytick_labels, rotation=0, ha="right", fontsize=8
        )

        plt.grid(axis="x", linestyle="--", alpha=0.7)  # Adjust grid lines along x-axis
        plt.tight_layout(pad=3.5)  # Add padding/margins around the plot

        summary = "This graph indicates the average time taken per question for each topic."
        plt.figtext(
            0.5, 0.01, summary, wrap=True, ha="center", fontsize=8
        )  # Adjust figtext position for summary
        plt.subplots_adjust(bottom=0.15)
        pdf.savefig(bbox_inches="tight", pad_inches=0.3)
        plt.close()

        # Plot Pie Chart for Percentage Correct, Incorrect, and Unattempted Questions
        plt.figure(figsize=(9.05, 6))  # Keep figure size for better readability
        plt.pie(sizes, colors=colors, autopct="%1.1f%%", startangle=140)
        plt.title("Question Response Analysis", fontweight="bold", pad=20)
        plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.legend(
            loc="upper right",
            labels=["Correct", "Incorrect", "Unattempted"],
            fontsize=8,
        )
        plt.xlabel("Response Categories")  # Add x-axis label
        summary = "This pie chart shows the distribution of correct, incorrect, and unattempted questions."
        plt.figtext(0.5, 0.01, summary, wrap=True, ha="center", fontsize=8)
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        pdf.savefig(bbox_inches="tight", pad_inches=0.5)
        plt.close()


    # Plot Total Time Taken per Section
        # plt.figure(figsize=(8, 6))
        # plt.barh(sections, total_times, color="skyblue", height=0.5)
        # plt.title("Total Time Taken per Section")
        # plt.xlabel("Total Time Taken (minutes)")
        # plt.ylabel("Sections")

        # # Split y-tick labels into two lines after a whitespace
        # ytick_labels = [split_label(label) for label in sections]

        # # Set y-tick labels with margin on the right
        # plt.yticks(
        #     range(len(sections)), ytick_labels, fontsize=8, va="center", ha="right"
        # )

        # # Add a figure text with a summary
        # summary = "This graph indicates the total time taken per section in minutes."
        # plt.figtext(0.5, 0.03, summary, wrap=True, ha="center", fontsize=8)
        # plt.subplots_adjust(bottom=0.2)

        # pdf.savefig(bbox_inches="tight")  # Save the figure
        # plt.close()


    # Plot PERCENTAGE OF CORRECT ANSWERS TOPIC-WISE
        # plt.figure(figsize=(7, 6))
        # bars = plt.barh(
        #     topic_names, percentage_correct_topicwise, color="orange", height=0.5
        # )
        # plt.title(
        #     "PERCENTAGE OF CORRECT ANSWERS TOPIC-WISE", fontsize=10, fontweight="bold"
        # )  # Title in uppercase
        # plt.xlabel(
        #     "PERCENTAGE OF CORRECT ANSWERS", fontsize=8, fontweight="bold"
        # )  # X-axis label in uppercase
        # plt.ylabel("TOPICS", fontsize=8, fontweight="bold")  # Y-axis label in uppercase
        # plt.gca().xaxis.set_major_formatter(FuncFormatter(percentage_formatter))

        # # Split y-tick labels into two lines after a certain character limit
        # ytick_labels = [
        #     label[:10] + "\n" + label[10:] if len(label) > 10 else label
        #     for label in topic_names
        # ]

        # # Set y-tick labels with margin on the right
        # plt.yticks(
        #     range(len(topic_names)), ytick_labels, fontsize=8, va="center", ha="right"
        # )

        # plt.grid(axis="x", linestyle="--", alpha=0.7)  # Adjust grid lines along x-axis
        # plt.tight_layout(pad=3.5)  # Add padding/margins around the plot

        # summary = "THIS GRAPH INDICATES THE PERCENTAGE OF CORRECT ANSWERS FOR EACH TOPIC."  # Summary in uppercase
        # plt.figtext(0.5, 0.01, summary, wrap=True, ha="center", fontsize=8)
        # pdf.savefig(pad_inches=(20, 20, 20, 20))  # Adjust page size here
        # plt.close()

        # Create a PDF file to save the plots

        bar_height = 0.35
        bar_offset = bar_height / 2
        y_positions = np.arange(len(topic_names))
        correct_positions = y_positions + bar_offset
        incorrect_positions = y_positions - bar_offset
        plt.figure(figsize=(8.23, 6))
        bars1 = plt.barh(
            correct_positions,
            percentage_correct_topicwise,
            bar_height,
            color="orange",
            label="Correct",
        )
        bars2 = plt.barh(
            incorrect_positions,
            percentage_incorrect_topicwise,
            bar_height,
            color="lightcoral",
            label="Incorrect",
        )

        plt.title("Percentage Of Correct vs Incorrect Answers Topic-Wise", fontweight="bold")
        plt.xlabel("Percentage Of Answers")
        plt.ylabel("Topics")
        plt.gca().xaxis.set_major_formatter(FuncFormatter(percentage_formatter))

        # Split y-tick labels into two lines after a certain character limit and make them uppercase
        ytick_labels = [
        (label.split(' ', 1)[0] + "\n" + label.split(' ', 1)[1]) if ' ' in label else label
        for label in topic_names
        ]
        ytick_labels = [label for label in ytick_labels]

        # Set y-tick labels with margin on the right
        plt.yticks(range(len(topic_names)), ytick_labels, fontsize=8, ha="right")

        plt.legend(loc="best")
        plt.xlim(0, 100)  # Adjust the x-axis limit based on your data range
        plt.grid(axis="x", linestyle="--", alpha=0.7)
        plt.tight_layout(pad=3.5)

        summary = "This Graph Indicates The Percentage Of Correct And Incorrect Answers For Each Topic."
        plt.figtext(0.5, 0.04, summary, wrap=True, ha="center", fontsize=8)
        plt.subplots_adjust(bottom=0.20)
        pdf.savefig(pad_inches=(20, 20, 20, 20))  # Adjust page size here
        plt.close()

    # Create a PDF file
    with PdfPages("assets/pdfs/analysis_plots.pdf") as pdf:
        # if find_student_rank(given_student_id) <= 10:
        #     fig = visualize_accuracy_top_users2()
        # else:
        #     fig = visualize_accuracy_top_users1()
        # Add description
        # plt.text(
        #     0.5,
        #     0.01,
        #     "This graph compares the students accuracy analysis against the top 10 users.",
        #     ha="center",
        #     fontsize=10,
        #     transform=fig.transFigure,
        # )
        # pdf.savefig(
        #     fig, bbox_inches="tight", pad_inches=0.6
        # )  # Save the current figure to the PDF with a tight bounding box
        # plt.close(fig)  # Close the current figure to free memory


        fig = visualize_percent_top_users()
        # Add description
        plt.text(
            0.5,
            0.01,
            "This graph compares the students marks based percent analysis against the top 10 Students. ",
            ha="center",
            fontsize=8,
            transform=fig.transFigure,
        )
        pdf.savefig(
            fig, bbox_inches="tight", pad_inches=0.6
        )  # Save the current figure to the PDF with a tight bounding box
        plt.close(fig)

        fig, total_students = visualize_marks_top_users()
        # Add description
        plt.text(
            0.5,
            0.01,
            f"This graph displays the students marks analysis against the top {total_students} Students.",
            ha="center",
            fontsize=8,
            transform=fig.transFigure,
        )
        plt.subplots_adjust(bottom=0.15)
        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.3)
        plt.close(fig)


        # fig = visualize_time_taken_top_users()
        fig = custom_visualize_time_taken_top_users()
        # Add description
        # plt.text(
        #     0.5,
        #     0.01,
        #     "This graph compares the students time taken analysis against the top 10 Students.",
        #     ha="center",
        #     fontsize=10,
        #     transform=fig.transFigure,
        # )
        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.6)
        plt.close(fig)

        fig = visualize_time_efficiency_top_users()
        # Add description
        plt.text(
            0.5,
            0.01,
            "This graph compares the students time efficiency analysis against the top 10 Students.",
            ha="center",
            fontsize=8,
            transform=fig.transFigure,
        )
        plt.subplots_adjust(bottom=0.15)
        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.3)
        plt.close(fig)

        # Set the page size of the PDF to 10x10 inches
        pdf.infodict()["Title"] = "Analysis Plots"
        pdf.infodict()["Author"] = "Your Name"
        pdf.infodict()["Subject"] = "Analysis of top 10 Students"
        pdf.infodict()["Keywords"] = "analysis, top Students"
        # pdf.infodict()['CreationDate'] = datetime.datetime.today()
        pdf.infodict()["PageSize"] = (
            720,
            720,
        )  # 10x10 inches in points (1 inch = 72 points)

    options = {
        "margin-top": "0",
        "margin-bottom": "0",
        "margin-left": "0",
        "margin-right": "0",
    }

    subject_percentages = {}
    for topic in topics_data:
        subject_percentages[topic["name"]] = topic["correct_percentage"]

    max_subject = max(subject_percentages, key=subject_percentages.get)
    min_subject = min(subject_percentages, key=subject_percentages.get)
    correct_percentages = [topic["correct_percentage"] for topic in topics_data]

    max_percentage = max(correct_percentages)
    min_percentage = min(correct_percentages)

    # Example student data
    strong_areas = f"{max_subject} stands out as the strongest area, with the highest percentage of correct answers ({max_percentage:.1f}%)."
    weak_areas = f"{min_subject} appears to be the weakest area, with a lower percentage of correct answers ({min_percentage:.1f}%) and a higher percentage of incorrect answers."
    # Rank 1   -----   # HARDCODED DATA
    rank1_accuracy = 99
    rank1_marks = 49
    rank1_time_taken = 25
    rank1_time_efficiency = 86.1

    # Define average data (example data)
    avg_accuracy = average_accuracy()
    avg_marks = average_marks()
    avg_percent = average_percent()
    avg_time_efficiency = average_time_efficiency()

    student_name = get_student_name(given_student_id)
    accuracy = "{:.2f}".format(accuracy_analysis_for_current_student())
    percent = percent_analysis_for_current_student()
    marks = marks_analysis(given_student_id)
    points_percentage2 = points_percentage_analysis(given_student_id)
    formatted_percentage = "{:.2f}".format(points_percentage2)
    points_percentage = formatted_percentage

    time_taken = time_taken_analysis(given_student_id)
    minutes = int(time_taken)

    passing_probab = 100 * calculate_passing_probability(percent)
    passing_result = f"{passing_probab:.0f}"
    # Extract seconds
    seconds = int((time_taken - minutes) * 60)

    perc = marks * 100 / 50  # HARDCODED DATA (magic values)
    time_efficiency2 = "{:.2f}".format(time_efficiency(given_student_id))

    # Rank
    student_id_to_find = given_student_id  # Example student ID to find rank
    TotalRanks = len(rank_students())
    rank = find_student_rank(student_id_to_find)

    sorted_topics = sorted(topics_data, key=lambda x: x['time_efficiency'], reverse=True)
    top_opportunities = [topic['name'] for topic in sorted_topics[:2]]
    top_threats = [topic['name'] for topic in sorted_topics[-2:]]

    percentile = round((rank*100) / TotalRanks,1)
    
    # Generate front page HTML dynamically
    front_page_args = {
        "student_name": student_name,
        "accuracy": accuracy,
        "marks": marks,
        "percent": percent,
        "time_taken": time_taken,
        "time_efficiency2": time_efficiency2,
        "minutes": minutes,
        "seconds": seconds,
        "rank": rank,
        "percentile":percentile,
        "rank1_accuracy": rank1_accuracy,
        "avg_percent": avg_percent,
        "rank1_marks": rank1_marks,
        "avg_marks": avg_marks,
        "avg_accuracy": avg_accuracy,
        "rank1_time_taken": rank1_time_taken,
        "average_time_taken": average_time_taken,
        "rank1_time_efficiency": rank1_time_efficiency,
        "avg_time_efficiency": avg_time_efficiency,
        "strong_areas": strong_areas,
        "weak_areas": weak_areas,
        "passing_result": passing_result,
        "topics_data": topics_data,
        "top_opportunities": top_opportunities,
        "top_threats": top_threats,
        "max_marks": max_subject_marks,
    }

    html_content1 = generate_front_page(**front_page_args)

    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    pdfkit.from_string(
        html_content1,
        "assets/pdfs/front_page.pdf",
        options=options,
        configuration=config,
    )

    # Merge front page PDF with analysis plots PDF
    merger = PdfMerger()
    merger.append("assets/pdfs/front_page.pdf")
    merger.append("assets/pdfs/graphs_summary.pdf")
    merger.append("assets/pdfs/analysis_plots.pdf")

    # Save the final report PDF
    merger.write("assets/pdfs/final_report.pdf")
    merger.close()
    print("Final report generated successfully.")
   
except Exception as e:
    print(f"Error: {str(e)}")
    print(traceback.format_exc())
    sys.exit(1)
