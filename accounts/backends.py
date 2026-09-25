from django.contrib.auth.backends import ModelBackend

class RoleBackend(ModelBackend):
    def get_group_permissions(self, user_obj, obj=None):
        """
        Returns a set of permission strings the user has from their custom roles.
        """
        permissions = super().get_group_permissions(user_obj, obj)
        
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return permissions
            
        # Get all permissions assigned to the user's custom roles
        role_perms = user_obj.roles.filter(
            permissions__isnull=False
        ).values_list(
            'permissions__content_type__app_label', 
            'permissions__codename'
        )
        
        # Format them as 'app_label.codename'
        custom_perms = {f"{app_label}.{codename}" for app_label, codename in role_perms}
        
        return permissions.union(custom_perms)
