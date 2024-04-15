# -*- coding: utf-8 -*-

"""Pretty-print tabular data."""


import sys

import math

from .my_itertools import zip

from .my_itertools import zip_longest as izip_longest

######################__future__.py###########################

# The CO_xxx symbols are defined here under the same names defined in
# code.h and used by compile.h, so that an editor search will find them here.
# However, they're not exported in __all__, because they don't really belong to
# this module.
CO_NESTED = 0x0010                      # nested_scopes
CO_GENERATOR_ALLOWED = 0                # generators (obsolete, was 0x1000)
CO_FUTURE_DIVISION = 0x20000            # division
CO_FUTURE_ABSOLUTE_IMPORT = 0x40000     # perform absolute imports by default
CO_FUTURE_WITH_STATEMENT = 0x80000      # with statement
CO_FUTURE_PRINT_FUNCTION = 0x100000     # print function
CO_FUTURE_UNICODE_LITERALS = 0x200000   # unicode string literals
CO_FUTURE_BARRY_AS_BDFL = 0x400000
CO_FUTURE_GENERATOR_STOP = 0x800000     # StopIteration becomes RuntimeError in generators
CO_FUTURE_ANNOTATIONS = 0x1000000       # annotations become strings at runtime


class _Feature:

    def __init__(self, optionalRelease, mandatoryRelease, compiler_flag):
        self.optional = optionalRelease
        self.mandatory = mandatoryRelease
        self.compiler_flag = compiler_flag

    def getOptionalRelease(self):
        """Return first release in which this feature was recognized.

        This is a 5-tuple, of the same form as sys.version_info.
        """
        return self.optional

    def getMandatoryRelease(self):
        """Return release in which this feature will become mandatory.

        This is a 5-tuple, of the same form as sys.version_info, or, if
        the feature was dropped, or the release date is undetermined, is None.
        """
        return self.mandatory

    def __repr__(self):
        return "_Feature" + repr((self.optional,
                                  self.mandatory,
                                  self.compiler_flag))


nested_scopes = _Feature((2, 1, 0, "beta",  1),
                         (2, 2, 0, "alpha", 0),
                         CO_NESTED)

generators = _Feature((2, 2, 0, "alpha", 1),
                      (2, 3, 0, "final", 0),
                      CO_GENERATOR_ALLOWED)

division = _Feature((2, 2, 0, "alpha", 2),
                    (3, 0, 0, "alpha", 0),
                    CO_FUTURE_DIVISION)

absolute_import = _Feature((2, 5, 0, "alpha", 1),
                           (3, 0, 0, "alpha", 0),
                           CO_FUTURE_ABSOLUTE_IMPORT)

with_statement = _Feature((2, 5, 0, "alpha", 1),
                          (2, 6, 0, "alpha", 0),
                          CO_FUTURE_WITH_STATEMENT)

print_function = _Feature((2, 6, 0, "alpha", 2),
                          (3, 0, 0, "alpha", 0),
                          CO_FUTURE_PRINT_FUNCTION)

unicode_literals = _Feature((2, 6, 0, "alpha", 2),
                            (3, 0, 0, "alpha", 0),
                            CO_FUTURE_UNICODE_LITERALS)

barry_as_FLUFL = _Feature((3, 1, 0, "alpha", 2),
                          (4, 0, 0, "alpha", 0),
                          CO_FUTURE_BARRY_AS_BDFL)

generator_stop = _Feature((3, 5, 0, "beta", 1),
                          (3, 7, 0, "alpha", 0),
                          CO_FUTURE_GENERATOR_STOP)

annotations = _Feature((3, 7, 0, "beta", 1),
                       None,
                       CO_FUTURE_ANNOTATIONS)

#################################################



# ######## reduce , partial ########
# def reduce(function, sequence, initial=None):
#     """
#     reduce(function, iterable[, initial]) -> value

#     Apply a function of two arguments cumulatively to the items of a sequence
#     or iterable, from left to right, so as to reduce the iterable to a single
#     value.  For example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5]) calculates
#     ((((1+2)+3)+4)+5).  If initial is present, it is placed before the items
#     of the iterable in the calculation, and serves as a default when the
#     iterable is empty.
#     """
#     initial = initial or object()
#     it = iter(sequence)

#     if initial is object():
#         try:
#             value = next(it)
#         except StopIteration:
#             raise TypeError("reduce() of empty iterable with no initial value") 
#     else:
#         value = initial

#     for element in it:
#         value = function(value, element)

#     return value

# class partial:
#     def __init__(self, func, *args, **keywords):
#         self.func = func
#         self.args = args
#         self.keywords = keywords

#     def __call__(self, *args, **keywords):
#         # Combine new args and keywords with those provided at initialization
#         new_args = self.args + args
#         new_keywords = self.keywords.copy()
#         new_keywords.update(keywords)
#         return self.func(*new_args, **new_keywords)
    
# ###################################

from functools import partial
from functools import reduce

_none_type = type(None)
_bool_type = bool
_int_type = int
_long_type = int
_float_type = float
_text_type = str
_binary_type = bytes
basestring = str


try:
    import wcwidth  # optional wide-character (CJK) support
except ImportError:
    wcwidth = None


######## escape ########
def htmlescape(s, quote=True):
    """
    Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true (the default), the quotation mark
    characters, both double quote (") and single quote (') characters are also
    translated.
    """
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
        s = s.replace('\'', "&#x27;")
    return s
###################################

__all__ = ["tabulate", "tabulate_formats", "simple_separated_format"]
__version__ = "0.8.10"


# minimum extra space in headers
MIN_PADDING = 2

# Whether or not to preserve leading/trailing whitespace in data.
PRESERVE_WHITESPACE = False

_DEFAULT_FLOATFMT = "g"
_DEFAULT_MISSINGVAL = ""
# default align will be overwritten by "left", "center" or "decimal"
# depending on the formatter
_DEFAULT_ALIGN = "default"


# if True, enable wide-character (CJK) support
WIDE_CHARS_MODE = wcwidth is not None



class Line:
    __slots__ = ['begin', 'hline', 'sep', 'end']

    def __init__(self, begin, hline, sep, end):
        self.begin = begin
        self.hline = hline
        self.sep = sep
        self.end = end

    def __repr__(self):
        return f"Line(begin={self.begin!r}, hline={self.hline!r}, sep={self.sep!r}, end={self.end!r})"

    def __iter__(self):
        for attr_name in self.__slots__:
            yield getattr(self, attr_name)


class DataRow:
    __slots__ = ['begin', 'sep', 'end']

    def __init__(self, begin, sep, end):
        self.begin = begin
        self.sep = sep
        self.end = end

    def __repr__(self):
        return f"DataRow(begin={self.begin!r}, sep={self.sep!r}, end={self.end!r})"

    def __iter__(self):
        for attr_name in self.__slots__:
            yield getattr(self, attr_name)



# A table structure is suppposed to be:
#
#     --- lineabove ---------
#         headerrow
#     --- linebelowheader ---
#         datarow
#     --- linebetweenrows ---
#     ... (more datarows) ...
#     --- linebetweenrows ---
#         last datarow
#     --- linebelow ---------
#
# TableFormat's line* elements can be
#
#   - either None, if the element is not used,
#   - or a Line tuple,
#   - or a function: [col_widths], [col_alignments] -> string.
#
# TableFormat's *row elements can be
#
#   - either None, if the element is not used,
#   - or a DataRow tuple,
#   - or a function: [cell_values], [col_widths], [col_alignments] -> string.
#
# padding (an integer) is the amount of white space around data values.
#
# with_header_hide:
#
#   - either None, to display all table elements unconditionally,
#   - or a list of elements not to be displayed if the table has column headers.
#
class TableFormat:
    __slots__ = [
        'lineabove',
        'linebelowheader',
        'linebetweenrows',
        'linebelow',
        'headerrow',
        'datarow',
        'padding',
        'with_header_hide',
    ]

    def __init__(self, lineabove=None, linebelowheader=None, linebetweenrows=None, linebelow=None, headerrow=None, datarow=None, padding=None, with_header_hide=None):
        self.lineabove = lineabove
        self.linebelowheader = linebelowheader
        self.linebetweenrows = linebetweenrows
        self.linebelow = linebelow
        self.headerrow = headerrow
        self.datarow = datarow
        self.padding = padding
        self.with_header_hide = with_header_hide

    def __repr__(self):
        return f"TableFormat(lineabove={self.lineabove!r}, linebelowheader={self.linebelowheader!r}, linebetweenrows={self.linebetweenrows!r}, linebelow={self.linebelow!r}, headerrow={self.headerrow!r}, datarow={self.datarow!r}, padding={self.padding!r}, with_header_hide={self.with_header_hide!r})"


