# plcd

This is a python library for facilitating pre-loaded compression
dictionary usage.

## What are pre-loaded compression dictionaries?

Pre-loaded compression means that you “seed” a compressor with some
sample data, which is representative of future data you wish to encode.

They are primarily useful for encoding small pieces of data. For
example, if you see this JSON blob (from the Twitter search API
example),

    {"user":"Sean Cummings","text":"Aggressive Ponytail #freebandnames","retweet_count":0,"id":250075927172759550}

you’ll notice there are some structural elements,
`{"user":,"text":,"retweet_count":,"id”:}` which have low information
content, if you know you’re dealing with JSON tweet blobs. There might
be values which have lower informational content in the context of other
vaues, like that the retweet count is zero. If you had pre-loaded your
compressor with examples of other tweets, you may get better
compression.

(NOTE: If you know a better term, let me know; I’m using words from
[this Wikipedia article][]).

## Why write a library?

There are a few tasks one might like to do when using pre-loaded
compression dictionaries,

-   Use representative data to “seed” the compressor

-   Guard against failures: version the pre-loaded data, tag compressed
    data, etc.

-   Compare performance (size and encode/decode time) of different
    compression options

This library aims to help with all those, as well as create a simple
interface that’s hard to mis-use (e.g. hard to “forget” a step that ends
up messing up the compressor/decompressor state).

## How does it perform?

It really depends on your data. If your data is highly redundant, maybe
3x. Maybe less, maybe more. Instead of looking at results from different
datasets, try it on yours:

    pip install git+https://github.com/gatoatigrado/plcd
    plcd_generate --line-separated my_data.json

(That assumes you have newline-separated data; use
`plcd_generate --help` for more options.)

  [this Wikipedia article]: http://en.wikibooks.org/wiki/Data_Compression/Inference_Compression#pre-loaded_dictionary
