from accounts.models import Profile


def reset_completed_cnt():
    profiles = Profile.objects.all()
    for profile in profiles:
        profile.completed_cnt = 0
        profile.save()
