# Cong•app

## Dev server

```
poetry install
poetry run uvicorn conga.app:app --reload
```

## Dev app

```
npm install
npm run dev
```

## Serve

```
poetry run uvicorn conga.app:app
npm run build && npm run serve
```

## Todo

- [ ] Fix finishing game
- [ ] Refactor app code as if I were a good programmer
- [ ] Only one endpoint that proxies server and app
- [ ] Host more than 1 game
