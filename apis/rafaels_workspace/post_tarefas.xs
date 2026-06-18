// =============================================================
// apis/.../post_tarefas.xs — POST /tarefas
// =============================================================
// Endpoint que cria uma nova tarefa/nota para o aluno autenticado.
//
// Método HTTP: POST (criação)
// Autenticação: obrigatória (token JWT)
//
// Uma tarefa possui dois modos baseados no status:
//   - "Concluída"     → exige o campo "nota" (0.0 a 10.0)
//   - "Para Entregar" → exige o campo "data_entrega" (timestamp)
//
// Todos os campos do input são inseridos diretamente no banco
// junto com o user_id do usuário logado ($auth.id).
// =============================================================

// Cria uma nova tarefa vinculada a uma disciplina e um curso
query "tarefas" verb=POST {
  description = "Cria uma nova tarefa vinculada a uma disciplina e um curso"
  auth = "user"

  input {
    // Nome ou título da atividade — obrigatório
    // filters=trim: remove espaços no início e no final
    text nome filters=trim {
      description = "Nome da tarefa"
    }
    // ID da disciplina à qual esta tarefa pertence — obrigatório
    int disc_id {
      description = "ID da disciplina"
    }
    // ID do curso ao qual esta tarefa está vinculada — obrigatório
    int course_id {
      description = "ID do curso"
    }
    // Status: "Concluída" ou "Para Entregar" — obrigatório
    text status {
      description = "Status da tarefa"
    }
    // Nota obtida — opcional (preenchido apenas para tarefas concluídas)
    // O tipo "decimal" permite valores como 8.5, 9.75 etc.
    decimal nota? {
      description = "Nota obtida na atividade"
    }
    // Data de entrega — opcional (preenchida para tarefas pendentes)
    // O tipo "timestamp" armazena data e hora
    timestamp data_entrega? {
      description = "Data de entrega para atividades futuras"
    }
    // Tipo de avaliação — opcional (MAP, PROVA, SUB, PAI, OUTRO)
    text tipo? {
      description = "Tipo de avaliação"
    }
  }

  stack {
    // db.add: insere todos os campos na tabela "tarefas"
    db.add "tarefas" {
      data = {
        // O user_id é obtido do token JWT — garante isolamento entre usuários
        user_id      : $auth.id
        course_id    : $input.course_id
        disc_id      : $input.disc_id
        nome         : $input.nome
        status       : $input.status
        nota         : $input.nota         // null se não enviado
        data_entrega : $input.data_entrega  // null se não enviado
        tipo         : $input.tipo         // null se não enviado
        // "now" registra automaticamente o timestamp atual
        created_at   : "now"
      }
    } as $new_tarefa  // Variável com o objeto da tarefa criada
  }

  // Retorna a tarefa recém-criada com o ID gerado pelo banco
  response = $new_tarefa
}
