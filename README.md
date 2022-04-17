# Scrycall
A command line tool for the [Scryfall](https://scryfall.com) API.

## Dependencies

- Python 3.9
- [Poetry](https://python-poetry.org/docs/)

<img src="https://i.imgur.com/k2M2bhR.gif">

## What does Scrycall do?
Scrycall makes it easy to search for MTG cards from the command line. It prints the card information of your choice to the terminal, allowing for easy integration with other tools. Scrycall uses https://scryfall.com/ to query for cards which are returned as JSON objects. You can parse the JSON using special attribute parameters (see below) to print any information you want about the cards you query.

Scrycall stores the query data in a local cache at `~/.cache/scrycall/` to adhere to HTTP caching best practices. The data is considered stale after 24 hours and Scrycall will automatically query the API again for a refresh if you try to use stale data. You can manage your cache using command line arguments (see below).


## How do I install Scrycall?
Download the project: `git clone https://github.com/0xdanelia/scrycall`

Compile to a binary: `pyinstaller scry.spec --clean`.

You can run the python source script using the command `poetry run scry` or `python3 scrycall_app.py`.

## How do I use Scrycall?

First familiarize yourself with the Scryfall search syntax at https://scryfall.com/docs/syntax

Then run Scrycall using your plain text search query as the arguments. If needed, surround your query in single quotes (i.e. when using `!` as it's a special bash character)
```
> scry query venser t:creature
Venser, Shaper Savant
Venser's Sliver
```
```
> scry query o:"counter target noncreature spell unless"
Concerted Defense
Disciple of the Ring
Izzet Charm
Spell Pierce
Stubborn Denial
```

You can also pipe the output into another program. For example, use Scrycall to get the url of a card image, then pipe into wget to download and save the image.
```
> scry query "time walk" set:alpha --format="%{image_uris.large}" | cut -d'?' -f1 | xargs -n 1 -I {} curl {} > "time_walk.jpg"
```

## Formatting
You can use the argument `--format` to print different information about the cards that the query returns. Within the format string  `%` is a special character used to indicate certain parameters based on the JSON card objects. Be sure to surround your format string in quotes "" if it contains any whitespace. The shortcut attribute parameters are:
```
%n    name
%m    mana_cost
%c    cmc  (converted mana cost)
%y    type_line
%p    power
%t    toughness
%l    loyalty
%o    oracle_text
%f    flavor_text
%%    this will print a literal % instead of interpreting a special character
%|    this will separate output into nicely spaced columns
```
```
> scry query counterspell --format="%n  %m  [%o]"
Counterspell  {U}{U}  [Counter target spell.]
```

You can also parse the raw JSON attribute-value pairs by putting the attribute names inside `%{}` and using `.` to separate multiple attributes.
```
> scry query "lightning bolt" --format="%{legalities.modern}"
legal
```

To print all available attributes, use `?` or `?-`.
```
> scry query '!"black lotus"' --format "%{prices.?}"
usd       
usd_foil  
usd_etched
eur
eur_foil
tix
```
```
> scry query '!"black lotus"' --format "%{prices.?-}"
usd,usd_foil,usd_etched,eur,eur_foil,tix
```

To iterate every value of an attribute, use `*` or `*-`.
```
> scry query '!"serra angel"' --format="%{keywords.*}"
Flying
Vigilance
```
```
> scry query '!"serra angel"' --format="%{keywords.*-}"
Flying,Vigilance
```

Some attribute values are Scryfall URIs. Use `/` to resolve them.
```
> scry query "mox lotus" --format "%{set_uri./.name} was released %{set_uri./.released_at}"
Unhinged was released 2004-11-19
```

### Cache commands

Run `scry cache --help` for more information.

## Testing

To run the unittests: `python3 -m unittest -b`

To run `mypy` static analysis: `mypy scrycall`

