# Change: Create `subject` table

## Why:
To support the academic subjects management in the EduTrack AI application. This table is necessary to store the subjects' data and associate them with the respective users.

## What:
A new database table named `subject` that includes fields for subject name, teacher, total hours, and a relationship (foreign key) to the `user` table.