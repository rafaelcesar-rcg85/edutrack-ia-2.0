query "professores" verb=POST {
  description = "Cria um novo professor vinculado a um curso e usuário"
  auth = "user"

  input {
    text nome filters=trim {
      description = "Nome do professor"
    }
    email email? {
      description = "Email do professor"
    }
    int course_id {
      description = "ID do curso"
    }
  }

  stack {
    db.add "professores" {
      data = {
        user_id   : $auth.id
        course_id : $input.course_id
        nome      : $input.nome
        email     : $input.email
        created_at: "now"
      }
    } as $new_prof
  }

  response = $new_prof
}
