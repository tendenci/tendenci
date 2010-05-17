from base.auth import BasePermission
from pages.models import Page
from authority import register

class PagePermission(BasePermission):
    """
        Permissions for pages
    """
    label = 'page_permission'
    
register(Page, PagePermission)