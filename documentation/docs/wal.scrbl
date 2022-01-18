#lang scribble/manual
@title{WAL: Waveform Analysis Language}
@author{Lucas Klemmer, Institute for Complex Systems ICS}

The @bold{W}aveform @bold{A}nalysis @bold{L}anguage (WAL) is a @italic{Domain Specific Language} (DSL) for analyzing
waveforms produced by hardware simulators. It gives developers the tools they need to naturally express hardware analyzis
problems.

@section{Introduction}
The core unit of WAL are expressions. An expression can be either literals, symbols, or lists.
Literals are data like @racket[1] or @racket["hello"]. Symbols are names that can refer to variables,
signals or functions. Some examples for signals are @racket[x], @racket[Top.module1.input], or @racket[print].


@section{WAL API}
This section contains the documentation for all WAL functions.

@subsection{Organization}
Organization function can be used to load and step through waveforms as well as introducing aliases for signals.

@defproc[(load [path string] [id symbol]) ()]{
    Loads the waveform in file @racket[path] and makes it available to WAL code usign the id id.
}

@defproc[(step [id symbol all] [amount integer 1]) ()]{
    Step trace @racket[id] by @racket[amount]. Both arguments are optional.
    If no @racket[id] is provided @italic{all} traces will be stepped by @racket[amount].
}

@defproc[(alias [name symbol] [signal symbol]) ()]{
    Introduces an alias for @racket[signal] such that it can be also referenced using @racket[name]. 
}

@defproc[(unalias [name symbol]) ()]{
    Removes the alias @racket[name].
}

@section{}