def _pipe_segment_with_colons(align, colwidth):
    """Return a segment of a horizontal line with optional colons which
    indicate column's alignment (as in `pipe` output format)."""
    w = colwidth
    if align in ["right", "decimal"]:
        return ("-" * (w - 1)) + ":"
    elif align == "center":
        return ":" + ("-" * (w - 2)) + ":"
    elif align == "left":
        return ":" + ("-" * (w - 1))
    else:
        return "-" * w


def _pipe_line_with_colons(colwidths, colaligns):
    """Return a horizontal line with optional colons to indicate column's
    alignment (as in `pipe` output format)."""
    if not colaligns:  # e.g. printing an empty data frame (github issue #15)
        colaligns = [""] * len(colwidths)
    segments = [_pipe_segment_with_colons(a, w) for a, w in zip(colaligns, colwidths)]
    return "|" + "|".join(segments) + "|"


def _mediawiki_row_with_attrs(separator, cell_values, colwidths, colaligns):
    alignment = {
        "left": "",
        "right": 'align="right"| ',
        "center": 'align="center"| ',
        "decimal": 'align="right"| ',
    }
    # hard-coded padding _around_ align attribute and value together
    # rather than padding parameter which affects only the value
    values_with_attrs = [
        " " + alignment.get(a, "") + c + " " for c, a in zip(cell_values, colaligns)
    ]
    colsep = separator * 2
    return (separator + colsep.join(values_with_attrs)).rstrip()


def _textile_row_with_attrs(cell_values, colwidths, colaligns):
    cell_values[0] += " "
    alignment = {"left": "<.", "right": ">.", "center": "=.", "decimal": ">."}
    values = tuple([alignment.get(a, "") + v for a, v in zip(colaligns, cell_values)])
    return "|" + "|".join(values) + "|"


def _html_begin_table_without_header(colwidths_ignore, colaligns_ignore):
    # this table header will be suppressed if there is a header row
    return "<table>\n<tbody>"


def _html_row_with_attrs(celltag, unsafe, cell_values, colwidths, colaligns):
    alignment = {
        "left": "",
        "right": ' style="text-align: right;"',
        "center": ' style="text-align: center;"',
        "decimal": ' style="text-align: right;"',
    }
    if unsafe:
        values_with_attrs = [
            "<{0}{1}>{2}</{0}>".format(celltag, alignment.get(a, ""), c)
            for c, a in zip(cell_values, colaligns)
        ]
    else:
        values_with_attrs = [
            "<{0}{1}>{2}</{0}>".format(celltag, alignment.get(a, ""), htmlescape(c))
            for c, a in zip(cell_values, colaligns)
        ]
    rowhtml = "<tr>{}</tr>".format("".join(values_with_attrs).rstrip())
    if celltag == "th":  # it's a header row, create a new table header
        rowhtml = "<table>\n<thead>\n{}\n</thead>\n<tbody>".format(rowhtml)
    return rowhtml


def _moin_row_with_attrs(celltag, cell_values, colwidths, colaligns, header=""):
    alignment = {
        "left": "",
        "right": '<style="text-align: right;">',
        "center": '<style="text-align: center;">',
        "decimal": '<style="text-align: right;">',
    }
    values_with_attrs = [
        "{0}{1} {2} ".format(celltag, alignment.get(a, ""), header + c + header)
        for c, a in zip(cell_values, colaligns)
    ]
    return "".join(values_with_attrs) + "||"


def _latex_line_begin_tabular(colwidths, colaligns, booktabs=False, longtable=False):
    alignment = {"left": "l", "right": "r", "center": "c", "decimal": "r"}
    tabular_columns_fmt = "".join([alignment.get(a, "l") for a in colaligns])
    return "\n".join(
        [
            ("\\begin{tabular}{" if not longtable else "\\begin{longtable}{") + tabular_columns_fmt + "}",
            "\\toprule" if booktabs else "\\hline",
        ]
    )


LATEX_ESCAPE_RULES = {
    r"&": r"\&",
    r"%": r"\%",
    r"$": r"\$",
    r"#": r"\#",
    r"_": r"\_",
    r"^": r"\^{}",
    r"{": r"\{",
    r"}": r"\}",
    r"~": r"\textasciitilde{}",
    "\\": r"\textbackslash{}",
    r"<": r"\ensuremath{<}",
    r">": r"\ensuremath{>}",
}


def _latex_row(cell_values, colwidths, colaligns, escrules=None):
    escrules = escrules or LATEX_ESCAPE_RULES
    def escape_char(c):
        return escrules.get(c, c)

    escaped_values = ["".join(map(escape_char, cell)) for cell in cell_values]
    rowfmt = DataRow("", "&", "\\\\")
    return _build_simple_row(escaped_values, rowfmt)


def _rst_escape_first_column(rows, headers):
    def escape_empty(val):
        if isinstance(val, (_text_type, _binary_type)) and not val.strip():
            return ".."
        else:
            return val

    new_headers = list(headers)
    new_rows = []
    if headers:
        new_headers[0] = escape_empty(headers[0])
    for row in rows:
        new_row = list(row)
        if new_row:
            new_row[0] = escape_empty(row[0])
        new_rows.append(new_row)
    return new_rows, new_headers


