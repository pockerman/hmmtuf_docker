class DBTaskNotFound(Exception):

    def __init__(self, task_id: str, task_type: str='UNKNOWN'):
        self.message = 'DB Task with task_id=' + task_id + \
                       " and task_type=" + task_type + \
                       " does not exist"

    def __str__(self) -> str:
        return self.message
