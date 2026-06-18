// =============================================================
// apis/.../patch_tarefas.xs — PATCH /tarefas
// =============================================================
// Endpoint que atualiza uma tarefa/nota existente do aluno autenticado.
//
// Método HTTP: PATCH (atualização parcial)
// Autenticação: obrigatória (token JWT)
//
// Fluxo com segurança:
//   1. Busca a tarefa filtrando por id E user_id
//   2. Se não encontrada → lança erro
//   3. Atualiza os campos usando ?? (preserva valores não enviados)
//
// Todos os campos de atualização são opcionais —
// o cliente pode enviar apenas o que mudou.
// =============================================================

// Atualiza uma tarefa existente
query "tarefas" verb=PATCH {
  description = "Atualiza uma tarefa existente"
  auth = "user"

  input {
    // ID da tarefa a ser atualizada — obrigatório para identificar o registro
    int id {
      description = "ID da tarefa a ser atualizada"
    }
    // Campos opcionais: apenas os enviados serão considerados para atualização
    text nome? filters=trim {
      description = "Novo nome da tarefa"
    }
    int disc_id? {
      description = "Novo ID da disciplina"
    }
    int course_id? {
      description = "Novo ID do curso"
    }
    text status? {
      description = "Novo status da tarefa"
    }
    decimal nota? {
      description = "Nova nota obtida"
    }
    timestamp data_entrega? {
      description = "Nova data de entrega"
    }
    text tipo? {
      description = "Novo tipo de avaliação"
    }
  }

  stack {
    // Passo 1: Busca a tarefa verificando que pertence ao usuário logado
    // A dupla condição (id + user_id) impede que um usuário edite
    // tarefas de outro usuário — segurança em nível de objeto (BOLA prevention)
    db.query "tarefas" {
      where = ($db.tarefas.id == $input.id) && ($db.tarefas.user_id == $auth.id)
      return = {type: "single"}
    } as $existing_tarefa
    
    // Passo 2: Se não encontrou → lança erro e interrompe
    precondition {
      if ($existing_tarefa == null) {
        throw "Tarefa não encontrada ou acesso negado"
      }
    }

    // Passo 3: Atualiza o registro com os novos valores
    // O operador ?? garante que, se o campo não foi enviado (null),
    // o valor anterior ($existing_tarefa.campo) seja mantido
    db.edit "tarefas" {
      field_name = "id"
      field_value = $input.id
      data = {
        nome         : $input.nome         ?? $existing_tarefa.nome
        disc_id      : $input.disc_id      ?? $existing_tarefa.disc_id
        course_id    : $input.course_id    ?? $existing_tarefa.course_id
        status       : $input.status       ?? $existing_tarefa.status
        nota         : $input.nota         ?? $existing_tarefa.nota
        data_entrega : $input.data_entrega ?? $existing_tarefa.data_entrega
        tipo         : $input.tipo         ?? $existing_tarefa.tipo
      }
    } as $updated_tarefa
  }

  // Retorna a tarefa com todos os dados atualizados
  response = $updated_tarefa
}
