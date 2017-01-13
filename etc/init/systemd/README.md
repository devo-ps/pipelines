### Start pipelines via `systemd`

- change [config](pipelines.sevice) accordingly

- `chmod 644 pipelines.service`
 
- `chown root:root pipelines.service`

- `cp pipelines.service /usr/lib/systemd/system/pipelines.service`

- `systemctl daemon-reload`

- `systemctl start pipelines`