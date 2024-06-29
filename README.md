# ox-engine

# about :

ox-engine core of assistant work flow and a prompt data processer engine

> under development not implemented complete system


### build from source :

```
pip install git+https://github.com/ox-ai/ox-engine.git
```
## Installation:

always build from source for latest and bug free version

> note : install all pre requisite and before installing ox-engine

### pre requisite

+  **[ox-doc](https://github.com/ox-ai/ox-doc.git)**
+  **[ox-db](https://github.com/ox-ai/ox-db.git)**

```
pip install git+https://github.com/ox-ai/ox-db.git
pip install git+https://github.com/ox-ai/ox-doc.git
```

### build from source

```
pip install git+https://github.com/ox-ai/ox-engine.git
```
### from pip
```
pip install ox-engine
```


## docs :

- refere [test.log.ipynb](./test.log.ipynb.ipynb) for understanding the underlying usage [docs.md](./docs/docs.md) will be released after major release



## directory tree :

```tree
.
├── __init__.py
├── ai
│   ├── llm.py
│   ├── md_path.py
│   ├── prompt.py
│   └── vector.py
└── util
    └── __init__.py
```
