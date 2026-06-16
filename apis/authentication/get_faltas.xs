// =============================================================
// apis/authentication/get_faltas.xs — GET /faltas
// =============================================================
// Endpoint que lista as faltas do aluno, filtradas por disciplina.
// Grupo: Authentication (canonical: iiiYAbKm)
//
// Método HTTP: GET (leitura)
// Autenticação: obrigatória (token JWT)
//
// Parâmetro opcional: disc_id
//   - Se fornecido → retorna apenas as faltas daquela disciplina
//   - Se omitido   → retorna TODAS as faltas do usuário
// =============================================================
// Lista as faltas do aluno, opcionalmente filtradas por disciplina
query "faltas" verb=GET {
  description = "Retorna as faltas do aluno, opcionalmente filtradas por disciplina"
  auth = "user"

  input {
    // disc_id é opcional (?) — o cliente pode ou não enviar este filtro
    int disc_id? {
      description = "ID da disciplina para filtrar as faltas"
    }
  }

  stack {
    // Bloco condicional: executa uma consulta diferente dependendo do filtro
    conditional {
      // Caso 1: disc_id foi fornecido — filtra pela disciplina
      if ($input.disc_id) {
        db.query "faltas" {
          where = ($db.faltas.user_id == $auth.id) && ($db.faltas.disc_id == $input.disc_id)
          // Ordena da falta mais recente para a mais antiga
          sort  = {faltas.data_falta: "desc"}
          return = {type: "list"}
        } as $faltas
      } else {
        // Caso 2: nenhum filtro → retorna todas as faltas do usuário
        db.query "faltas" {
          where  = $db.faltas.user_id == $auth.id
          sort   = {faltas.data_falta: "desc"}
          return = {type: "list"}
        } as $faltas
      }
    }
  }

  // Retorna a lista de faltas (filtrada ou completa)
  response = $faltas
}
