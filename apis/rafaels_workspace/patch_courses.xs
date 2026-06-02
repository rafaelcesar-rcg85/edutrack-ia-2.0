// Atualiza um curso existente do aluno autenticado
query "courses/{courses_id}" verb=PATCH {
  description = "Atualiza o nome de um curso pertencente ao aluno autenticado"
  auth = "user"

  input {
    int courses_id {
      description = "ID do curso a ser atualizado"
    }

    text name? filters=trim {
      description = "Novo nome do curso ou instituição"
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
      error = "Você não tem permissão para editar este curso."
    }

    db.patch "courses" {
      field_name = "id"
      field_value = $input.courses_id
      data = {
        name: $input.name
      }
    } as $updated_course
  }

  response = $updated_course
}
