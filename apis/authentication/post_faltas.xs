// =============================================================
// apis/authentication/post_faltas.xs — POST /faltas
// =============================================================
// Endpoint que registra uma nova falta para o aluno autenticado.
// Grupo: Authentication (canonical: iiiYAbKm)
//
// Método HTTP: POST (criação)
// Autenticação: obrigatória (token JWT)
//
// Campos obrigatórios:
//   - disc_id:    disciplina onde a falta ocorreu
//   - data_falta: data da aula que o aluno faltou
//
// Campos opcionais:
//   - course_id:     curso (para facilitar filtros)
//   - justificativa: motivo ou observação da falta
//
// O user_id é obtido automaticamente do token JWT ($auth.id).
// =============================================================
// Registra uma nova falta vinculada a uma disciplina
query "faltas" verb=POST {
  description = "Registra uma nova falta vinculada a uma disciplina do aluno"
  auth = "user"

  input {
    // ID da disciplina — obrigatório
    int disc_id {
      description = "ID da disciplina onde a falta ocorreu"
    }
    // ID do curso — opcional, facilita filtros futuros
    int course_id? {
      description = "ID do curso ao qual a disciplina pertence"
    }
    // Data da aula em que o aluno faltou — obrigatório
    timestamp data_falta {
      description = "Data da aula em que a falta ocorreu"
    }
    // Justificativa ou observação — opcional
    text justificativa? filters=trim {
      description = "Justificativa ou observação sobre a falta"
    }
    // Peso da falta: número de aulas perdidas neste dia (padrão: 1)
    // Ex: disciplina com 2 aulas seguidas no mesmo dia → peso = 2
    int peso? {
      description = "Número de aulas perdidas neste registro (padrão: 1)"
    }
  }

  stack {
    // db.add: insere o registro de falta na tabela "faltas"
    db.add "faltas" {
      data = {
        // O user_id é obtido do token JWT — garante isolamento entre usuários
        user_id      : $auth.id
        disc_id      : $input.disc_id
        course_id    : $input.course_id    // null se não enviado
        data_falta   : $input.data_falta
        justificativa: $input.justificativa // null se não enviado
        peso         : $input.peso ?? 1    // padrão 1 se não enviado
        created_at   : "now"
      }
    } as $new_falta
  }

  // Retorna o registro de falta criado (com o ID gerado pelo banco)
  response = $new_falta
}
