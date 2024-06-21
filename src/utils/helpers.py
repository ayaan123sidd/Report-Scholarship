from utils.constants import QUALIFICATION_DATA


def get_qualification_data(qualification):
    if qualification in QUALIFICATION_DATA:
        return QUALIFICATION_DATA[qualification]
    return None


def get_scholarship_data(qualification, scholarship):
    qualification_data = get_qualification_data(qualification)

    if qualification_data is None:
        return None

    scholarship_data = qualification_data.get("scholarships")
    if scholarship in scholarship_data:
        data = scholarship_data.get(scholarship, None) or None
        return data
    return None


def get_class_and_test_id(qualification, scholarship):
    data = get_scholarship_data(qualification, scholarship)

    if data is None:
        return None

    return data.get("class_id", 0), data.get("test_id", 0)


# Function to calculate the sum of marks for correct answers
def calculate_sum_marks(marks):
    return sum(mark for mark in marks if mark == 1)


def process_question_data(test_parts, qualification, subject):
    scholarship_data = get_scholarship_data(qualification, subject)
    total_questions = scholarship_data.get("total_questions", 0)
    marks_array = [0] * total_questions
    time_taken_array = [0] * total_questions

    question_index = 0

    for test_part in test_parts:
        questions = test_part.get("questions", [])
        for question in questions:
            if question_index < total_questions:
                if "markedInputs" in question:
                    marked_input = question["markedInputs"][0]
                    if "is_attempted" in marked_input:
                        # flags for marks_array[i] , i = 1 correct, 0 = incorrect, 2 = unattempted
                        if marked_input["is_attempted"] == 1:
                            marks_array[question_index] = (
                                1 if marked_input.get("correct", 0) == 1 else 0
                            )
                        else:
                            marks_array[question_index] = 2

                # Extract time taken per question
                time_taken_array[question_index] = question.get("user_question_time", 0)
                question_index += 1

    return marks_array, time_taken_array


def calculate_counts(marks):
    total = len(marks)
    correct = marks.count(1)
    incorrect = marks.count(0)
    unattempted = marks.count(2)
    correct_percentage = (correct / total) * 100
    incorrect_percentage = (incorrect / total) * 100
    unattempted_percentage = (unattempted / total) * 100

    return (
        total,
        correct,
        incorrect,
        unattempted,
        correct_percentage,
        incorrect_percentage,
        unattempted_percentage,
    )


def calculate_time_efficiency(max_marks, marks_scored, max_time, time_taken):
    if marks_scored == 0 and time_taken == 0:
        efficiency = 0
    else:
        efficiency = (
            marks_scored / max_marks * 0.7 + (1 - time_taken / max_time) * 0.3
        ) * 100
    return round(efficiency)


# Passing probability
def calculate_passing_probability(score):
    if score < 10:
        return 20.0
    elif score > 80:
        P = min(0.63 + ((score - 80) / 20) * 0.07, 0.8)
    elif score >= 50:
        P = min(0.49 + ((score - 50) / 30) * 0.24, 0.8)
    elif score >= 30:
        P = min(0.35 + ((score - 30) / 20) * 0.24, 0.8)
    elif score >= 25:
        P = min(0.21 + ((score - 25) / 5) * 0.24, 0.8)
    elif score >= 10:
        P = min(0.07 + ((score - 10) / 15) * 0.24, 0.8)
    
    # Transform P to the new range [30, 60]
    P_new = 30 + 37.5 * P
    return P_new

# Function to split label into two lines after a whitespace
def split_label(label):
    index = label.rfind(" ")
    if index != -1:
        return label[:index] + "\n" + label[index + 1 :]
    else:
        return label


def get_summary_to_display(percent):
    if percent > 70:
        return 0
    elif 55 < percent <= 70:
        return 1
    elif 35 < percent <= 55:
        return 2
    else:
        return 3


