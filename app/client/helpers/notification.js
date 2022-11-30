// TODO we better:
// a) try retrieve a icon file from the current site meta head
// b) fallback to use a pipelie logo
const icon = 'https://wiredcraft.com/assets/favicons/apple-touch-icon.png';
const hasNotificationFeature = typeof window.Notification === 'function';
const successEmoji = '🚀';
const failureEmoji = '🚨';

function tryAskForPermission(grantedCallback) {
  Notification.requestPermission().then(permission => {
    if (permission === 'granted') grantedCallback();
  });
}

function notifyTaskStatus(pipelineName, status = 'success') {
  let title;
  switch (status) {
    case 'success':
      title = `${successEmoji} ${status} ${pipelineName}`;
      break;
    case 'failure':
      title = `${failureEmoji} ${status} ${pipelineName}`;
      break;
    default:
      title = `${status} ${pipelineName}`;
  }
  return spawnNotification(title);
}

function spawnNotification(title, body) {
  const options = { icon };
  if (body) options.body = body;
  return new Notification(title, options);
}

export function tryNotifyTaskStatus(pipelineName, type = 'success') {
  const notify = () => notifyTaskStatus(pipelineName, type);
  if (hasNotificationFeature === false) return;
  if (Notification.permission === 'granted') return notify();
  if (Notification.permission !== 'denied') {
    tryAskForPermission(notify);
  }
}