_table_formats = {
    "simple": TableFormat(
        lineabove=Line("", "-", "  ", ""),
        linebelowheader=Line("", "-", "  ", ""),
        linebetweenrows=None,
        linebelow=Line("", "-", "  ", ""),
        headerrow=DataRow("", "  ", ""),
        datarow=DataRow("", "  ", ""),
        padding=0,
        with_header_hide=["lineabove", "linebelow"],
    ),
    "plain": TableFormat(
        lineabove=None,
        linebelowheader=None,
        linebetweenrows=None,
        linebelow=None,
        headerrow=DataRow("", "  ", ""),
        datarow=DataRow("", "  ", ""),
        padding=0,
        with_header_hide=None,
    ),
    "grid": TableFormat(
        lineabove=Line("+", "-", "+", "+"),
        linebelowheader=Line("+", "=", "+", "+"),
        linebetweenrows=Line("+", "-", "+", "+"),
        linebelow=Line("+", "-", "+", "+"),
        headerrow=DataRow("|", "|", "|"),
        datarow=DataRow("|", "|", "|"),
        padding=1,
        with_header_hide=None,
    ),
    "fancy_grid": TableFormat(
        lineabove=Line("╒", "═", "╤", "╕"),
        linebelowheader=Line("╞", "═", "╪", "╡"),
        linebetweenrows=Line("├", "─", "┼", "┤"),
        linebelow=Line("╘", "═", "╧", "╛"),
        headerrow=DataRow("│", "│", "│"),
        datarow=DataRow("│", "│", "│"),
        padding=1,
        with_header_hide=None,
    ),
    "fancy_outline": TableFormat(
        lineabove=Line("╒", "═", "╤", "╕"),
        linebelowheader=Line("╞", "═", "╪", "╡"),
        linebetweenrows=None,
        linebelow=Line("╘", "═", "╧", "╛"),
        headerrow=DataRow("│", "│", "│"),
        datarow=DataRow("│", "│", "│"),
        padding=1,
        with_header_hide=None,
    ),
    "github": TableFormat(
        lineabove=Line("|", "-", "|", "|"),
        linebelowheader=Line("|", "-", "|", "|"),
        linebetweenrows=None,
        linebelow=None,
        headerrow=DataRow("|", "|", "|"),
        datarow=DataRow("|", "|", "|"),
        padding=1,
        with_header_hide=["lineabove"],
    ),
    "pipe": TableFormat(
        lineabove=_pipe_line_with_colons,
        linebelowheader=_pipe_line_with_colons,
        linebetweenrows=None,
        linebelow=None,
        headerrow=DataRow("|", "|", "|"),
        datarow=DataRow("|", "|", "|"),
        padding=1,
        with_header_hide=["lineabove"],
    ),
    "orgtbl": TableFormat(
        lineabove=None,
        linebelowheader=Line("|", "-", "+", "|"),
        linebetweenrows=None,
        linebelow=None,
        headerrow=DataRow("|", "|", "|"),
        datarow=DataRow("|", "|", "|"),
        padding=1,
        with_header_hide=None,
    ),
    "jira": TableFormat(
        lineabove=None,
        linebelowheader=None,
        linebetweenrows=None,
        linebelow=None,
        headerrow=DataRow("||", "||", "||"),
        datarow=DataRow("|", "|", "|"),
        padding=1,
        with_header_hide=None,
    ),
    "presto": TableFormat(
        lineabove=None,
        linebelowheader=Line("", "-", "+", ""),
        linebetweenrows=None,
        linebelow=None,
        headerrow=DataRow("", "|", ""),
        datarow=DataRow("", "|", ""),
        padding=1,
        with_header_hide=None,
    ),
    "pretty": TableFormat(
        lineabove=Line("+", "-", "+", "+"),
        linebelowheader=Line("+", "-", "+", "+"),
        linebetweenrows=None,
        linebelow=Line("+", "-", "+", "+"),
        headerrow=DataRow("|", "|", "|"),
        datarow=DataRow("|", "|", "|"),
        padding=1,
        with_header_hide=None,
    ),
    "psql": TableFormat(
        lineabove=Line("+", "-", "+", "+"),
        linebelowheader=Line("|", "-", "+", "|"),
        linebetweenrows=None,
        linebelow=Line("+", "-", "+", "+"),
        headerrow=DataRow("|", "|", "|"),
        datarow=DataRow("|", "|", "|"),
        padding=1,
        with_header_hide=None,
    ),
    "rst": TableFormat(
        lineabove=Line("", "=", "  ", ""),
        linebelowheader=Line("", "=", "  ", ""),
        linebetweenrows=None,
        linebelow=Line("", "=", "  ", ""),
        headerrow=DataRow("", "  ", ""),
        datarow=DataRow("", "  ", ""),
        padding=0,
        with_header_hide=None,
    ),
    "mediawiki": TableFormat(
        lineabove=Line(
            '{| class="wikitable" style="text-align: left;"',
            "",
            "",
            "\n|+ <!-- caption -->\n|-",
        ),
        linebelowheader=Line("|-", "", "", ""),
        linebetweenrows=Line("|-", "", "", ""),
        linebelow=Line("|}", "", "", ""),
        headerrow=partial(_mediawiki_row_with_attrs, "!"),
        datarow=partial(_mediawiki_row_with_attrs, "|"),
        padding=0,
        with_header_hide=None,
    ),
    "moinmoin": TableFormat(
        lineabove=None,
        linebelowheader=None,
        linebetweenrows=None,
        linebelow=None,
        headerrow=partial(_moin_row_with_attrs, "||", header="'''"),
        datarow=partial(_moin_row_with_attrs, "||"),
        padding=1,
        with_header_hide=None,
    ),
    "youtrack": TableFormat(
        lineabove=None,
        linebelowheader=None,
        linebetweenrows=None,
        linebelow=None,
        headerrow=DataRow("|| ", " || ", " || "),
        datarow=DataRow("| ", " | ", " |"),
        padding=1,
        with_header_hide=None,
    ),
    "html": TableFormat(
        lineabove=_html_begin_table_without_header,
        linebelowheader="",
        linebetweenrows=None,
        linebelow=Line("</tbody>\n</table>", "", "", ""),
        headerrow=partial(_html_row_with_attrs, "th", False),
        datarow=partial(_html_row_with_attrs, "td", False),
        padding=0,
        with_header_hide=["lineabove"],
    ),
    "unsafehtml": TableFormat(
        lineabove=_html_begin_table_without_header,
        linebelowheader="",
        linebetweenrows=None,
        linebelow=Line("</tbody>\n</table>", "", "", ""),
        headerrow=partial(_html_row_with_attrs, "th", True),
        datarow=partial(_html_row_with_attrs, "td", True),
        padding=0,
        with_header_hide=["lineabove"],
    ),
    "latex": TableFormat(
        lineabove=_latex_line_begin_tabular,
        linebelowheader=Line("\\hline", "", "", ""),
        linebetweenrows=None,
        linebelow=Line("\\hline\n\\end{tabular}", "", "", ""),
        headerrow=_latex_row,
        datarow=_latex_row,
        padding=1,
        with_header_hide=None,
    ),
    "latex_raw": TableFormat(
        lineabove=_latex_line_begin_tabular,
        linebelowheader=Line("\\hline", "", "", ""),
        linebetweenrows=None,
        linebelow=Line("\\hline\n\\end{tabular}", "", "", ""),
        headerrow=partial(_latex_row, escrules={}),
        datarow=partial(_latex_row, escrules={}),
        padding=1,
        with_header_hide=None,
    ),
    "latex_booktabs": TableFormat(
        lineabove=partial(_latex_line_begin_tabular, booktabs=True),
        linebelowheader=Line("\\midrule", "", "", ""),
        linebetweenrows=None,
        linebelow=Line("\\bottomrule\n\\end{tabular}", "", "", ""),
        headerrow=_latex_row,
        datarow=_latex_row,
        padding=1,
        with_header_hide=None,
    ),
    "latex_longtable": TableFormat(
        lineabove=partial(_latex_line_begin_tabular, longtable=True),
        linebelowheader=Line("\\hline\n\\endhead", "", "", ""),
        linebetweenrows=None,
        linebelow=Line("\\hline\n\\end{longtable}", "", "", ""),
        headerrow=_latex_row,
        datarow=_latex_row,
        padding=1,
        with_header_hide=None,
    ),
    "tsv": TableFormat(
        lineabove=None,
        linebelowheader=None,
        linebetweenrows=None,
        linebelow=None,
        headerrow=DataRow("", "\t", ""),
        datarow=DataRow("", "\t", ""),
        padding=0,
        with_header_hide=None,
    ),
    "textile": TableFormat(
        lineabove=None,
        linebelowheader=None,
        linebetweenrows=None,
        linebelow=None,
        headerrow=DataRow("|_. ", "|_.", "|"),
        datarow=_textile_row_with_attrs,
        padding=1,
        with_header_hide=None,
    ),
}


tabulate_formats = list(sorted(_table_formats.keys()))

# The table formats for which multiline cells will be folded into subsequent
# table rows. The key is the original format specified at the API. The value is
# the format that will be used to represent the original format.
multiline_formats = {
    "plain": "plain",
    "simple": "simple",
    "grid": "grid",
    "fancy_grid": "fancy_grid",
    "pipe": "pipe",
    "orgtbl": "orgtbl",
    "jira": "jira",
    "presto": "presto",
    "pretty": "pretty",
    "psql": "psql",
    "rst": "rst",
}

# TODO: Add multiline support for the remaining table formats:
#       - mediawiki: Replace \n with <br>
#       - moinmoin: TBD
#       - youtrack: TBD
#       - html: Replace \n with <br>
#       - latex*: Use "makecell" package: In header, replace X\nY with
#         \thead{X\\Y} and in data row, replace X\nY with \makecell{X\\Y}
#       - tsv: TBD
#       - textile: Replace \n with <br/> (must be well-formed XML)






def simple_separated_format(separator):
    """Construct a simple TableFormat with columns separated by a separator.

    >>> tsv = simple_separated_format("\\t") ; 
        tabulate([["foo", 1], ["spam", 23]], tablefmt=tsv) == 'foo \\t 1\\nspam\\t23'
    True

    """
    return TableFormat(
        None,
        None,
        None,
        None,
        headerrow=DataRow("", separator, ""),
        datarow=DataRow("", separator, ""),
        padding=0,
        with_header_hide=None,
    )


