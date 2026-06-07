query "user_role/{id}" verb=PATCH {
  description = "Updates the role of a user. Requires admin authentication."
  auth = "user"

  input {
    int id {
      description = "User ID to update"
    }
    text role {
      description = "New role for the user (e.g. 'admin' or 'user')"
    }
  }

  stack {
    db.get "user" {
      field_name = "id"
      field_value = $auth.id
    } as $current_user
    
    precondition ($current_user.role == "admin") {
      error_type = "accessdenied"
      error = "Unauthorized: You do not have admin privileges."
    }
    
    db.patch "user" {
      field_name = "id"
      field_value = $input.id
      data = {
        role: $input.role
      }
    } as $updated_user
  }
  
  response = $updated_user
}
