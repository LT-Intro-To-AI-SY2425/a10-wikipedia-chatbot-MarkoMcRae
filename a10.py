import re, string
import requests
import wikipedia
from typing import List, Callable, Tuple, Any, Match as TypingMatch  # Removed duplicate import
# Removed unused imports from nltk
# Removed unused import from nltk.tree
# Removed unused import from nltk.tree
from typing import Optional

def match(pattern: List[str], source: List[str]) -> Optional[List[str]]:
    """Matches a pattern with a source list of words.

    Args:
        pattern - a list of words with '%' as a wildcard
        source - a list of words to match against the pattern

    Returns:
        A list of matched words if the pattern matches, otherwise None
    """
    if len(pattern) != len(source):
        return None

    matches = []
    for p, s in zip(pattern, source):
        if p == "%":
            matches.append(s)
        elif p != s:
            return None

    return matches
from typing import List, Callable, Tuple, Any, Match as TypingMatch


def get_page_html(title: str) -> str:
    results = wikipedia.search(title)
    if not results:
        raise LookupError(f"No results found for title: {title}")
    
    print("Search results:", results)  # <-- TEMPORARY DEBUGGING LINE
    
    try:
        page = wikipedia.page(results[0])
        page_url = page.url
    except wikipedia.exceptions.DisambiguationError as e:
        raise LookupError(f"Disambiguation error: {e}")
    except wikipedia.exceptions.PageError as e:
        raise LookupError(f"Page error: {e}")
    except IndexError:
        raise LookupError("No valid page found for the given title")
    response = requests.get(page_url)  # Enable SSL verification for security
    
    if response.status_code != 200:
        raise LookupError(f"Failed to fetch page HTML: {response.status_code}")
    
    return response.text

def get_first_infobox_text(html: str) -> str:
    """Gets first infobox html from a Wikipedia page (summary box)

    Args:
        html - the full html of the page

    Returns:
        html of just the first infobox
    """
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all(class_="infobox")

    if not results:
        raise LookupError("Page has no infobox")
    return results[0].text


def clean_text(text: str) -> str:
    """Cleans given text removing non-ASCII characters and duplicate spaces & newlines

    Args:
        text - text to clean

    Returns:
        cleaned text
    """
    only_ascii = "".join([char if char in string.printable else " " for char in text])
    no_dup_spaces = re.sub(" +", " ", only_ascii)
    no_dup_newlines = re.sub("\n+", "\n", no_dup_spaces)
    return no_dup_newlines


def get_match(
    text: str,
    pattern: str,
    error_text: str = "Page doesn't appear to have the property you're expecting",
) -> TypingMatch:
    """Finds regex matches for a pattern

    Args:
        text - text to search within
        pattern - pattern to attempt to find within text
        error_text - text to display if pattern fails to match

    Returns:
        text that matches
    """
    p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
    match = p.search(text)

    if not match:
        raise AttributeError(error_text)
    return match


def get_polar_radius(planet_name: str) -> str:
    """Gets the radius of the given planet

    Args:
        planet_name - name of the planet to get radius of

    Returns:
        radius of the given planet
    """
    try:
        infobox_text = clean_text(get_first_infobox_text(get_page_html(planet_name)))
        pattern = r"(?:Polar radius.*?)(?: ?[\d]+ )?(?P<radius>[\d,.]+)(?:.*?)km"
        error_text = "Page infobox has no polar radius information"
        match = get_match(infobox_text, pattern, error_text)
        return match.group("radius")
    except LookupError as e:
        return f"Error: {e}"


