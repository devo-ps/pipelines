### Start pipelines via `systemd`

alter [config](pipelines.service) file accordingly

```bash 
chmod 644 pipelines.service
sudo chown root:root pipelines.service
sudo cp pipelines.service /usr/lib/systemd/system/pipelines.service
sudo systemctl daemon-reload
sudo systemctl start pipelines
```