


# Running the API

```
pip install -r requirements.txt
PYTHONPATH=. bin/pipelines server --workspace=test/fixtures/workspace
```

It runs on port 8888.


# Frontend development


- First make sure you have the API running on port 8888!
- Then run the app
```
cd app
npm install
NODE_ENV=test API_HOST=http://127.0.0.1:8888 npm start
```

- Open browser on: http://localhost:3001/
