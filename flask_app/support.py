
def capitalize_all(s):
    capitalized_words = [word.capitalize() for word in s.strip().split()]
    return " ".join(capitalized_words)

