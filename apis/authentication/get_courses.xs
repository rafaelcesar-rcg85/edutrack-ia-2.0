// Lista todos os cursos do aluno autenticado
query "courses" verb=GET {
  description = "Retorna todos os cursos pertencentes ao aluno autenticado"
  auth = "user"

  input {
  }

  stack {
    db.query "courses" {
      where = $db.courses.user_id == $auth.id
      sort = {courses.created_at: "desc"}
      return = {type: "list"}
    } as $courses
  }

  response = $courses
}
