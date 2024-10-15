# `command-fn`

**Usage**:

```console
$ command-fn [OPTIONS]
```

**Options**:

* `--config-paths TEXT`: Paths to config files  [required]
* `--sweep-paths TEXT`: Paths to sweep files  [default: <class 'list'>]
* `--path TEXT`: Path to the dataset. Maps to 'data.dataset.path'
* `--num-layers INTEGER`: Number of layers. Maps to 'model.num_layers'
* `--num-epochs INTEGER`: Number of epochs. Maps to 'training.num_epochs'
* `--num-workers INTEGER`: Number of workers for loading the dataset. Maps to 'data.num_workers'
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.
