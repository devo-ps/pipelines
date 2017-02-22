import moment from 'moment';

export function relativeTime(timestamp) {
  if (!timestamp) {
    return 'No runs'
  }
  if (timestamp == 'now') {
    return 'Now'
  }
  return moment(timestamp, "YYYY-MM-DDThh:mm:ss.SSSSSS").fromNow();
}
