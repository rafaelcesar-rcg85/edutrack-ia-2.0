// Remove um curso do aluno autenticado
query "courses/{courses_id}" verb=DELETE {
  description = "Remove um curso pertencente ao aluno autenticado"
  auth = "user"

  input {
    int courses_id {
      description = "ID do curso a ser removido"
    }
  }

  stack {
    // Verifica se o curso pertence ao aluno autenticado
    db.get "courses" {
      field_name = "id"
      field_value = $input.courses_id
    } as $course

    precondition ($course.user_id == $auth.id) {
      description = "Garante que o curso pertence ao aluno autenticado"
      error_type = "accessdenied"
      error = "Você não tem permissão para remover este curso."
    }

    db.del "courses" {
      field_name = "id"
      field_value = $input.courses_id
    }
  }

  response = {}
}