def _isnumber_with_thousands_separator(string):
    """
    >>> _isnumber_with_thousands_separator(".")
    False
    >>> _isnumber_with_thousands_separator("1")
    True
    >>> _isnumber_with_thousands_separator("1.")
    True
    >>> _isnumber_with_thousands_separator(".1")
    True
    >>> _isnumber_with_thousands_separator("1000")
    False
    >>> _isnumber_with_thousands_separator("1,000")
    True
    >>> _isnumber_with_thousands_separator("1,0000")
    False
    >>> _isnumber_with_thousands_separator("1,000.1234")
    True
    >>> _isnumber_with_thousands_separator(b"1,000.1234")
    True
    >>> _isnumber_with_thousands_separator("+1,000.1234")
    True
    >>> _isnumber_with_thousands_separator("-1,000.1234")
    True
    """
    try:
        string = string.decode()
    except (UnicodeDecodeError, AttributeError):
        pass

    # 如果输入是字节串，将其转换为字符串
    if isinstance(string, bytes):
        string = string.decode()
    
    # 检查开头符号
    if string.startswith(('+', '-')):
        string = string[1:]
    
    # 拆分整数部分和小数部分
    parts = string.split('.')
    if len(parts) > 2:
        return False  # 出现多于一个的小数点
    
    # 拆分整数部分的千位分隔符
    integer_part = parts[0]
    if ',' in integer_part:
        integer_groups = integer_part.split(',')
        # 检查最后一组外的所有组是否为三位数字
        for group in integer_groups[:-1]:
            if len(group) != 3:
                return False
        # 检查最后一组是否为1到3位数字
        if not 1 <= len(integer_groups[-1]) <= 3:
            return False
    elif integer_part and not integer_part.isdigit():
        # 如果整数部分不包含千位分隔符但包含非数字字符
        return False
    
    # 检查小数部分，如果存在，是否全部为数字
    if len(parts) == 2 and not parts[1].isdigit():
        return False
    
    return True


def _isconvertible(conv, string):
    try:
        conv(string)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def _isnumber(string):
    """
    >>> _isnumber("123.45")
    True
    >>> _isnumber("123")
    True
    >>> _isnumber("spam")
    False
    >>> _isnumber("123e45678")
    False
    >>> _isnumber("inf")
    True
    """
    if not _isconvertible(float, string):
        return False
    elif isinstance(string, (_text_type, _binary_type)) and (
        math.isinf(float(string)) or math.isnan(float(string))
    ):
        return string.lower() in ["inf", "-inf", "nan"]
    return True


def _isint(string, inttype=None):
    """
    >>> _isint("123")
    True
    >>> _isint("123.45")
    False
    """
    inttype = inttype or int
    return (
        type(string) is inttype or (isinstance(string, _binary_type) or isinstance(string, _text_type)) and _isconvertible(inttype, string)
    )


def _isbool(string):
    """
    >>> _isbool(True)
    True
    >>> _isbool("False")
    True
    >>> _isbool(1)
    False
    """
    return type(string) is _bool_type or (
        isinstance(string, (_binary_type, _text_type)) and string in ("True", "False")
    )


def _type(string, has_invisible=True, numparse=True):
    """The least generic type (type(None), int, float, str, unicode).

    >>> _type(None) is type(None)
    True
    >>> _type("foo") is type("")
    True
    >>> _type("1") is type(1)
    True
    >>> _type('\x1b[31m42\x1b[0m') is type(42)
    True
    >>> _type('\x1b[31m42\x1b[0m') is type(42)
    True

    """

    if has_invisible and (
        isinstance(string, _text_type) or isinstance(string, _binary_type)
    ):
        string = _strip_invisible(string)

    if string is None:
        return _none_type
    elif hasattr(string, "isoformat"):  # datetime.datetime, date, and time
        return _text_type
    elif _isbool(string):
        return _bool_type
    elif _isint(string) and numparse:
        return int
    elif _isint(string, _long_type) and numparse:
        return int
    elif _isnumber(string) and numparse:
        return float
    elif isinstance(string, _binary_type):
        return _binary_type
    else:
        return _text_type

def _my_rfind(s, sub):
    """Find the highest index of 'sub' in 's', searching from right to left.
        >>> my_rfind("hello.world.hello", ".")
        11
        >>> my_rfind("hello.world.hello", ",")
        -1
    
    """
    for i in range(len(s) - 1, -1, -1):
        if s[i:i+len(sub)] == sub:
            return i
    return -1

def _afterpoint(string):
    """Symbols after a decimal point, -1 if the string lacks the decimal point.

    >>> _afterpoint("123.45")
    2
    >>> _afterpoint("1001")
    -1
    >>> _afterpoint("eggs")
    -1
    >>> _afterpoint("123e45")
    2
    >>> _afterpoint("123,456.78")
    2

    """
    if _isnumber(string) or _isnumber_with_thousands_separator(string):
        if _isint(string):
            return -1
        else:
            pos = _my_rfind(string, ".")
            pos = _my_rfind(string.lower(), "e") if pos < 0 else pos
            if pos >= 0:
                return len(string) - pos - 1
            else:
                return -1  # no point
    else:
        return -1  # not a number


def _padleft(width, s):
    """Flush right.

    >>> _padleft(6, 'abcd') == '  abcd'
    True

    """
    padding_size = max(0, width - len(s))
    # Create the padding string of spaces of the calculated padding size.
    padding = ' ' * padding_size
    # Concatenate the padding string with the original string.
    return padding + s


def _padright(width, s):
    """Flush left.

    >>> _padright(6, 'abcd') == 'abcd  '
    True

    """
    padding_size = max(0, width - len(s))
    # Create the padding string of spaces of the calculated padding size.
    padding = ' ' * padding_size
    # Concatenate the original string with the padding string.
    return s + padding

def _padboth(width, s):
    """Center string.

    >>> _padboth(6, 'abcd') == ' abcd '
    True

    """
    fmt = "{0:^%ds}" % width
    return fmt.format(s)


def _padnone(ignore_width, s):
    return s


def _strip_invisible(s):
    r"""Remove invisible ANSI color codes.

    >>> str(_strip_invisible('\x1B]8;;https://example.com\x1B\\This is a link\x1B]8;;\x1B\\'))
    'This is a link'

    """
    return s


def _visible_width(s):
    """Visible width of a printed string. ANSI color codes are removed.

    >>> _visible_width('\x1b[31mhello\x1b[0m'), _visible_width("world")
    (5, 5)

    """
    # optional wide-character support
    if wcwidth is not None and WIDE_CHARS_MODE:
        len_fn = wcwidth.wcswidth
    else:
        len_fn = len
    if isinstance(s, _text_type) or isinstance(s, _binary_type):
        return len_fn(_strip_invisible(s))
    else:
        return len_fn(_text_type(s))


def _is_multiline(s):
    if isinstance(s, _text_type):
        return '\n' in s or '\r\n' in s
    raise NotImplementedError("没有实现")


def _multiline_width(multiline_s, line_width_fn=None):
    """Visible width of a potentially multiline content."""
    line_width_fn = line_width_fn or len
    return max(map(line_width_fn, multiline_s.splitlines()))


def _choose_width_fn(has_invisible, enable_widechars, is_multiline):
    """Return a function to calculate visible cell width."""
    if has_invisible:
        line_width_fn = _visible_width
    elif enable_widechars:  # optional wide-character support if available
        line_width_fn = wcwidth.wcswidth
    else:
        line_width_fn = len
    if is_multiline:
        width_fn = lambda s: _multiline_width(s, line_width_fn)  # noqa
    else:
        width_fn = line_width_fn
    return width_fn


def _align_column_choose_padfn(strings, alignment, has_invisible):
    if alignment == "right":
        if not PRESERVE_WHITESPACE:
            strings = [s.strip() for s in strings]
        padfn = _padleft
    elif alignment == "center":
        if not PRESERVE_WHITESPACE:
            strings = [s.strip() for s in strings]
        padfn = _padboth
    elif alignment == "decimal":
        if has_invisible:
            decimals = [_afterpoint(_strip_invisible(s)) for s in strings]
        else:
            decimals = [_afterpoint(s) for s in strings]
        maxdecimals = max(decimals)
        strings = [s + (maxdecimals - decs) * " " for s, decs in zip(strings, decimals)]
        padfn = _padleft
    elif not alignment:
        padfn = _padnone
    else:
        if not PRESERVE_WHITESPACE:
            strings = [s.strip() for s in strings]
        padfn = _padright
    return strings, padfn


