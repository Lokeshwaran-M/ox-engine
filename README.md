# ox-engine

ox-engine core of assistant work flow and a prompt data processer engine

## to install :

always build from source for latest and bug free version

```
pip install ox-engine
```

### build from source :

```
pip install git+https://github.com/ox-ai/ox-engine.git
```

## docs :

- refere [test.log.ipynb](./test.log.ipynb.ipynb) for understanding the underlying usage [docs.md](./docs/docs.md) will be released after major release

## features

### 1 ox-db :

to start vector db (ox-db) api run below commend refer [docs](./docs/api.log.md)

```
uvicorn ox_engine.api.log:app
```

## lib implementation :

| Title                     | Status | Description                                             |
| ------------------------- | ------ | ------------------------------------------------------- |
| log                       | ip     | log data base system                                    |
| vector integration        | ip     | log vecctor data base                                   |
| query engine              | ip     | vector search                                           |
| demon search engine       |        | optimized search                                        |
| tree load                 |        | vector storage system                                   |
| key lang translator       |        | natural lang to key lang                                |
| plugin integration        |        | system to write add-on to intract with vector data base |
| data structurer as plugin |        | structure raw data to custom format                     |


## directory tree :

```tree
.
├── __init__.py
├── ai
│   ├── llm.py
│   ├── md_path.py
│   ├── prompt.py
│   └── vector.py
├── api
│   ├── __init__.py
│   └── log.py
├── db
│   ├── __init__.py
│   └── log.py
└── util
    ├── __init__.py
    └── do.py
```
