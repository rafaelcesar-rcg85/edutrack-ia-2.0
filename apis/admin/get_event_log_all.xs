query "event_log_all" verb=GET {
  description = "Returns all events from event_log for admin analytics."
  auth = "user"

  input {}

  stack {
    db.get "user" {
      field_name = "id"
      field_value = $auth.id
    } as $current_user

    precondition ($current_user.role == "admin") {
      error_type = "accessdenied"
      error = "Unauthorized: You do not have admin privileges."
    }

    // Busca todos os eventos do event_log (sem filtro)
    db.query "event_log" {
      sort = {created_at: "desc"}
      return = {type: "list"}
    } as $all_events
  }

  response = $all_events
}