def _align_column_choose_width_fn(has_invisible, enable_widechars, is_multiline):
    if has_invisible:
        line_width_fn = _visible_width
    elif enable_widechars:  # optional wide-character support if available
        line_width_fn = wcwidth.wcswidth
    else:
        line_width_fn = len
    if is_multiline:
        width_fn = lambda s: _align_column_multiline_width(s, line_width_fn)  # noqa
    else:
        width_fn = line_width_fn
    return width_fn


def _align_column_multiline_width(multiline_s, line_width_fn=None):
    """Visible width of a potentially multiline content."""
    line_width_fn = line_width_fn or len
    return list(map(line_width_fn, multiline_s.splitlines()))


def _flat_list(nested_list):
    ret = []
    for item in nested_list:
        if isinstance(item, list):
            for subitem in item:
                ret.append(subitem)
        else:
            ret.append(item)
    return ret


def _align_column(
    strings,
    alignment,
    minwidth=0,
    has_invisible=True,
    enable_widechars=False,
    is_multiline=False):
    """[string] -> [padded_string]"""
    strings, padfn = _align_column_choose_padfn(strings, alignment, has_invisible)
    width_fn = _align_column_choose_width_fn(
        has_invisible, enable_widechars, is_multiline
    )
    
    s_widths = list(map(width_fn, strings))
    maxwidth = max(max(_flat_list(s_widths)), minwidth)
    # TODO: refactor column alignment in single-line and multiline modes
    if is_multiline:
        if not enable_widechars and not has_invisible:
            padded_strings = [
                "\n".join([padfn(maxwidth, s) for s in ms.splitlines()])
                for ms in strings
            ]
        else:
            # enable wide-character width corrections
            s_lens = [[len(s) for s in ms.splitlines()] for ms in strings]
            visible_widths = [
                [maxwidth - (w - l) for w, l in zip(mw, ml)]
                for mw, ml in zip(s_widths, s_lens)
            ]
            # wcswidth and _visible_width don't count invisible characters;
            # padfn doesn't need to apply another correction
            padded_strings = [
                "\n".join([padfn(w, s) for s, w in zip((ms.splitlines() or ms), mw)])
                for ms, mw in zip(strings, visible_widths)
            ]
    else:  # single-line cell values
        if not enable_widechars and not has_invisible:
            padded_strings = [padfn(maxwidth, s) for s in strings]
        else:
            # enable wide-character width corrections
            s_lens = list(map(len, strings))
            visible_widths = [maxwidth - (w - l) for w, l in zip(s_widths, s_lens)]
            # wcswidth and _visible_width don't count invisible characters;
            # padfn doesn't need to apply another correction
            padded_strings = [padfn(w, s) for s, w in zip(strings, visible_widths)]
    return padded_strings


def _more_generic(type1, type2):
    types = {
        _none_type: 0,
        _bool_type: 1,
        int: 2,
        float: 3,
        _binary_type: 4,
        _text_type: 5,
    }
    invtypes = {
        5: _text_type,
        4: _binary_type,
        3: float,
        2: int,
        1: _bool_type,
        0: _none_type,
    }
    moregeneric = max(types.get(type1, 5), types.get(type2, 5))
    return invtypes[moregeneric]


def _column_type(strings, has_invisible=True, numparse=True):
    """The least generic type all column values are convertible to.

    >>> _column_type([True, False]) is _bool_type
    True
    >>> _column_type(["1", "2"]) is _int_type
    True
    >>> _column_type(["1", "2.3"]) is _float_type
    True
    >>> _column_type(["1", "2.3", "four"]) is _text_type
    True
    >>> _column_type(["four", 'abcd']) is _text_type
    True
    >>> _column_type([None, "brux"]) is _text_type
    True
    >>> _column_type([1, 2, None]) is _int_type
    True
    >>> import datetime as dt
    >>> _column_type([dt.datetime(1991,2,19), dt.time(17,35)]) is _text_type
    True

    """
    types = [_type(s, has_invisible, numparse) for s in strings]
    return reduce(_more_generic, types, _bool_type)


def _format(val, valtype, floatfmt, missingval="", has_invisible=True):
    """Format a value according to its type.

    """  # noqa
    if val is None:
        return missingval

    if valtype in [int, _text_type]:
        return "{0}".format(val)
    elif valtype is _binary_type:
        try:
            return _text_type(val, "ascii")
        except TypeError:
            return _text_type(val)
    elif valtype is float:
        return str(float(val))
    else:
        return "{0}".format(val)


def _align_header(
    header, alignment, width, visible_width, is_multiline=False, width_fn=None):
    "Pad string header to width chars given known visible_width of the header."
    if is_multiline:
        # 首先尝试Windows风格的换行(\r\n)
        if '\r\n' in header:
            header_lines = header.split('\r\n')
        # 如果不是Windows风格换行，则默认使用Unix/Linux风格(\n)
        else:
            header_lines = header.split('\n')
        
        padded_lines = [
            _align_header(h, alignment, width, width_fn(h)) for h in header_lines
        ]
        return "\n".join(padded_lines)
    # else: not multiline
    ninvisible = len(header) - visible_width
    width += ninvisible
    if alignment == "left":
        return _padright(width, header)
    elif alignment == "center":
        return _padboth(width, header)
    elif not alignment:
        return "{0}".format(header)
    else:
        return _padleft(width, header)


def _prepend_row_index(rows, index):
    """Add a left-most index column."""
    if index is None or index is False:
        return rows
    if len(index) != len(rows):
        print("index=", index)
        print("rows=", rows)
        raise ValueError("index must be as long as the number of data rows")
    rows = [[v] + list(row) for v, row in zip(index, rows)]
    return rows


def _bool(val):
    "A wrapper around standard bool() which doesn't throw on NumPy arrays"
    try:
        return bool(val)
    except ValueError:  # val is likely to be a numpy array with many elements
        return False


