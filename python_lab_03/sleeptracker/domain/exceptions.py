class SleepTrackerError(Exception):
    pass

class InvalidSleepTimeError(SleepTrackerError):
    pass

class InvalidSleepQualityError(SleepTrackerError):
    pass    