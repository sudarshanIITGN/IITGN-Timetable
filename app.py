import pandas as pd
import re
from datetime import datetime
from flask import Flask, request, render_template

app = Flask(__name__)

def remove_bracketed_content(*args):
    """Remove content inside parentheses (and the parentheses themselves) from all input strings and concatenate them."""
    cleaned_parts = [re.sub(r"\s*\(.*?\)", "", s).strip() for s in args if isinstance(s, str)]
    return ', '.join(cleaned_parts)

def find_lecture_time(subject_inputs, df2):
    time_slots = {
        "A1": "Monday, 8:30 - 9:50",
        "B1": "Tuesday, 8:30 - 9:50",
        "A2": "Wednesday, 8:30 - 9:50",
        "C2": "Thursday, 8:30 - 9:50",
        "B2": "Friday, 8:30 - 9:50",
        "C1": "Monday, 10:00 - 11:20",
        "D1": "Tuesday, 10:00 - 11:20",
        "E1": "Wednesday, 10:00 - 11:20",
        "D2": "Thursday, 10:00 - 11:20",
        "E2": "Friday, 10:00 - 11:20",
        "F1": "Monday, 11:30 - 12:50",
        "G1": "Tuesday, 11:30 - 12:50",
        "H2": "Wednesday, 11:30 - 12:50",
        "F2": "Thursday, 11:30 - 12:50",
        "G2": "Friday, 11:30 - 12:50",
        "T1": "Monday, 13:00 - 14:00",
        "T2": "Tuesday, 13:00 - 14:00",
        "T3": "Wednesday, 13:00 - 14:00",
        "O1": "Thursday, 13:00 - 14:00",
        "O2": "Friday, 13:00 - 14:00",
        "I1": "Monday, 14:00 - 15:20",
        "J1": "Tuesday, 14:00 - 15:20",
        "I2": "Wednesday, 14:00 - 15:20",
        "K2": "Thursday, 14:00 - 15:20",
        "J2": "Friday, 14:00 - 15:20",
        "K1": "Monday, 15:30 - 16:50",
        "L1": "Tuesday, 15:30 - 16:50",
        "M1": "Wednesday, 15:30 - 16:50",
        "L2": "Thursday, 15:30 - 16:50",
        "M2": "Friday, 15:30 - 16:50",
        "H1": "Monday, 17:00 - 18:20",
        "N1": "Tuesday, 17:00 - 18:20",
        "P1": "Wednesday, 17:00 - 18:20",
        "N2": "Thursday, 17:00 - 18:20",
        "P2": "Friday, 17:00 - 18:20"
    }

    results = []
    scheduled_slots = {}
    conflicts = []
    timetable = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}

    def parse_time(time_str):
        """Parse time in 'HH:MM - HH:MM' format and return start time as datetime object."""
        return datetime.strptime(time_str.split(' - ')[0], '%H:%M')

    for subject_input in subject_inputs:
        found = False
        for index, row in df2.iterrows():
            course_name = row['Course Name'] if isinstance(row['Course Name'], str) else ''
            course_code = row['Course Code'] if isinstance(row['Course Code'], str) else ''
            if subject_input.strip() == course_name or subject_input.strip() == course_code:
                found = True
                lecture_tutorial_time = f"{row['Lecture']}, {row['Tutorial']}, {row['Lab']}"
                lecture_time = remove_bracketed_content(lecture_tutorial_time)
                lecture_slots = lecture_time.split(',')
                new_lecture_slots = [item.strip() for item in lecture_slots if item.strip() != 'nan']
                lecture_times = [time_slots[slot] for slot in new_lecture_slots]
                
                for slot in new_lecture_slots:
                    if slot not in scheduled_slots:
                        scheduled_slots[slot] = (course_name, course_code)
                    else:
                        conflict_course_name, conflict_course_code = scheduled_slots[slot]
                        conflicts.append(f"Conflict detected for {course_name} ({course_code}) and {conflict_course_name} ({conflict_course_code}) at {time_slots[slot]}\n")
                        day = time_slots[slot].split(',')[0]
                        timetable[day].append((parse_time(time_slots[slot].split(',')[1].strip()), f"{time_slots[slot].split(',')[1].strip()}, {course_name} ({course_code}) or {conflict_course_name} ({conflict_course_code})"))
                        continue

                    day = time_slots[slot].split(',')[0]
                    timetable[day].append((parse_time(time_slots[slot].split(',')[1].strip()), f"{time_slots[slot].split(',')[1].strip()}, {course_name} ({course_code})"))
                break
        if not found:
            results.append(f"Subject not found: {subject_input.strip()}")

    if conflicts:
        results.append("Conflicts:")
        results.extend(conflicts)

    for day, schedule in timetable.items():
        if schedule:
            results.append(f"{day}:")
            # Sort the schedule for each day by the parsed time
            sorted_schedule = sorted(schedule, key=lambda x: x[0])
            for _, entry in sorted_schedule:
                results.append(f"    {entry}")
            results.append("")  # Add a blank line for separation

    return '\n'.join(results)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/timetable', methods=['POST'])
def timetable():
    subject_input = request.form['subjects']
    subject_inputs = [subject.strip() for subject in subject_input.split(',')]
    
    df2 = pd.read_csv(r'C:\Users\Sudhashan\Desktop\IITGN Timetable\New Experiment\static\Timetable 2024-25, Sem-I - Time table.csv')
    
    result = find_lecture_time(subject_inputs, df2)
    
    return result.replace('\n', '<br>')

if __name__ == '__main__':
    app.run(debug=True)
