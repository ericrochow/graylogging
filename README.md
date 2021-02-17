# graylogging

Graylogging is an extension to the built-in logging module that allows logs to be written directly to Graylog via the GELF input rather than feeding from a flat file.

## Installation

The package can be installed by one of the following methods:

### PIP

    pip install graylogging

### Pipenv

    pipenv install graylogging

## General Use


### Initialization

Import both the `logging` and the `graylogging` module:

    import logging
    import graylogging

After those have been imported, you can use both the GraylogHandler and GraylogFormatter classes like the other built-in Formatters and Handlers:

    logger = logging.getLogger(name)
    gh = GraylogHandler(graylog_server, gelf_port, transport="tcp", appname="MyKickassApp")
    gh.setFormatter(GraylogFormatter)
    logger.addHandler(gh)
    logger.setLevel(logging.DEBUG)

The transport options are "tcp", "udp", and "http"; the correct choice will depend on the Graylog input configuration. 

This handler could also be used in conjunction with another handler. For example if it's desired to output the logs to console as well, we can accomplish this with the following example:

    graylog_server = "graylog.contoso.com"
    gelf_port = 12201
    appname = "MyKickassApp"
    log_level = logging.INFO
    logger = logging.getLogger(name)
    logger.propogate = False
    logger.disable_existing_loggers = True
    console_formatter = logging.Formatter(
        "%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s"
    )
    sh = logging.StreamHandler()
    sh.setFormatter(console_formatter)
    logger.handlers = [ch]
    gh = GraylogHandler(graylog_server, gelf_port, transport="http", appname=appname)
    gh.setFormatter(GraylogFormatter)
    logger.addHandler(gh)
    logger.setLevel(log_level)

You should be ready to roll now.

### Shipping actual log messages:

One logging has been initialized, graylogging can be used just like the built-in logging module:

    logger.debug(message)
    logger.info(message)
    logger.warning(message)
    logger.error(message)
    logger.critical(message)
    logger.exception(message)

## Enhancements

### JSON payloads

Graylogging can be fed either a string as normal, or a dict that will be json-encoded before shipping. This will allow a configured pipeline rule to parse the json and extract the key-value pairs into searchable fields. Example pipeline rule:

    rule "parse gelf json input"
    when
      contains(to_string($message.application), "MyKickassApp")
    then
      let json_fields = parse_json(to_string($message.message));
      let json_map = to_map(json_fields);
      set_fields(json_map);
    end

This will allow you to search by appname and e.g. severity level, function name, as well as any exception info (if called from logger.exception()).

## Limitations

* Graylogging requires python3.6+
* GraylogHandler and GraylogFormatter are co-dependent. Don't try to use either without the other.
