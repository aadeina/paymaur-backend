from django.utils import timezone
from .models import SimpleKYC, PopulationRecord

def verify_against_population(nni, full_name):
    """
    Checks the provided NNI & name against the simulated government registry.
    """
    try:
        record = PopulationRecord.objects.get(nni=nni)
    except PopulationRecord.DoesNotExist:
        return False, "NNI not found in government database"

    normalize = lambda s: " ".join(s.lower().strip().split())
    if normalize(record.full_name) == normalize(full_name):
        return True, "Exact match"
    else:
        return False, f"Name mismatch. Found record: {record.full_name}"


def process_kyc_submission(user, nni, full_name):
    """
    Creates or updates a KYC record and verifies against simulated data.
    """
    kyc, created = SimpleKYC.objects.update_or_create(
        user=user,
        defaults={"nni": nni, "full_name": full_name, "status": "PENDING"},
    )

    is_valid, reason = verify_against_population(nni, full_name)
    if is_valid:
        kyc.status = "VERIFIED"
        kyc.verified_at = timezone.now()
        kyc.notes = reason
        kyc.save()
        user.is_verified = True
        user.save()
    else:
        kyc.status = "PENDING"
        kyc.notes = reason
        kyc.save()

    return kyc
