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
    calculate_passing_probability
)
from utils.constants import LMS_API_HEADERS, WKHTMLTOPDF_PATH


try:
    student_id = ""
    subject = ""
    if len(sys.argv) > 2:
        e = sys.argv[1]
        f = sys.argv[2]

        student_id = e
        subject = f
    else:
        raise Exception("Student ID is not specified")

    classId, testId = get_class_and_test_id(subject)

    exercie_service = ExerciseService(LMS_API_HEADERS)

    data = exercie_service.get_attempt_data(testId, classId, student_id)

    if data["code"] == 200 and data["message"] == "Exercise Retrieved":
        attempt_id = data["exercises"][0]["attempt_id"]
    else:
        raise Exception("Failed to retrieve exercises")

    exercise_data = exercie_service.get_exercise_data(attempt_id)

    # Get the questions array
    questions = exercise_data["exercise"]["test_parts"][0]["questions"]

    marks_array, time_taken_array = process_question_data(questions)

    pharmaceutical_chemistry_marks = marks_array[:10]
    pharmacology_marks = marks_array[10:25]
    physiology_marks = marks_array[25:40]
    pharmaceutics_and_therapeutics_marks = marks_array[40:]

    # time array
    pharmaceutical_chemistry_time = time_taken_array[:10]
    pharmacology_time = time_taken_array[10:25]
    physiology_time = time_taken_array[25:40]
    pharmaceutics_and_therapeutics_time = time_taken_array[40:]

    report_service = ReportService(LMS_API_HEADERS)
    class_progress_report_data = report_service.get_class_progress_report(classId) # PER PAGE DATA IS HARDCODED
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

        rank = 1 # HARDCODED DATA
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
        marks_list = [marks_analysis(student_id) for student_id in users_df["student_id"]]
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


    def accuracy_analysis(student_id):
        marks_data = extract_marks(student_id)
        accuracy = int(marks_data[0]["gr"])
        return accuracy


    def marks_analysis(student_id):
        marks_data = extract_marks(student_id)
        marks = int(marks_data[0]["mk"])
        return marks


    # Define a function to analyze marks for a given student
    def marks_analysis2(student_id):
        marks_data = extract_marks(student_id)
        if marks_data:
            attempt = marks_data[0]
            marks = int(attempt.get("mk"))
            total_marks = int(attempt.get("tm"))
            return marks, total_marks
        return None


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


    # Define a function to visualize time taken for top users using seaborn
    def visualize_time_taken_top_users():
        sorted_user_ids = sort_users_by_time_taken()
        time_data = {
            get_student_name(student_id): time_taken_analysis(student_id)
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(8, 6))
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

        ax.set_title("Time Taken Analysis (Top 10 Users)")
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
        marks, total_marks = marks_data
        if total_marks == 0:
            return None  # or return 0 or any other value as appropriate

        # Normalize marks and time taken
        normalized_marks = marks / 50  # Maximum marks
        normalized_time_taken = time_taken_analysis(student_id) / 60  # Maximum time taken

        # Calculate efficiency within 100%
        efficiency = (normalized_marks + (1 - normalized_time_taken)) * 50
        return efficiency


    def visualize_time_efficiency_top_users():
        sorted_user_ids = sort_users_by_time_taken()
        efficiency_data = {
            get_student_name(student_id): time_efficiency(student_id)
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(8, 6))
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
        ax.text(
            given_student_efficiency,
            given_student_name,
            f"{given_student_efficiency:.2f}%",
            color="black",
            va="center",
            ha="left",
        )  # Write value inside the bar
        ax.set_title("Time Efficiency Analysis (Top 10 Users)")
        ax.set_xlabel("Time Efficiency (%)")
        ax.set_ylabel("Students")
        ax.legend()
        ax.set_yticks([])
        return fig


    def visualize_points_percentage_top_users():
        sorted_user_ids = sort_users_by_max_marks()
        points_data = {
            get_student_name(student_id): points_percentage_analysis(student_id)
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
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
        ax.set_title("Points Percentage Analysis (Top 10 Users)")
        ax.set_xlabel("Students")
        ax.set_ylabel("Points Percentage")
        ax.set_xticks([])
        ax.legend()
        return fig


    def visualize_marks_top_users():
        sorted_user_ids = sort_users_by_max_marks()
        marks_data = {
            get_student_name(student_id): marks_analysis(student_id)
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(8, 6))
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
            [time_efficiency(given_student_id)],
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
        ax.set_title("Marks Analysis (Top 10 Users)")
        ax.set_xlabel("Marks Obtained")
        ax.set_ylabel("Top 10 Student")
        ax.legend()
        ax.set_yticks([])
        return fig


    def visualize_accuracy_top_users1():
        sorted_user_ids = sort_users_by_max_marks()
        accuracy_data = {
            get_student_name(student_id): accuracy_analysis(student_id)
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111)

        # Plot data points
        for student_id in sorted_user_ids:
            student_name = get_student_name(student_id)
            ax.plot(
                [student_name], [accuracy_data[student_name]], marker="o", color="skyblue"
            )

        # Include the given student's data point in the list
        sorted_names = [get_student_name(student_id) for student_id in sorted_user_ids]
        sorted_values = [accuracy_data[name] for name in sorted_names]
        sorted_names.append(get_student_name(given_student_id))  # Add given student's name
        sorted_values.append(
            accuracy_analysis(given_student_id)
        )  # Add given student's data
        ax.plot(
            sorted_names, sorted_values, linestyle="--", color="grey"
        )  # Dotted line, grey color

        # Plot for given student
        ax.plot(
            [get_student_name(given_student_id)],
            [accuracy_analysis(given_student_id)],
            "ro",
            label=f"Candidate: ({get_student_name(given_student_id)})",
        )

        ax.set_title("Accuracy Analysis (Top 10 Users)")
        ax.set_xlabel("Students")
        ax.set_ylabel("Accuracy (%)")
        ax.set_xticks([])
        ax.legend()
        return fig


    def visualize_accuracy_top_users2():
        sorted_user_ids = sort_users_by_max_marks()
        accuracy_data = {
            get_student_name(student_id): accuracy_analysis(student_id)
            for student_id in sorted_user_ids
        }
        fig = plt.figure(figsize=(8, 6))
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

        ax.set_title("Accuracy Analysis (Top 10 Users)")
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
        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111)

        # Plot data points
        for student_id in sorted_user_ids:
            student_name = get_student_name(student_id)
            ax.plot(
                [student_name], [accuracy_data[student_name]], marker="o", color="skyblue"
            )

        # Include the given student's data point in the list
        sorted_names = [get_student_name(student_id) for student_id in sorted_user_ids]
        sorted_values = [accuracy_data[name] for name in sorted_names]
        sorted_names.append(get_student_name(given_student_id))  # Add given student's name
        sorted_values.append(percent_analysis(given_student_id))  # Add given student's data
        ax.plot(
            sorted_names, sorted_values, linestyle="--", color="grey"
        )  # Dotted line, grey color

        # Plot for given student
        ax.plot(
            [get_student_name(given_student_id)],
            [percent_analysis(given_student_id)],
            "ro",
            label=f"Candidate: ({get_student_name(given_student_id)})",
        )

        ax.set_title("Percentage Analysis (Top 10 Users)")
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

    # Calculate sum of marks for each topic
    sum_marks_pharmaceutical_chemistry = calculate_sum_marks(pharmaceutical_chemistry_marks)
    sum_marks_pharmacology = calculate_sum_marks(pharmacology_marks)
    sum_marks_physiology = calculate_sum_marks(physiology_marks)
    sum_marks_pharmaceutics_and_therapeutics = calculate_sum_marks(
        pharmaceutics_and_therapeutics_marks
    )

    # Bar chart for sum of marks per topic
    topics = [
        "Pharmaceutical Chemistry",
        "Pharmacology",
        "Physiology",
        "Pharmaceutics and Therapeutics",
    ]
    sum_marks = [
        sum_marks_pharmaceutical_chemistry,
        sum_marks_pharmacology,
        sum_marks_physiology,
        sum_marks_pharmaceutics_and_therapeutics,
    ]

    # Pie chart for percentage of correct, incorrect, and unattempted questions per topic
    correct_counts = [
        pharmaceutical_chemistry_marks.count(1),
        pharmacology_marks.count(1),
        physiology_marks.count(1),
        pharmaceutics_and_therapeutics_marks.count(1),
    ]
    incorrect_counts = [
        pharmaceutical_chemistry_marks.count(0),
        pharmacology_marks.count(0),
        physiology_marks.count(0),
        pharmaceutics_and_therapeutics_marks.count(0),
    ]
    unattempted_counts = [
        pharmaceutical_chemistry_marks.count(2),
        pharmacology_marks.count(2),
        physiology_marks.count(2),
        pharmaceutics_and_therapeutics_marks.count(2),
    ]

    plt.pie(
        correct_counts,
        labels=topics,
        autopct="%1.1f%%",
        colors=["lightgreen", "lightcoral", "lightblue", "lightyellow"],
    )
    # plt.title('Percentage of Correct Answers')

    # plt.subplot(1, 2, 2)
    plt.pie(
        incorrect_counts,
        labels=topics,
        autopct="%1.1f%%",
        colors=["lightcoral", "lightgreen", "lightblue", "lightyellow"],
    )

    topic_marks = [
        pharmaceutical_chemistry_marks,
        pharmacology_marks,
        physiology_marks,
        pharmaceutics_and_therapeutics_marks,
    ]

    # Calculate total marks for each topic based on correct answers (array element is 1)
    total_marks_topicwise = [
        sum(1 for mark in topic_marks if mark == 1)
        for topic_marks in [
            pharmaceutical_chemistry_marks,
            pharmacology_marks,
            physiology_marks,
            pharmaceutics_and_therapeutics_marks,
        ]
    ]

    # Calculate average time taken for each topic
    average_time_taken_a = [
        np.mean(pharmaceutical_chemistry_time),
        np.mean(pharmacology_time),
        np.mean(physiology_time),
        np.mean(pharmaceutics_and_therapeutics_time),
    ]

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

    # Calculate total time taken per section
    total_time_pharmaceutical_chemistry = sum(pharmaceutical_chemistry_time) / 60
    total_time_pharmacology = sum(pharmacology_time) / 60
    total_time_physiology = sum(physiology_time) / 60
    total_time_pharmaceutics_and_therapeutics = (
        sum(pharmaceutics_and_therapeutics_time) / 60
    )

    # Define section names
    sections = [
        "Pharmaceutical Chemistry",
        "Pharmacology",
        "Physiology",
        "Pharmaceutics and Therapeutics",
    ]
    total_times = [
        total_time_pharmaceutical_chemistry,
        total_time_pharmacology,
        total_time_physiology,
        total_time_pharmaceutics_and_therapeutics,
    ]


    # Calculate the percentage of correct answers for each topic
    total_questions_per_topic = [
        len(topic_marks)
        for topic_marks in [
            pharmaceutical_chemistry_marks,
            pharmacology_marks,
            physiology_marks,
            pharmaceutics_and_therapeutics_marks,
        ]
    ]
    total_correct_per_topic = [
        sum(1 for mark in topic_marks if mark == 1)
        for topic_marks in [
            pharmaceutical_chemistry_marks,
            pharmacology_marks,
            physiology_marks,
            pharmaceutics_and_therapeutics_marks,
        ]
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
    total_questions_per_topic = [
        len(topic_marks)
        for topic_marks in [
            pharmaceutical_chemistry_marks,
            pharmacology_marks,
            physiology_marks,
            pharmaceutics_and_therapeutics_marks,
        ]
    ]
    total_correct_per_topic = [
        sum(1 for mark in topic_marks if mark == 1)
        for topic_marks in [
            pharmaceutical_chemistry_marks,
            pharmacology_marks,
            physiology_marks,
            pharmaceutics_and_therapeutics_marks,
        ]
    ]
    percentage_correct_topicwise = [
        (correct / total_questions) * 100
        for correct, total_questions in zip(
            total_correct_per_topic, total_questions_per_topic
        )
    ]

    # Calculate percentage of incorrect answers for each topic
    total_incorrect_per_topic = [
        sum(1 for mark in topic_marks if mark == 0)
        for topic_marks in [
            pharmaceutical_chemistry_marks,
            pharmacology_marks,
            physiology_marks,
            pharmaceutics_and_therapeutics_marks,
        ]
    ]
    percentage_incorrect_topicwise = [
        (incorrect / total_questions) * 100
        for incorrect, total_questions in zip(
            total_incorrect_per_topic, total_questions_per_topic
        )
    ]

    # Plot Percentage of Correct and Incorrect Answers Topic-wise
    bar_width = 0.35
    topics_bar = np.arange(len(topics))

    # Create a PDF file to save the plots
    with PdfPages("assets/pdfs/graphs_summary.pdf") as pdf:
        plt.figure(figsize=(7, 6))
        plt.bar(topics, total_marks_topicwise, color="skyblue", width=0.5)
        plt.title("Topic-wise Total Marks (Correct Answers)")
        plt.xlabel("Topics")
        plt.ylabel("Total Correct Answers")

        # Split x-tick labels into two lines after a whitespace
        xtick_labels = [split_label(label) for label in topics]

        # Set x-tick labels with margin on the right
        plt.xticks(range(len(topics)), xtick_labels, rotation=0, ha="center", fontsize=8)

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout(pad=3.5)  # Add padding/margins around the plot
        summary = "This graph indicates the total number of correct answers for each topic."
        plt.figtext(0.5, 0.06, summary, wrap=True, ha="center", fontsize=8)
        pdf.savefig(pad_inches=(20, 20, 20, 20))  # Adjust page size here
        plt.close()

        plt.figure(figsize=(7, 6))
        plt.bar(topics, average_time_taken_a, color="lightgreen", width=0.5)
        plt.title("Topic-wise Average Time Taken per question")
        plt.xlabel("Topics")
        plt.ylabel("Average Time Taken (seconds)")

        # Split x-tick labels into two lines after a whitespace
        xtick_labels = [split_label(label) for label in topics]

        # Set x-tick labels with margin on the right
        plt.xticks(range(len(topics)), xtick_labels, rotation=0, ha="center", fontsize=8)

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout(pad=3.5)  # Add padding/margins around the plot
        summary = "This graph indicates the average time taken per question for each topic."
        plt.figtext(0.5, 0.06, summary, wrap=True, ha="center", fontsize=8)
        pdf.savefig(pad_inches=(20, 20, 20, 20))  # Adjust page size here
        plt.close()

        # Plot Pie Chart for Percentage Correct, Incorrect, and Unattempted Questions
        plt.figure(figsize=(6, 6))  # Keep figure size for better readability
        plt.pie(sizes, colors=colors, autopct="%1.1f%%", startangle=140)
        plt.title("Question Response Analysis", fontsize=12, pad=20)
        plt.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle
        plt.legend(
            loc="upper right", labels=["Correct", "Incorrect", "Unattempted"], fontsize=8
        )
        plt.xlabel("Response Categories", fontsize=10)  # Add x-axis label
        summary = "This pie chart shows the distribution of correct, incorrect, and unattempted questions."
        plt.figtext(0.5, 0.01, summary, wrap=True, ha="center", fontsize=10)
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        pdf.savefig(bbox_inches="tight", pad_inches=0.5)
        plt.close()

        # Plot Total Time Taken per Section
        plt.figure(figsize=(8, 6))
        plt.barh(sections, total_times, color="skyblue", height=0.5)
        plt.title("Total Time Taken per Section")
        plt.xlabel("Total Time Taken (minutes)")
        plt.ylabel("Sections")

        # Split y-tick labels into two lines after a whitespace
        ytick_labels = [split_label(label) for label in sections]

        # Set y-tick labels with margin on the right
        plt.yticks(range(len(sections)), ytick_labels, fontsize=8, va="center", ha="right")

        # Add a figure text with a summary
        summary = "This graph indicates the total time taken per section in minutes."
        plt.figtext(0.5, 0.03, summary, wrap=True, ha="center", fontsize=8)
        plt.subplots_adjust(bottom=0.2)

        pdf.savefig(bbox_inches="tight")  # Save the figure
        plt.close()

        plt.figure(figsize=(7, 6))
        bars = plt.bar(topics, percentage_correct_topicwise, color="orange", width=0.5)
        plt.title("Percentage of Correct Answers Topic-wise")
        plt.xlabel("Topics")
        plt.ylabel("Percentage of Correct Answers")
        plt.gca().yaxis.set_major_formatter(FuncFormatter(percentage_formatter))

        # Split x-tick labels into two lines after a whitespace
        xtick_labels = [split_label(label) for label in topics]

        # Set x-tick labels with margin on the right
        plt.xticks(range(len(topics)), xtick_labels, rotation=0, ha="center", fontsize=8)

        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout(pad=3.5)  # Add padding/margins around the plot
        summary = "This graph indicates the percentage of correct answers for each topic."
        plt.figtext(0.5, 0.06, summary, wrap=True, ha="center", fontsize=8)
        pdf.savefig(pad_inches=(20, 20, 20, 20))  # Adjust page size here
        plt.close()

        # Create a PDF file to save the plots

        plt.figure(figsize=(7, 6))
        bars1 = plt.bar(
            topics_bar - bar_width / 2,
            percentage_correct_topicwise,
            bar_width,
            color="orange",
            label="Correct",
        )
        bars2 = plt.bar(
            topics_bar + bar_width / 2,
            percentage_incorrect_topicwise,
            bar_width,
            color="lightcoral",
            label="Incorrect",
        )
        plt.title("Percentage of Correct Vs Incorrect Answers Topic-wise")
        plt.xlabel("Topics")
        plt.ylabel("Percentage of Answers")
        plt.gca().yaxis.set_major_formatter(FuncFormatter(percentage_formatter))

        # Split x-tick labels into two lines after a whitespace
        xtick_labels = [split_label(label) for label in topics]

        # Set x-tick labels with margin on the right
        plt.xticks(range(len(topics)), xtick_labels, rotation=0, ha="center", fontsize=8)

        plt.legend()
        plt.ylim(0, 100)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.tight_layout(pad=3.5)
        summary = "This graph indicates the percentage of correct and incorrect answers for each topic."
        plt.figtext(0.5, 0.06, summary, wrap=True, ha="center", fontsize=8)
        pdf.savefig(pad_inches=(20, 20, 20, 20))  # Adjust page size here
        plt.close()


    (
        pharmaceutical_chemistry_total,
        pharmaceutical_chemistry_correct,
        pharmaceutical_chemistry_incorrect,
        pharmaceutical_chemistry_unattempted,
        pharmaceutical_chemistry_correct_percentage,
        pharmaceutical_chemistry_incorrect_percentage,
        pharmaceutical_chemistry_unattempted_percentage,
    ) = calculate_counts(pharmaceutical_chemistry_marks)

    (
        pharmacology_total,
        pharmacology_correct,
        pharmacology_incorrect,
        pharmacology_unattempted,
        pharmacology_correct_percentage,
        pharmacology_incorrect_percentage,
        pharmacology_unattempted_percentage,
    ) = calculate_counts(pharmacology_marks)

    (
        physiology_total,
        physiology_correct,
        physiology_incorrect,
        physiology_unattempted,
        physiology_correct_percentage,
        physiology_incorrect_percentage,
        physiology_unattempted_percentage,
    ) = calculate_counts(physiology_marks)

    (
        pharmaceutics_and_therapeutics_total,
        pharmaceutics_and_therapeutics_correct,
        pharmaceutics_and_therapeutics_incorrect,
        pharmaceutics_and_therapeutics_unattempted,
        pharmaceutics_and_therapeutics_correct_percentage,
        pharmaceutics_and_therapeutics_incorrect_percentage,
        pharmaceutics_and_therapeutics_unattempted_percentage,
    ) = calculate_counts(pharmaceutics_and_therapeutics_marks)

    # Average time taken per question for each topic
    pharmaceutical_chemistry_avg_time = sum(pharmaceutical_chemistry_time) / len(
        pharmaceutical_chemistry_time
    )
    pharmacology_avg_time = sum(pharmacology_time) / len(pharmacology_time)
    physiology_avg_time = sum(physiology_time) / len(physiology_time)
    pharmaceutics_and_therapeutics_avg_time = sum(
        pharmaceutics_and_therapeutics_time
    ) / len(pharmaceutics_and_therapeutics_time)

    # Convert time to minutes for better readability
    pharmaceutical_chemistry_avg_time_minutes = pharmaceutical_chemistry_avg_time / 60
    pharmacology_avg_time_minutes = pharmacology_avg_time / 60
    physiology_avg_time_minutes = physiology_avg_time / 60
    pharmaceutics_and_therapeutics_avg_time_minutes = (
        pharmaceutics_and_therapeutics_avg_time / 60
    )

    # Correct, incorrect, and unattempted counts for each topic
    pharmaceutical_chemistry_correct_count = pharmaceutical_chemistry_marks.count(1)
    pharmaceutical_chemistry_incorrect_count = pharmaceutical_chemistry_marks.count(0)
    pharmaceutical_chemistry_unattempted_count = pharmaceutical_chemistry_marks.count(2)

    pharmacology_correct_count = pharmacology_marks.count(1)
    pharmacology_incorrect_count = pharmacology_marks.count(0)
    pharmacology_unattempted_count = pharmacology_marks.count(2)

    physiology_correct_count = physiology_marks.count(1)
    physiology_incorrect_count = physiology_marks.count(0)
    physiology_unattempted_count = physiology_marks.count(2)

    pharmaceutics_and_therapeutics_correct_count = (
        pharmaceutics_and_therapeutics_marks.count(1)
    )
    pharmaceutics_and_therapeutics_incorrect_count = (
        pharmaceutics_and_therapeutics_marks.count(0)
    )
    pharmaceutics_and_therapeutics_unattempted_count = (
        pharmaceutics_and_therapeutics_marks.count(2)
    )

    # Total counts for each topic
    pharmaceutical_chemistry_total_count = len(pharmaceutical_chemistry_marks)
    pharmacology_total_count = len(pharmacology_marks)
    physiology_total_count = len(physiology_marks)
    pharmaceutics_and_therapeutics_total_count = len(pharmaceutics_and_therapeutics_marks)


    # Create a PDF file
    with PdfPages("assets/pdfs/analysis_plots.pdf") as pdf:
        if find_student_rank(given_student_id) <= 10:
            fig = visualize_accuracy_top_users2()
        else:
            fig = visualize_accuracy_top_users1()
        # Add description
        plt.text(
            0.5,
            0.01,
            "This graph compares the students accuracy analysis against the top 10 users.",
            ha="center",
            fontsize=10,
            transform=fig.transFigure,
        )
        pdf.savefig(
            fig, bbox_inches="tight", pad_inches=0.6
        )  # Save the current figure to the PDF with a tight bounding box
        plt.close(fig)  # Close the current figure to free memory

        fig = visualize_percent_top_users()
        # Add description
        plt.text(
            0.5,
            0.01,
            "This graph compares the students marks based percent analysis against the top 10 users. ",
            ha="center",
            fontsize=10,
            transform=fig.transFigure,
        )
        pdf.savefig(
            fig, bbox_inches="tight", pad_inches=0.6
        )  # Save the current figure to the PDF with a tight bounding box
        plt.close(fig)

        fig = visualize_marks_top_users()
        # Add description
        plt.text(
            0.5,
            0.01,
            "This graph displays the students marks analysis against the top 10 users.",
            ha="center",
            fontsize=10,
            transform=fig.transFigure,
        )
        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.6)
        plt.close(fig)
        fig = visualize_time_taken_top_users()
        # Add description
        plt.text(
            0.5,
            0.01,
            "This graph compares the students time taken analysis against the top 10 users.",
            ha="center",
            fontsize=10,
            transform=fig.transFigure,
        )
        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.6)
        plt.close(fig)

        fig = visualize_time_efficiency_top_users()
        # Add description
        plt.text(
            0.5,
            0.01,
            "This graph compares the students time efficiency analysis against the top 10 users.",
            ha="center",
            fontsize=10,
            transform=fig.transFigure,
        )
        pdf.savefig(fig, bbox_inches="tight", pad_inches=0.6)
        plt.close(fig)

        # Set the page size of the PDF to 10x10 inches
        pdf.infodict()["Title"] = "Analysis Plots"
        pdf.infodict()["Author"] = "Your Name"
        pdf.infodict()["Subject"] = "Analysis of top 10 users"
        pdf.infodict()["Keywords"] = "analysis, top users"
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

    # max and min subject
    subject_percentages = {
        "Pharmaceutical Chemistry": pharmaceutical_chemistry_correct_percentage,
        "Pharmacology": pharmacology_correct_percentage,
        "Physiology": physiology_correct_percentage,
        "Pharmaceutics and Therapeutics": pharmaceutics_and_therapeutics_correct_percentage,
    }
    max_subject = max(subject_percentages, key=subject_percentages.get)
    min_subject = min(subject_percentages, key=subject_percentages.get)

    max_percentage = max(
        pharmaceutical_chemistry_correct_percentage,
        pharmacology_correct_percentage,
        physiology_correct_percentage,
        pharmaceutics_and_therapeutics_correct_percentage,
    )

    min_percentage = min(
        pharmaceutical_chemistry_correct_percentage,
        pharmacology_correct_percentage,
        physiology_correct_percentage,
        pharmaceutics_and_therapeutics_correct_percentage,
    )

    # Example student data
    strong_areas = f"{max_subject} stands out as the strongest area, with the highest percentage of correct answers ({max_percentage:.1f}%)."
    weak_areas = f"{min_subject} appears to be the weakest area, with a lower percentage of correct answers ({min_percentage:.1f}%) and a higher percentage of incorrect answers."
    # Rank 1   -----   # HARDCODED DATA
    rank1_accuracy = 99
    rank1_marks = 49
    rank1_time_taken = 25
    rank1_time_efficiency = 90

    # Define average data (example data)
    avg_accuracy = average_accuracy()
    avg_marks = average_marks()
    avg_percent = average_percent()
    avg_time_efficiency = average_time_efficiency()

    student_name = get_student_name(given_student_id)
    accuracy = accuracy_analysis(given_student_id)
    percent = percent_analysis(given_student_id)
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

    perc = marks * 100 / 50 # HARDCODED DATA (magic values)
    # time_efficiency2 = time_efficiency(90577321)
    time_efficiencyx = marks * time_taken * 100 / (60 * 50) # HARDCODED DATA (magic values)
    time_efficiency2 = "{:.2f}".format(time_efficiencyx)

    # Rank
    student_id_to_find = given_student_id  # Example student ID to find rank
    rank = find_student_rank(student_id_to_find)

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
        "rank1_accuracy": rank1_accuracy,
        "avg_percent": avg_percent,
        "rank1_marks": rank1_marks,
        "avg_marks": avg_marks,
        "avg_accuracy": avg_accuracy,
        "rank1_time_taken": rank1_time_taken,
        "average_time_taken": average_time_taken,
        "rank1_time_efficiency": rank1_time_efficiency,
        "avg_time_efficiency": avg_time_efficiency,
        "pharmaceutical_chemistry_avg_time": pharmaceutical_chemistry_avg_time,
        "pharmaceutical_chemistry_correct": pharmaceutical_chemistry_correct,
        "pharmaceutical_chemistry_total": pharmaceutical_chemistry_total,
        "pharmaceutical_chemistry_correct_percentage": pharmaceutical_chemistry_correct_percentage,
        "pharmaceutical_chemistry_incorrect": pharmaceutical_chemistry_incorrect,
        "pharmaceutical_chemistry_incorrect_percentage": pharmaceutical_chemistry_incorrect_percentage,
        "pharmaceutical_chemistry_unattempted": pharmaceutical_chemistry_unattempted,
        "pharmaceutical_chemistry_unattempted_percentage": pharmaceutical_chemistry_unattempted_percentage,
        "pharmacology_avg_time": pharmacology_avg_time,
        "pharmacology_correct": pharmacology_correct,
        "pharmacology_total": pharmacology_total,
        "pharmacology_correct_percentage": pharmacology_correct_percentage,
        "pharmacology_incorrect": pharmacology_incorrect,
        "pharmacology_incorrect_percentage": pharmacology_incorrect_percentage,
        "pharmacology_unattempted": pharmacology_unattempted,
        "pharmacology_unattempted_percentage": pharmacology_unattempted_percentage,
        "physiology_avg_time": physiology_avg_time,
        "physiology_correct": physiology_correct,
        "physiology_total": physiology_total,
        "physiology_correct_percentage": physiology_correct_percentage,
        "physiology_incorrect": physiology_incorrect,
        "physiology_incorrect_percentage": physiology_incorrect_percentage,
        "physiology_unattempted": physiology_unattempted,
        "physiology_unattempted_percentage": physiology_unattempted_percentage,
        "pharmaceutics_and_therapeutics_avg_time": pharmaceutics_and_therapeutics_avg_time,
        "pharmaceutics_and_therapeutics_correct": pharmaceutics_and_therapeutics_correct,
        "pharmaceutics_and_therapeutics_total": pharmaceutics_and_therapeutics_total,
        "pharmaceutics_and_therapeutics_correct_percentage": pharmaceutics_and_therapeutics_correct_percentage,
        "pharmaceutics_and_therapeutics_incorrect": pharmaceutics_and_therapeutics_incorrect,
        "pharmaceutics_and_therapeutics_incorrect_percentage": pharmaceutics_and_therapeutics_incorrect_percentage,
        "pharmaceutics_and_therapeutics_unattempted": pharmaceutics_and_therapeutics_unattempted,
        "pharmaceutics_and_therapeutics_unattempted_percentage": pharmaceutics_and_therapeutics_unattempted_percentage,
        "strong_areas": strong_areas,
        "weak_areas": weak_areas,
        "passing_result": passing_result,
    }
    html_content1 = generate_front_page(**front_page_args)

    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    pdfkit.from_string(
        html_content1, "assets/pdfs/front_page.pdf", options=options, configuration=config
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
    sys.exit(1)