def generate_front_page(
    student_name,
    accuracy,
    marks,
    percent,
    time_taken,
    time_efficiency2,
    minutes,
    seconds,
    rank,
    percentile,
    rank1_accuracy,
    avg_percent,
    rank1_marks,
    avg_marks,
    avg_accuracy,
    rank1_time_taken,
    average_time_taken,
    rank1_time_efficiency,
    avg_time_efficiency,
    strong_areas,
    weak_areas,
    passing_result,
    topics_data,
    top_opportunities,
    top_threats,
    max_marks,
):

    summary_to_display = get_summary_to_display(percent)

    # html css

    html_content = f"""
   <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Student Report</title>
        <style>
            html{{
              background-color: #f9f9f9;
              
            }}
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                background-color: #f9f9f9;
                color: #333;
            }}
            table {{
                width: 80%;
                border-collapse: collapse;
                margin:0 auto;
                margin-bottom: 20px;
                margin-top:40px;
            }}
            th, td {{
                border: 2px solid #ddd;
                padding: 8px;
                text-align: center;
                font-size:17px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            
            caption {{
                caption-side: top;
                font-weight: bold;
                margin-bottom:20px;
            }}
            .container2 {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin-top:100px;
            }}
            .summary2 {{
            margin-top: 20px;
            }}
            .container {{
                width: 80%;
                margin: 0 auto;
                text-align: center;
                padding-top: 50px;
                position: relative;
            }}
            .header {{
                margin-bottom: 30px;
            }}
            .summary2 h2{{
                color:#0FB995;
            }}
            .logo {{
                position: absolute;
                top: 20px;
                left: -40px;
                width: 160px; /* Adjust width as needed */
                height: auto;
            }}
             .student-id {{
                position: absolute;
                top: 20px;
                right: -40px;
                font-size: 16px;
            }}
            .report-title {{
                font-size: 3em;
                margin-top: 60px;
                color: #555;
                border-bottom: 2px solid #555;
                display: inline-block;
            }}
            .generative{{
                font-size:2.5rem;
                color: #555;
                border-bottom: 2px solid #555;
            }}
            .student-info {{
                margin-top: 20px;
                text-align: left;
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                font-size:18px;
            }}
            .how{{
                text-align: justify;
                margin-top:50px;
                padding: 0px 70px;
                padding-top:20px;
                font-size:18px;
                line-height:1.8rem
            }}
            .how h1{{
                color:#0FB995
            }}
            .note p{{
              font-size:13px
            }}
            .summary {{
                text-align: justify;
                padding: 20px;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                margin:0 40px;
                margin-top: 50px;
            }}
            .summary ul > li {{
                font-size: 17px !important;
            }}
            .swot-analysis {{
                padding: 0px 70px;
                text-align: justify;
                padding-top: 250px;
            }}
            .passprob{{
                text-align: justify;
                padding: 0px 70px;
                margin-top:50px;
            }}
            .passprob div{{
                font-size:18px;
                line-height:1.8rem;
            }}
            .pp{{
                font-weight:700;
                font-size:22px;
                border-bottom:2px solid #103AC5;
            }}
            
            .equal{{
                font-size:14px
            }}
            power{{
                
            }}
            .student-info p {{
                margin: 10px 0;
            }}
            .assessment-desc {{
                margin-bottom: 50px;
            }}
            .areas {{
                font-size: 17px;
            }}
            .area-value {{
                color: #0FB995;
                font-weight: bold;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://academically.com/front/assets/img/logo.svg" alt="Company Logo" class="logo">
                <span class="student-id">Student ID: 9057732</span>
                <h1 class="report-title">Report</h1>
            </div>
            <div class="student-info">
                <p><strong>Name: </strong>{student_name}</p>
                <p><strong>Percentage: </strong> {percent:.2f}%</p>
                <p><strong>Accuracy: </strong> {accuracy}%</p>
                <p><strong>Marks Obtained (out of {max_marks}): </strong> {marks}</p>
                <p><strong>Time Taken: </strong> {minutes} minutes, {seconds} seconds</p>
                <p><strong>Time Efficiency: </strong> {time_efficiency2}% </p>
                <p><strong>Percentile of Student: </strong> {percentile} %</p>
                <p class="equal"><em><strong>Time Efficiency:</strong> Number of correct answers marked relative to the time expended. (How Efficiently time was managed) </em></p>
                {"<p class='equal'><em><strong>Note: </strong>Percentage and accuracy are equal because the student attempted all questions.</em></p>" if f'{percent:.2f}' == accuracy else ""}
            </div>
            </div>

            <table>
                <caption><h3>Performance Comparison</h3></caption>
                <thead>
                    <tr>
                        <th></th>
                        <th>Top Performer</th>
                        <th>{student_name}</th>
                        <th>Average Score</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Percentage Obtained: (%)</td>
                        <td>{rank1_accuracy}</td>
                        <td>{percent:.2f}</td>
                        <td>{avg_percent}</td>
                    </tr>
                    <tr>
                        <td>Marks Obtained</td>
                        <td>{rank1_marks}</td>
                        <td>{marks}</td>
                        <td>{avg_marks}</td>
                    </tr>
                    <tr>
                        <td>Accuracy (%)</td>
                        <td>{rank1_accuracy}</td>
                        <td>{accuracy}</td>
                        <td>{avg_accuracy}</td>
                    </tr>
                    
                    <tr>
                        <td>Time Taken (minutes)</td>
                        <td>{rank1_time_taken}</td>
                        <td>{time_taken:.1f}</td>
                        <td>{average_time_taken()}</td>

                    </tr>
                    <tr>
                        <td>Time Efficiency (%)</td>
                        <td>{rank1_time_efficiency}</td>
                        <td>{time_efficiency2}</td>
                        <td>{avg_time_efficiency}</td>
                    </tr>
                </tbody>
            </table>

             <div class="summary" id="summary0" style="display:{'block' if summary_to_display == 0 else 'none'};">
                <h3>Student Summary</h3>
                <ul>
                <li>
                <p>The student showcased exceptional proficiency in the online scholarship test with an accuracy rate of <strong>{accuracy}%</strong> This demonstrates a deep understanding of the subject matter and strong problem-solving skills. 
</p>
                </li>
                <li>
                <p>The time taken to complete the test was <strong>{minutes} minutes & {seconds} seconds</strong>, which highlighted time efficiency. The accuracy rate is higher than average, and the number of questions attempted is considerably high. </p>
                </li>
                <li>
                <p>For better results, the student should focus on better time management strategies for even higher scores. Overall, the student is highly recommended for the scholarship. 
</p>
                </li>
                </ul>
            </div>

             <div class="summary" id="summary1" style="display:{'block' if summary_to_display == 1 else 'none'};" >
                <h3>Student Summary</h3>
                <ul>
                <li>
                <p>The student exhibited commendable performance in the online scholarship test, with an accuracy rate of <strong>{accuracy}%</strong>, showing effort and willingness to engage with the material. While the accuracy rate is below the desired level, the student's commitment to attempting questions is notable.
</p>
                </li>
                <li>
                <p>The student completed the test in <strong>{minutes} minutes & {seconds} seconds</strong>. The score is modest and indicates areas for improvement, suggesting further study or assistance may be beneficial.
</p>
                </li>
                <li>
                <p>Seeking additional study resources or assistance can help the student improve their performance. Overall, the student is recommended for the scholarship. 
</p>
                </li>
                </ul>
            </div>

             <div class="summary" id="summary2" style="display:{'block' if summary_to_display == 2 else 'none'};" >
                <h3>Student Summary</h3>
                <ul>
                <li>
                <p>The student achieved an average performance in the online scholarship test with an accuracy rate of <strong>{accuracy}%</strong>, indicating room for improvement in both accuracy and time efficiency. 
</p>
                </li>
                <li>
                <p>The student completed the test in <strong>{minutes} minutes & {seconds} seconds</strong>. While the effort to attempt questions is acknowledged, the overall score suggests a need for further study and practice to enhance understanding and skills. </p>
                </li>
                <li>
                <p>Unfortunately, according to the time-accuracy assessment model, the overall performance was average. The student should focus on developing a deeper understanding of the test material and improving time management strategies. </p>
                </li>
                </ul>
            </div>

             <div class="summary" id="summary3" style="display:{'block' if summary_to_display == 3 else 'none'};" >
                <h3>Student Summary</h3>
                <ul>
                <li>
                <p>The student exhibited below-average performance in the online scholarship test with an accuracy rate of <strong>{accuracy}%</strong>, indicating challenges in both accuracy and time management. 
</p>
                </li>
                <li>
                <p>The time taken to complete the test was <strong>{minutes} minutes & {seconds} seconds</strong>. While the effort to attempt questions is appreciated, significant improvement is needed in understanding the test material and effectively managing time.</p>
                </li>
                <li>
                <p>Unfortunately, according to the time-accuracy assessment model, the overall performance was below average. The student should prioritise seeking additional support and resources to address the gaps in understanding and time management skills.</p>
                </li>
                </ul>
            </div>

        </div>
        <div class="container2">
        <h1 class='generative'>AI-Powered Assessment</h1>
        <p class="assessment-desc"><em>This AI-Powered Assessment test analyzes user data in detail. It evaluates skills and knowledge accurately, providing personalized feedback and unbiased grading. The AI efficiently processes large data volumes, offering deep insights into user strengths and improvement areas.</em></p>
        {''.join([
            f'''
            <div class="summary2" style="{'padding-bottom: 170px;' if i == 4 else ''}">
            <h2>{topic.get("name")}</h2>
            <p>Average Time per Question: {float(topic.get("avg_time", 0.0)):.1f} seconds</p>
            <p>Correct Answers: {topic.get("correct_counts")} out of {topic.get("total")} ({topic.get("correct_percentage"):.1f}%)</p>
            <p>Incorrect Answers: {topic.get("incorrect_counts")} out of {topic.get("total")} ({topic.get("incorrect_percentage"):.1f}%)</p>
            <p>Unattempted: {topic.get("unattempted_counts")} out of {topic.get("total")} ({topic.get("unattempted_percentage"):.1f}%)</p>
            </div>
            ''' for i, topic in enumerate(topics_data)
        ])}
    </div>
    </div>

    <div class="summary2 swot-analysis">
        <h2 style="{'color:#103AC5'}">SWOT Analysis</h2>
        <p><strong class="areas">Strong Areas:</strong> {strong_areas}</p>
        <p><strong class="areas">Weak Areas:</strong> {weak_areas}</p>
        <p><strong class="areas">Opportunities: </strong>Topics <span class="area-value">{top_opportunities[0]}</span> and <span class="area-value">{top_opportunities[1]}</span> demonstrate high time efficiency scores, showing strong proficiency and potential for further mastery. This indicates efficient time management and deep understanding. Focusing on these topics can lead to advanced learning and higher scores through exploring related concepts and refining problem-solving skills.</p>
        <p><strong class="areas">Threats:</strong> However, <span class="area-value">{top_threats[0]}</span> and <span class="area-value">{top_threats[1]}</span> exhibit lower time efficiency scores, suggesting challenges in time management or understanding. To improve, prioritize enhancing time management skills, breaking down complex topics, and seeking additional study resources. Addressing these areas will enhance efficiency and comprehension, leading to better performance in assessments.</p>
    </div>
        
    <div class="passprob">
        <h2 style="{'color:#103AC5'}">Passing Probability</h2>
        <div>Based on your performance in the scholarship mock test, your estimated probability of passing the actual exam is <span class="pp" >{passing_result}%</span>. While this probability is derived from a detailed analysis of your mock test scores and may not fully reflect your potential, at Academically, we are committed to helping you surpass expectations and realize your aspirations. We'll collaborate closely to enhance your preparation and ensure you're primed for success on exam day.</div>
    </div>

    <div class="how">
        <h2>How <span style="color:#103AC5;font-weight:700">Academically</span> Can Help You Succeed:</h2> At<span style="color:#103AC5;font-weight:700"> Academically</span>, we're dedicated to helping you excel in your exam preparation. Join us and gain access to a comprehensive suite of resources designed to enhance your learning experience and boost your chances of success. Benefit from live interactive lectures with experienced instructors from around the world, a wide range of AI-powered mock exams to simulate your actual test environment, and detailed study handouts that cover all essential topics.
        <br>
        <br>
        Our personalized approach identifies your areas of improvement and provides targeted practice to help you overcome challenges. We also focus on strengthening your strong topics using advanced AI mocks. With a proven 93% success rate, we're confident in our ability to help you achieve outstanding results.
        <br>
        <br>
        Our goal is to provide you with the tools and support you need to confidently approach your exam and succeed. Join us at Academically and take the next step toward your academic success.
    </div>
    </body>
    </html>

    """
    return html_content


