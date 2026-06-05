query "professores" verb=PATCH {
  description = "Atualiza um professor existente"
  auth = "user"

  input {
    int id {
      description = "ID do professor a ser atualizado"
    }
    text nome? filters=trim {
      description = "Novo nome do professor"
    }
    email email? {
      description = "Novo email do professor"
    }
    int course_id? {
      description = "Novo ID do curso"
    }
  }

  stack {
    // Busca o professor garantindo que pertence ao usuário
    db.get "professores" {
      where = ($db.professores.id == $input.id) && ($db.professores.user_id == $auth.id)
    } as $existing_prof
    
    precondition {
      if ($existing_prof == null) {
        throw "Professor não encontrado ou acesso negado"
      }
    }

    db.edit "professores" {
      id = $input.id
      data = {
        nome      : $input.nome ?? $existing_prof.nome
        email     : $input.email ?? $existing_prof.email
        course_id : $input.course_id ?? $existing_prof.course_id
      }
    } as $updated_prof
  }

  response = $updated_prof
}
