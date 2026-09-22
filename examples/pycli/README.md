# greet

A tiny argparse CLI that greets people in three languages. It exists so
evergif has a realistic Python project to record.

<!-- evergif:start -->
![Terminal demo: greet --help lists the hello and bye subcommands, then greet hello --name Ada --lang fr prints Bonjour, Ada and --shout prints it in capitals](demo/evergif.gif)
<!-- evergif:end -->

## Usage

```bash
python3 greet.py hello --name Ada
python3 greet.py hello --name Ada --lang fr --shout
python3 greet.py bye --name Ada
```
