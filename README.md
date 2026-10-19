# EduDesk: Student Management Dashboard

A student management web app built with Python and Streamlit. Add students and teachers, record grades, and see everything on a dashboard. All data is saved in a simple JSON file, so there is no database to set up.

## EduDesk dashboard
<img width="1822" height="672" alt="1" src="https://github.com/user-attachments/assets/452d5975-d331-48af-88af-6a94c0fa8360" />

## Features
- **Dashboard:** total students, teachers and subjects, average marks, charts by subject and age, top performers, and students still waiting for grades
- **Students:** search, add and delete students, and add, update or remove grades from each student's profile
- **Teachers:** add and remove teachers, with a count of students graded in their subject
- **Safe inputs:** duplicate roll numbers or employee IDs and invalid emails are rejected with a clear message, and deletes need a confirmation
- **Data page:** view the raw JSON, download it, or restore the sample data

## Tech Stack
Python, Streamlit, pandas



### How to run
```
pip install streamlit
streamlit run app.py
```
For the terminal version: 
```
python main.py
```

## Screenshot
<img width="1852" height="475" alt="3" src="https://github.com/user-attachments/assets/c6ee29f7-adb4-4cae-b90a-12801259baad" />
<img width="1856" height="821" alt="2" src="https://github.com/user-attachments/assets/852e01bc-552e-456c-ab45-085edd6315d7" />
