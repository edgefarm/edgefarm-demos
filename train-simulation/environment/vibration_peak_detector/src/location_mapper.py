import logging

_logger = logging.getLogger(__name__)


def map_timestamp_to_location(ts, locs):
    """
    Find the location (lat,lon) at time <ts> in <locs>.
    <locs> must be array with entries [time,lat,lon], oldest entry first

    :return: lat, lon, status
    <lat>, <lon>: averaged position at time (linear interpolation)
    <status>: "ok" - mapping done
                "ts-too-new" ts is newer than all timestamps in locs, or locs is empty
                "ts-too-old" ts is older than all timestamps in locs
    """
    status = "ts-too-old" if len(locs) > 0 else "ts-too-new"
    for idx in range(len(locs)):
        try:
            if ts >= locs[idx, 0] and ts < locs[idx + 1, 0]:
                td = ts - locs[idx, 0]
                f = td / (locs[idx + 1, 0] - locs[idx, 0])
                lat = (locs[idx + 1, 1] - locs[idx, 1]) * f + locs[idx, 1]
                lon = (locs[idx + 1, 2] - locs[idx, 2]) * f + locs[idx, 2]

                return lat, lon, "ok"
        except IndexError:
            status = "ts-too-new"
            break

    if len(locs > 0):
        _logger.debug(f"oldest: {ts-locs[0,0]} newest: {ts-locs[-1,0]}")
    return None, None, status


def find_last_unused_location_entry(ts, locs):
    """
    Find the last location entry that is no more used.
    i.e. the last entry that is older than the one just before <ts>.
    <locs> must be array with entries [time,lat,lon], oldest entry first

    :return: idx or None
    """
    idx = 0
    for idx in range(len(locs)):
        try:
            if ts >= locs[idx, 0] and ts < locs[idx + 1, 0]:
                break
        except IndexError:
            break
    if idx > 0:
        return idx - 1
