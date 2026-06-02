query "disciplinas" verb=DELETE {
  description = "Deleta uma disciplina existente"
  auth = "user"

  input {
    int id {
      description = "ID da disciplina a ser deletada"
    }
  }

  stack {
    // Busca a disciplina garantindo que pertence ao usuário
    db.get "disciplinas" {
      where = ($db.disciplinas.id == $input.id) && ($db.disciplinas.user_id == $auth.id)
    } as $existing_disc
    
    precondition {
      if ($existing_disc == null) {
        throw "Disciplina não encontrada ou acesso negado"
      }
    }

    db.delete "disciplinas" {
      where = $db.disciplinas.id == $input.id
    }
  }

  response = {
    success: true
    message: "Disciplina deletada com sucesso"
  }
}
