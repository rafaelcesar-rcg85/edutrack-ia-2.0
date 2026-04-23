# Database Table: subject

## Description
This table stores the academic subjects managed by the users in the EduTrack AI platform.

## Schema Definition

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | integer | Yes | Primary internal ID |
| `created_at` | timestamp | Yes | Creation timestamp |
| `name` | text | Yes | The name of the subject |
| `teacher` | text | No | The name of the teacher responsible for this subject |
| `total_hours` | integer | No | Total hours assigned to the subject |
| `user_id` | index/foreign key | Yes | Foreign key relationship referencing the `user` table constraints |

## Relations
* **user_id**: References `user.id`. Each subject is created/managed by a specific user.