def get_birth_date(name: str) -> str:
    """Gets birth date of the given person

    Args:
        name - name of the person

    Returns:
        birth date of the given person
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(name)))
    pattern = r"(?:Born\D*)(?P<birth>\d{4}-\d{2}-\d{2})"
    error_text = (
        "Page infobox has no birth information (at least none in xxxx-xx-xx format)"
    )
    match = get_match(infobox_text, pattern, error_text)

    return match.group("birth")


def get_population_size(country: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country)))
    pattern = r"(?:Population.*?)(?P<pop>\d{1,3}(?:,\d{3})+)"
    error_text = (
        "Page infobox has no information for population size"
    )
    match = get_match(infobox_text, pattern, error_text)

    return match.group("pop")


def get_capital(capital_name: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(capital_name)))
    pattern = r"(?:capital[^\w]*[:|]?[^\w]*)(?P<capital>[A-Za-z\s]+)"
    error_text = (
        "Page infobox has no information for the capital"
    )
    
    match = get_match(infobox_text, pattern, error_text)
    
    capital = match.group("capital") 

    if "and largest city" in capital:
        capital = capital.replace("and largest city", "").strip()

    return capital


def get_coordinates(place: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(place)))
    pattern = r"Coordinates(?P<coord>[\dNEWS\.\/\s\-;]+)"
    error_text = (
        "No coordinate information found in correct format"
    )
    match = get_match(infobox_text, pattern, error_text)

    return match.group("coord")



# below are a set of actions. Each takes a list argument and returns a list of answers
# according to the action and the argument. It is important that each function returns a
# list of the answer(s) and not just the answer itself.


def birth_date(matches: List[str]) -> List[str]:
    print(f"[DEBUG] birth_date matches: {matches}")
    return [get_birth_date(" ".join(matches))]


def polar_radius(matches: List[str]) -> List[str]:
    """Returns polar radius of planet in matches

    Args:
        matches - match from pattern of planet to find polar radius of

    Returns:
        polar radius of planet
    """
    return [get_polar_radius(matches[0])]


def population_size(matches: List[str]) -> List[str]:
    return [get_population_size(matches[0])]

def capital(matches: List[str]) -> List[str]:
    return [get_capital(matches[0])]

def coordinates(matches: List[str]) -> List[str]:
    return [get_coordinates(matches[0])]

def bye_action(_: List[str]) -> None:
    """Exits the program gracefully."""
    raise KeyboardInterrupt
# Removed redundant definition of bye_action


# type aliases to make pa_list type more readable, could also have written:
# pa_list: List[Tuple[List[str], Callable[[List[str]], List[Any]]]] = [...]
Pattern = List[str]
Action = Callable[[List[str]], List[Any]]

# The pattern-action list for the natural language query system. It must be declared
# here, after all of the funcztion definitions
pa_list: List[Tuple[Pattern, Action]] = [
    ("when was % born".split(), birth_date),
    ("what is the polar radius of %".split(), polar_radius),
    ("what is the population of %".split(), population_size),
    ("what is the capital of %".split(), capital),
    ("what are the coordinates of % ".split(), coordinates),
    (["bye"], bye_action),
]


def search_pa_list(src: List[str]) -> List[str]:
    """Takes source, finds matching pattern and calls corresponding action. If it finds
    a match but has no answers it returns ["No answers"]. If it finds no match it
    returns ["I don't understand"].

    Args:
        source - a phrase represented as a list of words (strings)

    Returns:
        a list of answers. Will be ["I don't understand"] if it finds no matches and
        ["No answers"] if it finds a match but no answers
    """
    for pat, act in pa_list:
        mat = match(pat, src)
        if mat is not None:
            answer = act(mat)
            return answer if answer else ["No answers"]

    return ["I don't understand"]


def query_loop() -> None:
    """The simple query loop. The try/except structure is to catch Ctrl-C or Ctrl-D
    characters and exit gracefully"""
    print("Welcome to the wikipedia database!\n")
    while True:
        try:
            print()
            query = input("Your query? ").replace("?", "").strip()
            query_words = query.lower().split()
            answers = search_pa_list(query_words)
            for ans in answers:
                print(ans)

        except (KeyboardInterrupt, EOFError):
            break

    print("\nSo long!\n")


# uncomment the next line once you've implemented everything are ready to try it out
query_loop()