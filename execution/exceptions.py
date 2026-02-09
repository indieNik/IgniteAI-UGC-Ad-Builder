"""
Pipeline exception classes for graceful failure handling.
"""

class PipelineFailureException(Exception):
    """
    Exception raised when a pipeline stage fails and should trigger graceful failure.
    This includes automatic credit refunds and user notifications.
    """
    def __init__(self, stage: str, reason: str, user_message: str, requires_refund: bool = True):
        """
        Args:
            stage: Pipeline stage where failure occurred (e.g., 'visual_dna', 'script_generation')
            reason: Technical reason for failure (logged for debugging)
            user_message: User-friendly message to display
            requires_refund: Whether to refund credits (default: True)
        """
        self.stage = stage
        self.reason = reason
        self.user_message = user_message
        self.requires_refund = requires_refund
        super().__init__(f"[{stage}] {reason}")
    
    def to_dict(self):
        """Convert to dictionary for storage/transmission"""
        return {
            "stage": self.stage,
            "reason": self.reason,
            "user_message": self.user_message,
            "requires_refund": self.requires_refund
        }


class QuotaExceededException(Exception):
    """
    Raised when daily API quota is exceeded.
    This triggers immediate fallback without retries, as daily quotas
    cannot be recovered by waiting.
    """
    pass
