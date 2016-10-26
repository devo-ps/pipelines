


# Running the API

```
pip install -r requirements.txt
PYTHONPATH=. bin/pipelines api --workspace=fixtures/workspace
```

It runs on port 8888.


# Frontend development


- First make sure you have the API running on port 8888!
- Then run the app
```
cd app
npm install
NODE_ENV=test npm start
```

- Open browser on: http://localhost:3001/