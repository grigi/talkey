import langid

# Get the list of identifiable languages
DETECTABLE_LANGS = sorted([a[0] for a in langid.rank('')])