def _normalize_tabular_data(tabular_data, headers, showindex="default"):
    """Transform a supported data type to a list of lists, and a list of headers.

    Supported tabular data types:

    * list-of-lists or another iterable of iterables

    * list of named tuples (usually used with headers="keys")

    * list of dicts (usually used with headers="keys")

    * list of OrderedDicts (usually used with headers="keys")

    * 2D NumPy arrays

    * NumPy record arrays (usually used with headers="keys")

    * dict of iterables (usually used with headers="keys")

    * pandas.DataFrame (usually used with headers="keys")

    The first row can be used as headers if headers="firstrow",
    column indices can be used as headers if headers="keys".

    If showindex="default", show row indices of the pandas.DataFrame.
    If showindex="always", show row indices for all types of data.
    If showindex="never", don't show row indices for all types of data.
    If showindex is an iterable, show its values as row indices.

    """

    try:
        bool(headers)
        is_headers2bool_broken = False  # noqa
    except ValueError:  # numpy.ndarray, pandas.core.index.Index, ...
        is_headers2bool_broken = True  # noqa
        headers = list(headers)

    index = None
    if hasattr(tabular_data, "keys") and hasattr(tabular_data, "values"):
        # dict-like and pandas.DataFrame?
        if hasattr(tabular_data.values, "__call__"):
            # likely a conventional dict
            keys = tabular_data.keys()
            rows = list(
                izip_longest(*tabular_data.values())
            )  # columns have to be transposed
        elif hasattr(tabular_data, "index"):
            # values is a property, has .index => it's likely a pandas.DataFrame (pandas 0.11.0)
            keys = list(tabular_data)
            if ( showindex in ["default", "always", True] and tabular_data.index.name is not None):
                if isinstance(tabular_data.index.name, list):
                    keys[:0] = tabular_data.index.name
                else:
                    keys[:0] = [tabular_data.index.name]
            vals = tabular_data.values  # values matrix doesn't need to be transposed
            # for DataFrames add an index per default
            index = list(tabular_data.index)
            rows = [list(row) for row in vals]
        else:
            raise ValueError("tabular data doesn't appear to be a dict or a DataFrame")

        if headers == "keys":
            headers = list(map(_text_type, keys))  # headers should be strings

    else:  # it's a usual an iterable of iterables, or a NumPy array
        rows = list(tabular_data)

        if headers == "keys" and not rows:
            # an empty table (issue #81)
            headers = []
        elif ( headers == "keys" and hasattr(tabular_data, "dtype") and getattr(tabular_data.dtype, "names") ):
            # numpy record array
            headers = tabular_data.dtype.names
        elif ( headers == "keys" and len(rows) > 0 and isinstance(rows[0], tuple) and hasattr(rows[0], "_fields") ):
            # namedtuple
            headers = list(map(_text_type, rows[0]._fields))
        elif len(rows) > 0 and hasattr(rows[0], "keys") and hasattr(rows[0], "values"):
            # dict-like object
            uniq_keys = set()  # implements hashed lookup
            keys = []  # storage for set
            if headers == "firstrow":
                firstdict = rows[0] if len(rows) > 0 else {}
                keys.extend(firstdict.keys())
                uniq_keys.update(keys)
                rows = rows[1:]
            for row in rows:
                for k in row.keys():
                    # Save unique items in input order
                    if k not in uniq_keys:
                        keys.append(k)
                        uniq_keys.add(k)
            if headers == "keys":
                headers = keys
            elif isinstance(headers, dict):
                # a dict of headers for a list of dicts
                headers = [headers.get(k, k) for k in keys]
                headers = list(map(_text_type, headers))
            elif headers == "firstrow":
                if len(rows) > 0:
                    headers = [firstdict.get(k, k) for k in keys]
                    headers = list(map(_text_type, headers))
                else:
                    headers = []
            elif headers:
                raise ValueError(
                    "headers for a list of dicts is not a dict or a keyword"
                )
            rows = [[row.get(k) for k in keys] for row in rows]

        elif (headers == "keys" and hasattr(tabular_data, "description") and hasattr(tabular_data, "fetchone") and hasattr(tabular_data, "rowcount") ):
            # Python Database API cursor object (PEP 0249)
            # print tabulate(cursor, headers='keys')
            headers = [column[0] for column in tabular_data.description]

        elif headers == "keys" and len(rows) > 0:
            # keys are column indices
            headers = list(map(_text_type, range(len(rows[0]))))

    # take headers from the first row if necessary
    if headers == "firstrow" and len(rows) > 0:
        if index is not None:
            headers = [index[0]] + list(rows[0])
            index = index[1:]
        else:
            headers = rows[0]
        headers = list(map(_text_type, headers))  # headers should be strings
        rows = rows[1:]

    headers = list(map(_text_type, headers))
    rows = list(map(list, rows))

    # add or remove an index column
    showindex_is_a_str = type(showindex) in [_text_type, _binary_type]
    if showindex == "default" and index is not None:
        rows = _prepend_row_index(rows, index)
    elif hasattr(showindex, '__iter__') and not showindex_is_a_str:
        rows = _prepend_row_index(rows, list(showindex))
    elif showindex == "always" or (_bool(showindex) and not showindex_is_a_str):
        if index is None:
            index = list(range(len(rows)))
        rows = _prepend_row_index(rows, index)
    elif showindex == "never" or (not _bool(showindex) and not showindex_is_a_str):
        pass

    # pad with empty headers for initial columns if necessary
    if headers and len(rows) > 0:
        nhs = len(headers)
        ncols = len(rows[0])
        if nhs < ncols:
            headers = [""] * (ncols - nhs) + headers

    return rows, headers


def _wrap_text_to_colwidths(list_of_lists, colwidths, numparses=True):
    numparses = _expand_iterable(numparses, len(list_of_lists[0]), True)

    result = []

    for row in list_of_lists:
        new_row = []
        for cell, width, numparse in zip(row, colwidths, numparses):
            if _isnumber(cell) and numparse:
                new_row.append(cell)
                continue

            if width is not None:
                wrapped = cell
                new_row.append("\n".join(wrapped))
            else:
                new_row.append(cell)
        result.append(new_row)

    return result


