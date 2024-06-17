# ox-engine

ox-engine core of assistant work flow and a prompt data processer engine

## to install :

```
pip install ox-engine
```

### build from source :

```
pip install git+https://github.com/ox-ai/ox-engine.git
```

## docs :

- refere [test.ipynb](./test.ipynb) for understanding the underlying usage [docs.md](./docs.md) will be released after major release

## lib implementation :

| Title                     | Status        | Description                                             |
| ------------------------- | ------------- | ------------------------------------------------------- |
| log                       | in progress   | log data base system                                    |
| vector integration        | in progress   | log vecctor data base                                   |
| demon search engine       | need to start | vector search                                           |
| query engine              |               | optimized vector search                                 |
| tree load                 |               | vector storage system                                   |
| key lang translator       |               | natural lang to key lang                                |
| plugin integration        |               | system to write add-on to intract with vector data base |
| data structurer as plugin |               | structure raw data to custom format                     |

## directory tree :

```tree
.
├── __init__.py
├── do.py
├── log.py
└── vector.py
```
