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

## need to update:

    - push -> to accept list of datas
    - pull -> to accept docs
    - pull -> to accept list of keys, times, dates, docs
    - vector.search -> all sim metrics

## directory tree :

```tree
.
├── __init__.py
├── api
│   └── log.py
├── do.py
├── log.py
└── vector.py
```
