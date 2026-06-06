query "user_password/{id}" verb=PATCH {
  description = "Updates the password of a user. Requires admin authentication."
  auth = "user"

  input {
    int id {
      description = "User ID to update"
    }
    password password {
      description = "New password for the user"
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
        password: $input.password
      }
    } as $updated_user
  }
  
  response = $updated_user
}
