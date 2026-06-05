// Cria um novo curso para o aluno autenticado
// sALVE
query "courses" verb=POST {
  description = "Cria um novo curso vinculado ao aluno autenticado"
  auth = "user"

  input {
    text name filters=trim {
      description = "Nome do curso ou instituição"
    }
  }

  stack {
    db.add "courses" {
      data = {
        user_id   : $auth.id
        name      : $input.name
        created_at: "now"
      }
    } as $new_course
  }

  response = $new_course
}