def tabulate(
    tabular_data,
    headers=None,
    tablefmt=None,
    floatfmt=None,
    numalign=None,
    stralign=None,
    missingval=None,
    showindex=None,
    disable_numparse=None,
    colalign=None,
    maxcolwidths=None):
    """Format a fixed width table for pretty printing.

    >>> print(tabulate([[1, 2.34], [-56, "8.999"], ["2", "10001"]]))
    ---  ---------
      1      2.34
    -56      8.999
      2  10001
    ---  ---------

    The first required argument (`tabular_data`) can be a
    list-of-lists (or another iterable of iterables), a list of named
    tuples, a dictionary of iterables, an iterable of dictionaries,
    a two-dimensional NumPy array, NumPy record array, or a Pandas'
    dataframe.


    Table headers
    -------------

    To print nice column headers, supply the second argument (`headers`):

      - `headers` can be an explicit list of column headers
      - if `headers="firstrow"`, then the first row of data is used
      - if `headers="keys"`, then dictionary keys or column indices are used

    Otherwise a headerless table is produced.

    If the number of headers is less than the number of columns, they
    are supposed to be names of the last columns. This is consistent
    with the plain-text format of R and Pandas' dataframes.

    >>> print(tabulate([["sex","age"],["Alice","F",24],["Bob","M",19]],
    ...       headers="firstrow"))
           sex      age
    -----  -----  -----
    Alice  F         24
    Bob    M         19

    By default, pandas.DataFrame data have an additional column called
    row index. To add a similar column to all other types of data,
    use `showindex="always"` or `showindex=True`. To suppress row indices
    for all types of data, pass `showindex="never" or `showindex=False`.
    To add a custom row index column, pass `showindex=some_iterable`.

    >>> print(tabulate([["F",24],["M",19]], showindex="always"))
    -  -  --
    0  F  24
    1  M  19
    -  -  --


    Column alignment
    ----------------

    `tabulate` tries to detect column types automatically, and aligns
    the values properly. By default it aligns decimal points of the
    numbers (or flushes integer numbers to the right), and flushes
    everything else to the left. Possible column alignments
    (`numalign`, `stralign`) are: "right", "center", "left", "decimal"
    (only for `numalign`), and None (to disable alignment).


    Table formats
    -------------

    `floatfmt` is a format specification used for columns which
    contain numeric data with a decimal point. This can also be
    a list or tuple of format strings, one per column.

    `None` values are replaced with a `missingval` string (like
    `floatfmt`, this can also be a list of values for different
    columns):

    >>> print(tabulate([["spam", 1, None],
    ...                 ["eggs", 42, 3.14],
    ...                 ["other", None, 2.7]], missingval="?"))
    -----  --  ----
    spam    1  ?
    eggs   42  3.14
    other   ?  2.7
    -----  --  ----

    Various plain-text table formats (`tablefmt`) are supported:
    'plain', 'simple', 'grid', 'pipe', 'orgtbl', 'rst', 'mediawiki',
    'latex', 'latex_raw', 'latex_booktabs', 'latex_longtable' and tsv.
    Variable `tabulate_formats`contains the list of currently supported formats.

    "plain" format doesn't use any pseudographics to draw tables,
    it separates columns with a double space:

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]],
    ...                 ["strings", "numbers"], "plain"))
    strings      numbers
    spam         41.9999
    eggs        451

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]], tablefmt="plain"))
    spam   41.9999
    eggs  451

    "simple" format is like Pandoc simple_tables:

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]],
    ...                 ["strings", "numbers"], "simple"))
    strings      numbers
    ---------  ---------
    spam         41.9999
    eggs        451

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]], tablefmt="simple"))
    ----  --------
    spam   41.9999
    eggs  451
    ----  --------

    "grid" is similar to tables produced by Emacs table.el package or
    Pandoc grid_tables:

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]],
    ...                ["strings", "numbers"], "grid"))
    +-----------+-----------+
    | strings   |   numbers |
    +===========+===========+
    | spam      |   41.9999 |
    +-----------+-----------+
    | eggs      |  451      |
    +-----------+-----------+

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]], tablefmt="grid"))
    +------+----------+
    | spam |  41.9999 |
    +------+----------+
    | eggs | 451      |
    +------+----------+

    "fancy_grid" draws a grid using box-drawing characters:

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]],
    ...                ["strings", "numbers"], "fancy_grid"))
    ╒═══════════╤═══════════╕
    │ strings   │   numbers │
    ╞═══════════╪═══════════╡
    │ spam      │   41.9999 │
    ├───────────┼───────────┤
    │ eggs      │  451      │
    ╘═══════════╧═══════════╛

    "pipe" is like tables in PHP Markdown Extra extension or Pandoc
    pipe_tables:

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]],
    ...                ["strings", "numbers"], "pipe"))
    | strings   |   numbers |
    |:----------|----------:|
    | spam      |   41.9999 |
    | eggs      |  451      |

    "presto" is like tables produce by the Presto CLI:

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]],
    ...                ["strings", "numbers"], "presto"))
     strings   |   numbers
    -----------+-----------
     spam      |   41.9999
     eggs      |  451

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]], tablefmt="pipe"))
    |:-----|---------:|
    | spam |  41.9999 |
    | eggs | 451      |

    "orgtbl" is like tables in Emacs org-mode and orgtbl-mode. They
    are slightly different from "pipe" format by not using colons to
    define column alignment, and using a "+" sign to indicate line
    intersections:

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]],
    ...                ["strings", "numbers"], "orgtbl"))
    | strings   |   numbers |
    |-----------+-----------|
    | spam      |   41.9999 |
    | eggs      |  451      |


    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]], tablefmt="orgtbl"))
    | spam |  41.9999 |
    | eggs | 451      |

    "rst" is like a simple table format from reStructuredText; please
    note that reStructuredText accepts also "grid" tables:

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]],
    ...                ["strings", "numbers"], "rst"))
    =========  =========
    strings      numbers
    =========  =========
    spam         41.9999
    eggs        451
    =========  =========

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]], tablefmt="rst"))
    ====  ========
    spam   41.9999
    eggs  451
    ====  ========

    "mediawiki" produces a table markup used in Wikipedia and on other
    MediaWiki-based sites:

    >>> print(tabulate([["strings", "numbers"], ["spam", 41.9999], ["eggs", "451.0"]],
    ...                headers="firstrow", tablefmt="mediawiki"))
    {| class="wikitable" style="text-align: left;"
    |+ <!-- caption -->
    |-
    ! strings   !! align="right"|   numbers
    |-
    | spam      || align="right"|   41.9999
    |-
    | eggs      || align="right"|  451
    |}

    "html" produces HTML markup as an html.escape'd str
    with a ._repr_html_ method so that Jupyter Lab and Notebook display the HTML
    and a .str property so that the raw HTML remains accessible
    the unsafehtml table format can be used if an unescaped HTML format is required:

    >>> print(tabulate([["strings", "numbers"], ["spam", 41.9999], ["eggs", "451.0"]],
    ...                headers="firstrow", tablefmt="html"))
    <table>
    <thead>
    <tr><th>strings  </th><th style="text-align: right;">  numbers</th></tr>
    </thead>
    <tbody>
    <tr><td>spam     </td><td style="text-align: right;">  41.9999</td></tr>
    <tr><td>eggs     </td><td style="text-align: right;"> 451     </td></tr>
    </tbody>
    </table>

    "latex" produces a tabular environment of LaTeX document markup:

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]], tablefmt="latex"))
    \\begin{tabular}{lr}
    \\hline
     spam &  41.9999 \\\\
     eggs & 451      \\\\
    \\hline
    \\end{tabular}

    "latex_raw" is similar to "latex", but doesn't escape special characters,
    such as backslash and underscore, so LaTeX commands may embedded into
    cells' values:

    >>> print(tabulate([["spam$_9$", 41.9999], ["\\\\emph{eggs}", "451.0"]], tablefmt="latex_raw"))
    \\begin{tabular}{lr}
    \\hline
     spam$_9$    &  41.9999 \\\\
     \\emph{eggs} & 451      \\\\
    \\hline
    \\end{tabular}

    "latex_booktabs" produces a tabular environment of LaTeX document markup
    using the booktabs.sty package:

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]], tablefmt="latex_booktabs"))
    \\begin{tabular}{lr}
    \\toprule
     spam &  41.9999 \\\\
     eggs & 451      \\\\
    \\bottomrule
    \\end{tabular}

    "latex_longtable" produces a tabular environment that can stretch along
    multiple pages, using the longtable package for LaTeX.

    >>> print(tabulate([["spam", 41.9999], ["eggs", "451.0"]], tablefmt="latex_longtable"))
    \\begin{longtable}{lr}
    \\hline
     spam &  41.9999 \\\\
     eggs & 451      \\\\
    \\hline
    \\end{longtable}


    Number parsing
    --------------
    By default, anything which can be parsed as a number is a number.
    This ensures numbers represented as strings are aligned properly.
    This can lead to weird results for particular strings such as
    specific git SHAs e.g. "42992e1" will be parsed into the number
    429920 and aligned as such.

    To completely disable number parsing (and alignment), use
    `disable_numparse=True`. For more fine grained control, a list column
    indices is used to disable number parsing only on those columns
    e.g. `disable_numparse=[0, 2]` would disable number parsing only on the
    first and third columns.

    Column Widths and Auto Line Wrapping
    ------------------------------------
    Tabulate will, by default, set the width of each column to the length of the
    longest element in that column. However, in situations where fields are expected
    to reasonably be too long to look good as a single line, tabulate can help automate
    word wrapping long fields for you. Use the parameter `maxcolwidth` to provide a
    list of maximal column widths

    >>> print(tabulate( 
          [('1', 'John Smith', 
            'This is a rather long description that might look better if it is wrapped a bit')], 
          headers=("Issue Id", "Author", "Description"), 
          maxcolwidths=[None, None, 30], 
          tablefmt="grid"  
        ))
    +------------+------------+-------------------------------+
    |   Issue Id | Author     | Description                   |
    +============+============+===============================+
    |          1 | John Smith | This is a rather long         |
    |            |            | description that might look   |
    |            |            | better if it is wrapped a bit |
    +------------+------------+-------------------------------+


    """

    headers = headers or tuple()
    tablefmt = tablefmt or "simple"
    floatfmt = floatfmt or _DEFAULT_FLOATFMT
    numalign = numalign or _DEFAULT_ALIGN
    stralign = stralign or _DEFAULT_ALIGN
    missingval = missingval or _DEFAULT_MISSINGVAL
    showindex = showindex or "default"
    colalign = colalign or None
    maxcolwidths = maxcolwidths or None
    disable_numparse = disable_numparse or False
    
    
    if tabular_data is None:
        tabular_data = []
    list_of_lists, headers = _normalize_tabular_data(
        tabular_data, headers, showindex=showindex
    )
    

    if maxcolwidths is not None:
        num_cols = len(list_of_lists[0])
        if isinstance(maxcolwidths, int):  # Expand scalar for all columns
            maxcolwidths = _expand_iterable(maxcolwidths, num_cols, maxcolwidths)
        else:  # Ignore col width for any 'trailing' columns
            maxcolwidths = _expand_iterable(maxcolwidths, num_cols, None)

        numparses = _expand_numparse(disable_numparse, num_cols)
        list_of_lists = _wrap_text_to_colwidths(
            list_of_lists, maxcolwidths, numparses=numparses
        )

    # empty values in the first column of RST tables should be escaped (issue #82)
    # "" should be escaped as "\\ " or ".."
    if tablefmt == "rst":
        list_of_lists, headers = _rst_escape_first_column(list_of_lists, headers)

    # PrettyTable formatting does not use any extra padding.
    # Numbers are not parsed and are treated the same as strings for alignment.
    # Check if pretty is the format being used and override the defaults so it
    # does not impact other formats.
    min_padding = MIN_PADDING
    if tablefmt == "pretty":
        min_padding = 0
        disable_numparse = True
        numalign = "center" if numalign == _DEFAULT_ALIGN else numalign
        stralign = "center" if stralign == _DEFAULT_ALIGN else stralign
    else:
        numalign = "decimal" if numalign == _DEFAULT_ALIGN else numalign
        stralign = "left" if stralign == _DEFAULT_ALIGN else stralign

    # optimization: look for ANSI control codes once,
    # enable smart width functions only if a control code is found
    plain_text = "\t".join(["\t".join(map(_text_type, headers))] + ["\t".join(map(_text_type, row)) for row in list_of_lists])

    has_invisible = True
    enable_widechars = wcwidth is not None and WIDE_CHARS_MODE
    if (not isinstance(tablefmt, TableFormat) and tablefmt in multiline_formats and _is_multiline(plain_text)):
        tablefmt = multiline_formats.get(tablefmt, tablefmt)
        is_multiline = True
    else:
        is_multiline = False
    width_fn = _choose_width_fn(has_invisible, enable_widechars, is_multiline)

    # format rows and columns, convert numeric values to strings
    cols = list(izip_longest(*list_of_lists))
    numparses = _expand_numparse(disable_numparse, len(cols))
    coltypes = [_column_type(col, numparse=np) for col, np in zip(cols, numparses)]
    if isinstance(floatfmt, basestring):  # old version
        float_formats = len(cols) * [
            floatfmt
        ]  # just duplicate the string to use in each column
    else:  # if floatfmt is list, tuple etc we have one per column
        float_formats = list(floatfmt)
        if len(float_formats) < len(cols):
            float_formats.extend((len(cols) - len(float_formats)) * [_DEFAULT_FLOATFMT])
    if isinstance(missingval, basestring):
        missing_vals = len(cols) * [missingval]
    else:
        missing_vals = list(missingval)
        if len(missing_vals) < len(cols):
            missing_vals.extend((len(cols) - len(missing_vals)) * [_DEFAULT_MISSINGVAL])
            
    cols = [
        [_format(v, ct, fl_fmt, miss_v, has_invisible) for v in c]
        for c, ct, fl_fmt, miss_v in zip(cols, coltypes, float_formats, missing_vals)
    ]

    # align columns
    aligns = [numalign if ct in [int, float] else stralign for ct in coltypes]
    if colalign is not None:
        assert hasattr(colalign, '__iter__')
        for idx, align in enumerate(colalign):
            aligns[idx] = align
    orign_minwidths = (
        [width_fn(h) + min_padding for h in headers] if headers else [0] * len(cols)
    )
    print(orign_minwidths)
    cols = [
        _align_column(c, a, minw, has_invisible, enable_widechars, is_multiline)
        for c, a, minw in zip(cols, aligns, orign_minwidths)
    ]

    if headers:
        # align headers and add headers
        t_cols = cols or [[""]] * len(headers)
        t_aligns = aligns or [stralign] * len(headers)
        minwidths = []
        for minw, c in zip(orign_minwidths, t_cols):
            max_width = 0
            for cl in c:
                width = width_fn(cl)
                if width > max_width:
                    max_width = width
            minwidths.append(max(minw, max_width))
        headers = [_align_header(h, a, minw, width_fn(h), is_multiline, width_fn) for h, a, minw in zip(headers, t_aligns, minwidths)]
        rows = list(zip(*cols))
    else:
        minwidths = []
        for c in cols:
            max_width = 0
            for cl in c:
                width = width_fn(cl)
                if width > max_width:
                    max_width = width
            minwidths.append(max_width)
        rows = list(zip(*cols))

    if not isinstance(tablefmt, TableFormat):
        tablefmt = _table_formats.get(tablefmt, _table_formats["simple"])

    
    return _format_table(tablefmt, headers, rows, minwidths, aligns, is_multiline)