def generate_desclaimer():
    html_content = """
    <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Student Report</title>
            <style>
                html{
                    background-color: #f9f9f9;
                }
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    background-color: #f9f9f9;
                    color: #333;
                }
                .descl {
                    text-align: justify;
                    padding: 0px 50px;
                    padding-top: 60px;
                    color:gray;
                    padding-bottom:50px
                }
                .descl > h4 {
                    font-size: 20px;
                    padding-bottom: 20px;
                }
                .text {
                    margin-top: 200px;
                    text-align: center;
                    font-size: 20px;
                    padding-bottom: 450px;
                }
            </style>
        </head>
        <body>
            <div class="descl">
                <h4>Disclaimer:</h4>
                <ul>
                    <li>
                    <p>This report is intended solely for students who participated in the scholarship test. The data and analysis may not be relevant for students who haven't taken the test.</p>
                    </li>
                    <li>
                    <p>The analytics presented in this report are based on the responses and information provided by the test takers themselves. While we strive for accuracy, it's important to understand the data's origin.</p>
                    </li>
                    <li>
                    <p>The "passing probability" reflects your performance in the scholarship test, not necessarily the actual scholarship exam. It's a tool to help you make informed decisions, but it shouldn't be the sole factor.</p>
                    </li>
                    <li>
                    <p>We take steps to ensure the report's accuracy, but discrepancies or errors are always a possibility. We cannot assume responsibility for any such issues.</p>
                    </li>
                    <li>
                    <p>The provided probabilities are estimates based on test performance, not guarantees of your actual exam results.</p>
                    </li>
                    <li>
                    <p>We recommend that you independently verify any critical information presented in this report. Additionally, consulting with advisors or mentors can provide valuable insights for your scholarship journey.</p>
                    </li>
                    <li>
                    <p>The institution is not liable for any actions you take based on the information in this report. It's your responsibility to use this information alongside other resources and guidance.</p>
                    </li>
                </ul>

                <p class="text"> ---------------------------------------------- REPORT END ---------------------------------------------- </p>
            </div>
        </body>
    </html>
    """
    return html_content
