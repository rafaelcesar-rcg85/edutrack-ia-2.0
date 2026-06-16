// =============================================================
// tables/836282_professores.xs — Tabela de Professores
// =============================================================
// Define a estrutura (schema) da tabela "professores" no banco
// de dados do Xano.
//
// Esta tabela armazena os professores cadastrados por cada aluno.
// Relacionamentos:
//   professores.course_id → curso.id  (curso ao qual pertence)
//   professores.user_id   → user.id     (aluno dono do registro)
// =============================================================

table professores {
  // auth = false: esta tabela não requer autenticação para ser acessada
  // internamente pelo Xano (a segurança é feita nas APIs com auth = "user")
  auth = false

  schema {
    // Identificador único do professor (chave primária, auto-incremental)
    int id
  
    // Nome do professor — campo obrigatório (sem ?)
    text nome
  
    // E-mail de contato do professor — campo opcional (marcado com ?)
    email email?
  
    // Chave estrangeira: ID do curso ao qual o professor pertence
    // O campo "table" define o relacionamento com a tabela "curso"
    int course_id? {
      table = "curso"
    }
  
    // Chave estrangeira: ID do usuário (aluno) dono deste registro
    // Garante que cada professor pertence a um único aluno cadastrado
    int user_id {
      table = "user"
    }
  
    // Data de criação do registro — preenchida automaticamente com o momento atual
    // "?=now" significa: opcional na entrada, mas com valor padrão = hora atual
    timestamp created_at?=now
  }

  // Índices otimizam a velocidade das consultas no banco de dados
  index = [
    // Índice primário pelo campo "id" — garante unicidade e buscas rápidas por ID
    {type: "primary", field: [{name: "id"}]}
    {
      // Índice composto (btree) por user_id + course_id
      // Acelera consultas como: "todos os professores do usuário X no curso Y"
      type : "btree"
      field: [{name: "user_id"}, {name: "course_id"}]
    }
  ]
}