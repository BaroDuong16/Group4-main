from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str  # Update this line
import six

class InviteTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, invited_candidate, timestamp):
        return (
            str(invited_candidate.pk) + 
            str(timestamp) + 
            str(invited_candidate.invitation_date)
        )

invite_token_generator = InviteTokenGenerator()
