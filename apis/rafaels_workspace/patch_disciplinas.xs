// =============================================================
// apis/.../patch_disciplinas.xs — PATCH /disciplinas
// =============================================================
// Endpoint que atualiza uma disciplina existente do aluno autenticado.
//
// Método HTTP: PATCH (atualização parcial)
// Autenticação: obrigatória (token JWT)
//
// Fluxo com verificação de propriedade:
//   1. Busca a disciplina que pertença ao usuário logado
//   2. Se não existir, retorna erro (acesso negado / não encontrada)
//   3. Atualiza apenas os campos enviados (usa ?? para manter o valor atual)
//
// Operador ?? (Null Coalescing):
//   $input.nome ?? $existing_disc.nome
//   → se $input.nome for null (não enviado), usa o valor atual do banco
//   → isso permite atualizar apenas UM campo sem enviar os outros
// =============================================================

// Atualiza uma disciplina existente
query "disciplinas" verb=PATCH {
  description = "Atualiza uma disciplina existente"
  auth = "user"

  input {
    // ID da disciplina a ser atualizada — obrigatório para identificar o registro
    int id {
      description = "ID da disciplina a ser atualizada"
    }
    // Campos opcionais (marcados com ?): só atualiza os que forem enviados
    text nome? filters=trim {
      description = "Novo nome da disciplina"
    }
    int prof_id? {
      description = "Novo ID do professor"
    }
    int curso_id? {
      description = "Novo ID do curso"
    }
    int total_aulas? {
      description = "Novo total de aulas previstas"
    }
    int limite_faltas? {
      description = "Novo limite máximo de faltas"
    }
    int peso_map? {
      description = "Novo peso da MAP"
    }
    int peso_prova? {
      description = "Novo peso da Prova"
    }
    int peso_pai? {
      description = "Novo peso da Prova PAI"
    }
  }

  stack {
    // Passo 1: Busca a disciplina garantindo que pertence ao usuário
    // A condição combina dois filtros: id correto E user_id correto
    // Isso previne que um usuário edite disciplinas de outro
    db.query "disciplinas" {
      where = ($db.disciplinas.id == $input.id) && ($db.disciplinas.user_id == $auth.id)
      return = {type: "single"}
    } as $existing_disc
    
    // Passo 2: Verifica se o registro foi encontrado
    // Se $existing_disc for null (não encontrado ou não pertence ao usuário), lança erro
    precondition {
      if ($existing_disc == null) {
        throw "Disciplina não encontrada ou acesso negado"
      }
    }

    // Passo 3: Atualiza o registro com os novos valores
    // Operador ?? (null coalescing): usa o valor enviado; se for null, mantém o atual
    db.edit "disciplinas" {
      field_name = "id"
      field_value = $input.id
      data = {
        // Se $input.nome for enviado → usa; senão → mantém $existing_disc.nome
        nome         : $input.nome         ?? $existing_disc.nome
        prof_id      : $input.prof_id      ?? $existing_disc.prof_id
        curso_id     : $input.curso_id     ?? $existing_disc.curso_id
        total_aulas  : $input.total_aulas  ?? $existing_disc.total_aulas
        limite_faltas: $input.limite_faltas ?? $existing_disc.limite_faltas
        peso_map     : $input.peso_map     ?? $existing_disc.peso_map
        peso_prova   : $input.peso_prova   ?? $existing_disc.peso_prova
        peso_pai     : $input.peso_pai     ?? $existing_disc.peso_pai
      }
    } as $updated_disc
  }

  // Retorna a disciplina com os dados atualizados
  response = $updated_disc
}
