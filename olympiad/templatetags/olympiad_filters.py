from django import template
import logging

logger = logging.getLogger(__name__)
register = template.Library()

@register.filter
def filter_by_user(submissions, user_id):
    """Фильтрует набор отправленных заданий по user_id"""
    try:
        # Преобразуем user_id в целое число, если это строка
        if isinstance(user_id, str):
            user_id = int(user_id)
            
        # Проверяем, что submissions не None
        if submissions is None:
            logger.warning(f"filter_by_user: submissions is None for user_id {user_id}")
            return []
            
        # Проверяем, что у submissions есть user или enrollment.user
        filtered_submissions = []
        for submission in submissions:
            submission_user_id = None
            
            if hasattr(submission, 'user') and hasattr(submission.user, 'id'):
                submission_user_id = submission.user.id
            elif hasattr(submission, 'enrollment') and hasattr(submission.enrollment, 'user'):
                submission_user_id = submission.enrollment.user.id
                
            if submission_user_id == user_id:
                filtered_submissions.append(submission)
                
        return filtered_submissions
    except Exception as e:
        logger.error(f"Error in filter_by_user: {str(e)}")
        return [] 