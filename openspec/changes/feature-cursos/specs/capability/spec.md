# courses Specification

## Purpose
Estabelecer a arquitetura de dados necessária para suportar múltiplas instituições de ensino ou cursos sob o mesmo usuário no EduTrack AI.

## ADDED Requirements

### Requirement: Create courses table
O sistema SHALL armazenar informações de cursos atreladas ao usuário.

#### Scenario: User creates a new course
- **WHEN** user sends POST to /courses
- **THEN** system stores the course associated with the user_id

### Requirement: Link disciplines to courses
O sistema SHALL vincular obrigatoriamente disciplinas a um curso específico.

#### Scenario: User creates a discipline
- **WHEN** user creates a new discipline
- **THEN** system requires a valid course_id and links the discipline to that course
