class NotificationService:
    @staticmethod
    def send_approval_email(user_email: str, resource_name: str):
        print(f"NOTIFICATION: Sending approval email to {user_email} for {resource_name}")

    @staticmethod
    def send_rejection_email(user_email: str, resource_name: str):
        print(f"NOTIFICATION: Sending rejection email to {user_email} for {resource_name}")