def _expand_numparse(disable_numparse, column_count):
    """
    Return a list of bools of length `column_count` which indicates whether
    number parsing should be used on each column.
    If `disable_numparse` is a list of indices, each of those indices are False,
    and everything else is True.
    If `disable_numparse` is a bool, then the returned list is all the same.
    """
    if  hasattr(disable_numparse, '__iter__'):
        numparses = [True] * column_count
        for index in disable_numparse:
            numparses[index] = False
        return numparses
    else:
        return [not disable_numparse] * column_count


def _expand_iterable(original, num_desired, default):
    """
    Expands the `original` argument to return a return a list of
    length `num_desired`. If `original` is shorter than `num_desired`, it will
    be padded with the value in `default`.
    If `original` is not a list to begin with (i.e. scalar value) a list of
    length `num_desired` completely populated with `default will be returned
    """
    if isinstance(original, Iterable):
        return original + [default] * (num_desired - len(original))
    else:
        return [default] * num_desired


def _pad_row(cells, padding):
    if cells:
        pad = " " * padding
        padded_cells = [pad + cell + pad for cell in cells]
        return padded_cells
    else:
        return cells


def _build_simple_row(padded_cells, rowfmt):
    "Format row according to DataRow format without padding."
    begin, sep, end = rowfmt
    return (begin + sep.join(padded_cells) + end).rstrip()


def _build_row(padded_cells, colwidths, colaligns, rowfmt):
    "Return a string which represents a row of data cells."
    if not rowfmt:
        return None
    if hasattr(rowfmt, "__call__"):
        return rowfmt(padded_cells, colwidths, colaligns)
    else:
        return _build_simple_row(padded_cells, rowfmt)


def _append_basic_row(lines, padded_cells, colwidths, colaligns, rowfmt):
    lines.append(_build_row(padded_cells, colwidths, colaligns, rowfmt))
    return lines


def _append_multiline_row(lines, padded_multiline_cells, padded_widths, colaligns, rowfmt, pad=None):
    colwidths = [w - 2 * pad for w in padded_widths]
    cells_lines = [c.splitlines() for c in padded_multiline_cells]
    nlines = max(map(len, cells_lines))  # number of lines in the row
    # vertically pad cells where some lines are missing
    cells_lines = [
        (cl + [" " * w] * (nlines - len(cl))) for cl, w in zip(cells_lines, colwidths)
    ]
    lines_cells = [[cl[i] for cl in cells_lines] for i in range(nlines)]
    for ln in lines_cells:
        padded_ln = _pad_row(ln, pad)
        _append_basic_row(lines, padded_ln, colwidths, colaligns, rowfmt)
    return lines


def _build_line(colwidths, colaligns, linefmt):
    "Return a string which represents a horizontal line."
    if not linefmt:
        return None
    if hasattr(linefmt, "__call__"):
        return linefmt(colwidths, colaligns)
    else:
        begin, fill, sep, end = linefmt
        cells = [fill * w for w in colwidths]
        return _build_simple_row(cells, (begin, sep, end))


def _append_line(lines, colwidths, colaligns, linefmt):
    lines.append(_build_line(colwidths, colaligns, linefmt))
    return lines




def _format_table(fmt, headers, rows, colwidths, colaligns, is_multiline):
    """Produce a plain-text representation of the table."""
    lines = []
    hidden = fmt.with_header_hide if (headers and fmt.with_header_hide) else []
    pad = fmt.padding
    headerrow = fmt.headerrow

    padded_widths = [(w + 2 * pad) for w in colwidths]
    if is_multiline:
        pad_row = lambda row, _: row  # noqa do it later, in _append_multiline_row
        append_row = partial(_append_multiline_row, pad=pad)
    else:
        pad_row = _pad_row
        append_row = _append_basic_row

    padded_headers = pad_row(headers, pad)
    padded_rows = [pad_row(row, pad) for row in rows]

    if fmt.lineabove and "lineabove" not in hidden:
        _append_line(lines, padded_widths, colaligns, fmt.lineabove)

    if padded_headers:
        append_row(lines, padded_headers, padded_widths, colaligns, headerrow)
        if fmt.linebelowheader and "linebelowheader" not in hidden:
            _append_line(lines, padded_widths, colaligns, fmt.linebelowheader)
    
    if padded_rows and fmt.linebetweenrows and "linebetweenrows" not in hidden:
        # initial rows with a line below
        for row in padded_rows[:-1]:
            append_row(lines, row, padded_widths, colaligns, fmt.datarow)
            _append_line(lines, padded_widths, colaligns, fmt.linebetweenrows)
        # the last row without a line below
        append_row(lines, padded_rows[-1], padded_widths, colaligns, fmt.datarow)
    else:
        for row in padded_rows:
            append_row(lines, row, padded_widths, colaligns, fmt.datarow)
    
    if fmt.linebelow and "linebelow" not in hidden:
        _append_line(lines, padded_widths, colaligns, fmt.linebelow)

    
    if headers or rows:
        output = "\n".join(lines)
        return output
    else:  # a completely empty table
        return ""
