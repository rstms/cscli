# {{ config.project }} - {{ config.description.short }}

{{ config.description.medium }}


------
## Installation

Install with pip:
```
pip install {{ config.project }}
```

Optionally, install the dev/test modules:
```
pip install {{ config.project }}[dev]
```

------
## Module Dependencies
install:
```
{% for module in config.modules.install %}
{{ module }}
{% endfor %}
```

dev/test:
```
{% for module in config.modules.dev %}
{{ module }}
{% endfor %}
```

------
## Usage:
```
{{ config.usage }}
```

