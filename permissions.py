ROLE_PERMISSIONS = {
    'admin': {
        'can_manage_users': True,               # update user role(admin, host, umpire, user)
        'can_manage_tournaments': True,         # delete tournament (all)
        'can_manage_matches': True,             # delete match (all)
        'can_assign_umpire': True,              # assign umpire to a match (all match)
        'can_generate_schedule': True,          # generate match schedule (all tournament)
        'can_manage_registration': True,        # update each registration's status (all tournaments)
        'can_upload_registration_file': True,   # manually upload registration file (all tournaments)
        'can_generate_matches': True,           # generate match (all tournaments)
        'can_create_new_match': True,           # create new match (all tournaments)
    },
    
    'host': {
        'can_manage_users': True,               # update user role(admin, host, umpire, user) (only his tournament)
        'can_manage_tournaments': True,         # delete tournament (only his tournament)
        'can_manage_matches': True,             # delete match (only his tournament)
        'can_assign_umpire': True,              # assign umpire to a match (only his tournament)
        'can_generate_schedule': True,          # generate match schedule (only his tournament)
        'can_manage_registration': True,        # update each registration's status (only his tournament)
        'can_upload_registration_file': True,   # manually upload registration file (only his tournament)
        'can_generate_matches': True,           # generate match (only his tournament)
        'can_create_new_match': True,           # create new match (only his tournament)
    },

    'umpire': {
        'can_manage_users': False,               # update user role(admin, host, umpire, user) 
        'can_manage_tournaments': False,         # delete tournament
        'can_manage_matches': False,             # delete match 
        'can_assign_umpire': False,              # assign umpire to a match 
        'can_generate_schedule': False,          # generate match schedule 
        'can_manage_registration': False,        # update each registration's status
        'can_upload_registration_file': False,   # manually upload registration file 
        'can_generate_matches': False,           # generate match 
        'can_create_new_match': False,           # create new match 
    },

    'user': {
        'can_manage_users': False,               # update user role(admin, host, umpire, user) 
        'can_manage_tournaments': False,         # delete tournament
        'can_manage_matches': False,             # delete match 
        'can_assign_umpire': False,              # assign umpire to a match 
        'can_generate_schedule': False,          # generate match schedule 
        'can_manage_registration': False,        # update each registration's status
        'can_upload_registration_file': False,   # manually upload registration file 
        'can_generate_matches': False,           # generate match 
        'can_create_new_match': False,           # create new match 
    },
}

def has_function_permission(user, function_feature):
    if not user:
        return False

    if function_feature not in ROLE_PERMISSIONS['admin']:
        return False
    
    return ROLE_PERMISSIONS[user.role][function_feature]